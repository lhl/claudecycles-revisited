from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

from .generalize import generalizes_m3_cycle_to_m
from .m3_cycles import HamiltonianCycle, list_hamiltonian_cycles_m3
from .m3_decompositions import (
    DecompositionTriple,
    count_m3_decompositions_in_subset,
    list_m3_decompositions_from_arc_masks,
)


def _hex(mask: int) -> str:
    return hex(mask)


@dataclass(frozen=True)
class KnuthM3Counts:
    m: int
    n_hamiltonian_cycles: int
    n_generalize_to_m5: int
    n_generalize_to_m5_and_m7: int
    n_decompositions_total: int
    n_decompositions_all_generalizable: int
    elapsed_sec_total: float
    elapsed_sec_exact_cover: float


def _generalizable_indices(cycles: Sequence[HamiltonianCycle]) -> set[int]:
    allowed: set[int] = set()
    for idx, cyc in enumerate(cycles):
        if generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=5) and generalizes_m3_cycle_to_m(
            base_dirs=cyc.dirs, m=7
        ):
            allowed.add(idx)
    return allowed


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _decomp_masks(
    decomps: Sequence[DecompositionTriple], arc_masks: Sequence[int]
) -> list[list[str]]:
    out: list[list[str]] = []
    for d in decomps:
        triple = sorted((arc_masks[d.a], arc_masks[d.b], arc_masks[d.c]))
        out.append([_hex(triple[0]), _hex(triple[1]), _hex(triple[2])])
    out.sort()
    return out


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Reproduce the m=3 counting/exact-cover results from Knuth's 'Claude’s Cycles'."
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="output directory under artifacts/ (e.g. artifacts/knuth_m3)",
    )
    args = p.parse_args(argv)

    if args.out_dir.name in ("", ".", ".."):
        raise SystemExit("out-dir must be a real directory path")

    t0 = time.perf_counter()
    cycles = list_hamiltonian_cycles_m3()
    arc_masks = [c.arc_mask for c in cycles]

    n5 = 0
    n5n7 = 0
    for cyc in cycles:
        ok5 = generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=5)
        if ok5:
            n5 += 1
            if generalizes_m3_cycle_to_m(base_dirs=cyc.dirs, m=7):
                n5n7 += 1

    allowed = _generalizable_indices(cycles)

    t_cover0 = time.perf_counter()
    decomps = list_m3_decompositions_from_arc_masks(arc_masks)
    t_cover1 = time.perf_counter()

    n_all_gen = count_m3_decompositions_in_subset(decomps, allowed=allowed)
    t1 = time.perf_counter()

    counts = KnuthM3Counts(
        m=3,
        n_hamiltonian_cycles=len(cycles),
        n_generalize_to_m5=n5,
        n_generalize_to_m5_and_m7=n5n7,
        n_decompositions_total=len(decomps),
        n_decompositions_all_generalizable=n_all_gen,
        elapsed_sec_total=t1 - t0,
        elapsed_sec_exact_cover=t_cover1 - t_cover0,
    )

    _write_json(args.out_dir / "counts.json", asdict(counts))

    _write_json(
        args.out_dir / "generalizable_cycle_masks.json",
        {
            "m": 3,
            "definition": "cycles that generalize to Hamiltonian cycles for both m=5 and m=7 (Knuth 2026, p.4)",
            "n": len(allowed),
            "cycle_masks_hex": sorted(_hex(arc_masks[i]) for i in allowed),
        },
    )

    _write_json(
        args.out_dir / "decompositions.json",
        {
            "m": 3,
            "definition": "unordered exact covers of the 81 arcs by 3 Hamiltonian cycles",
            "n_total": len(decomps),
            "n_all_generalizable": n_all_gen,
            "triples_cycle_masks_hex_sorted": _decomp_masks(decomps, arc_masks),
        },
    )

    print("OK")
    print(json.dumps(asdict(counts), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())

