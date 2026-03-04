from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from .core import idx, unidx


@dataclass(frozen=True)
class SymmetryMapping:
    name: str
    # Coordinate permutation as indices: (i,j,k) -> (coord[perm[0]], coord[perm[1]], coord[perm[2]])
    perm: tuple[int, int, int]

    @property
    def dir_map(self) -> tuple[int, int, int]:
        # Direction d bumps old coord d; after permutation it bumps the new axis where that old coord ends up.
        p = self.perm
        return (p.index(0), p.index(1), p.index(2))


def _iter_arc_bits(mask: int, *, n_vertices: int = 27) -> Iterable[tuple[int, int]]:
    for v in range(n_vertices):
        base = 3 * v
        for d in range(3):
            if mask & (1 << (base + d)):
                yield v, d


def _map_arc_mask_m3(mask: int, mapping: SymmetryMapping) -> int:
    m = 3
    dir_map = mapping.dir_map
    out = 0
    for v, d in _iter_arc_bits(mask, n_vertices=27):
        i, j, k = unidx(v, m)
        coords = (i, j, k)
        v2 = idx(coords[mapping.perm[0]], coords[mapping.perm[1]], coords[mapping.perm[2]], m)
        d2 = dir_map[d]
        out |= 1 << (3 * v2 + d2)
    return out


def _canon_decomp(triple: Sequence[int]) -> tuple[int, int, int]:
    a, b, c = sorted(triple)
    return (a, b, c)


def _map_decomp_m3(triple: Sequence[int], mapping: SymmetryMapping) -> tuple[int, int, int]:
    return _canon_decomp([_map_arc_mask_m3(x, mapping) for x in triple])


def _load_cycle_masks(path: Path) -> set[int]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    masks_hex = obj.get("cycle_masks_hex")
    if not isinstance(masks_hex, list):
        raise ValueError("generalizable_cycle_masks.json missing cycle_masks_hex list")
    out: set[int] = set()
    for s in masks_hex:
        if not isinstance(s, str):
            raise ValueError("cycle_masks_hex must contain strings")
        out.add(int(s, 16))
    return out


def _load_decompositions(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    triples = obj.get("triples_cycle_masks_hex_sorted")
    if not isinstance(triples, list):
        raise ValueError("decompositions.json missing triples_cycle_masks_hex_sorted list")
    parsed: list[tuple[int, int, int]] = []
    for t in triples:
        if not isinstance(t, list) or len(t) != 3:
            raise ValueError("each decomposition triple must be a 3-list")
        masks: list[int] = []
        for s in t:
            if not isinstance(s, str):
                raise ValueError("decomposition triples must contain hex strings")
            masks.append(int(s, 16))
        parsed.append(_canon_decomp(masks))
    return {
        "m": obj.get("m"),
        "n_total": obj.get("n_total"),
        "n_all_generalizable": obj.get("n_all_generalizable"),
        "definition": obj.get("definition"),
        "triples": parsed,
    }


def _hex_triple(t: tuple[int, int, int]) -> list[str]:
    return [hex(t[0]), hex(t[1]), hex(t[2])]


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Verify Knuth m=3 symmetry subclaims (e.g. 136 under ijk→jki).")
    p.add_argument(
        "--decompositions",
        type=Path,
        default=Path("artifacts/knuth_m3/decompositions.json"),
        help="path to decompositions.json (exact cover output)",
    )
    p.add_argument(
        "--generalizable-cycles",
        type=Path,
        default=Path("artifacts/knuth_m3/generalizable_cycle_masks.json"),
        help="path to generalizable_cycle_masks.json (996 cycles)",
    )
    p.add_argument(
        "--out",
        type=Path,
        default=Path("artifacts/knuth_m3/symmetry_counts.json"),
        help="output JSON path",
    )
    args = p.parse_args(argv)

    allowed = _load_cycle_masks(args.generalizable_cycles)
    dec = _load_decompositions(args.decompositions)

    triples: list[tuple[int, int, int]] = dec["triples"]
    s_all_generalizable: set[tuple[int, int, int]] = set()
    for t in triples:
        if t[0] in allowed and t[1] in allowed and t[2] in allowed:
            s_all_generalizable.add(t)

    # Coordinate mappings discussed in Knuth (p.4).
    mappings = [
        SymmetryMapping(name="ijk", perm=(0, 1, 2)),  # identity
        SymmetryMapping(name="jki", perm=(1, 2, 0)),
        SymmetryMapping(name="kij", perm=(2, 0, 1)),
    ]

    # Cycle-level check: among the 996 generalizable Hamiltonian cycles, how many stay generalizable
    # under coordinate rotation?
    cycles_images: dict[str, set[int]] = {}
    cycles_intersections: dict[str, set[int]] = {}
    for mp in mappings:
        ms = {_map_arc_mask_m3(mask, mp) for mask in allowed}
        cycles_images[mp.name] = ms
        cycles_intersections[mp.name] = allowed & ms
    cycles_common_all = cycles_intersections["ijk"] & cycles_intersections["jki"] & cycles_intersections["kij"]

    # Decomposition-level check: among the 760 decompositions using only generalizable cycles, how many
    # map to another such decomposition under coordinate rotation?
    decomp_images: dict[str, set[tuple[int, int, int]]] = {}
    decomp_intersections: dict[str, set[tuple[int, int, int]]] = {}
    decomp_fixed_points: dict[str, int] = {}
    for mp in mappings:
        ms = {_map_decomp_m3(t, mp) for t in s_all_generalizable}
        decomp_images[mp.name] = ms
        decomp_intersections[mp.name] = s_all_generalizable & ms
        decomp_fixed_points[mp.name] = sum(
            1 for t in s_all_generalizable if _map_decomp_m3(t, mp) == t
        )
    decomp_common_all = (
        decomp_intersections["ijk"] & decomp_intersections["jki"] & decomp_intersections["kij"]
    )

    out_obj: dict[str, Any] = {
        "m": 3,
        "inputs": {
            "decompositions": str(args.decompositions),
            "generalizable_cycles": str(args.generalizable_cycles),
        },
        "cycle_level": {
            "n_generalizable_cycles": len(allowed),
            "mappings": {
                mp.name: (
                    {
                        "perm": list(mp.perm),
                        "dir_map": list(mp.dir_map),
                        "n_intersection_with_generalizable_set": len(cycles_intersections[mp.name]),
                    }
                    | (
                        {
                            "intersection_cycle_masks_hex": sorted(
                                hex(x) for x in cycles_intersections[mp.name]
                            )
                        }
                        if mp.name != "ijk"
                        else {}
                    )
                )
                for mp in mappings
            },
            "n_common_all_three_mappings": len(cycles_common_all),
            "common_all_three_cycle_masks_hex": sorted(hex(x) for x in cycles_common_all),
        },
        "decomposition_level": {
            "n_decompositions_total_declared": dec.get("n_total"),
            "n_decompositions_all_generalizable_declared": dec.get("n_all_generalizable"),
            "n_decompositions_all_generalizable_computed": len(s_all_generalizable),
            "mappings": {
                mp.name: (
                    {
                        "perm": list(mp.perm),
                        "dir_map": list(mp.dir_map),
                        "n_intersection_with_generalizable_set": len(decomp_intersections[mp.name]),
                        "n_fixed_points": decomp_fixed_points[mp.name],
                    }
                    | (
                        {
                            "intersection_triples_hex": sorted(
                                (_hex_triple(t) for t in decomp_intersections[mp.name]),
                                key=lambda xs: (xs[0], xs[1], xs[2]),
                            )
                        }
                        if mp.name != "ijk"
                        else {}
                    )
                )
                for mp in mappings
            },
            "n_common_all_three_mappings": len(decomp_common_all),
            "common_all_three_triples_hex": sorted(
                (_hex_triple(t) for t in decomp_common_all),
                key=lambda xs: (xs[0], xs[1], xs[2]),
            ),
        },
        "notes": [
            "Knuth (p.4) states a '136' subclaim under ijk→jki but appears to conflate the 996 generalizable cycles and the 760 generalizable decompositions.",
            "This script reports both cycle-level and decomposition-level counts so the interpretation is explicit.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out_obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "cycle_level_jki": len(cycles_intersections["jki"]),
                "cycle_level_kij": len(cycles_intersections["kij"]),
                "cycle_level_common_all": len(cycles_common_all),
                "decomp_level_jki": len(decomp_intersections["jki"]),
                "decomp_level_kij": len(decomp_intersections["kij"]),
                "decomp_level_common_all": len(decomp_common_all),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
