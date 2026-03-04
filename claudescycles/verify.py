from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence, cast

from .core import Decomposition, Dir, n_vertices, succ_idx


@dataclass(frozen=True)
class VerifyResult:
    ok: bool
    m: int
    n_vertices: int
    errors: list[str]


def _parse_dir_list(raw: Any, *, cycle: int, n: int) -> list[Dir]:
    if not isinstance(raw, list):
        raise ValueError(f"cycle {cycle} dirs must be a JSON list")
    if len(raw) != n:
        raise ValueError(f"cycle {cycle} dirs length must be {n}, got {len(raw)}")
    out: list[Dir] = []
    for idx, v in enumerate(raw):
        if v not in (0, 1, 2):
            raise ValueError(f"cycle {cycle} dirs[{idx}] must be 0/1/2, got {v!r}")
        out.append(cast(Dir, v))
    return out


def load_decomposition_json(path: Path) -> Decomposition:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError("decomposition JSON must be an object")
    if "m" not in obj:
        raise ValueError("decomposition JSON missing required key: m")
    m = obj["m"]
    if not isinstance(m, int):
        raise ValueError("decomposition JSON key m must be an int")
    n = n_vertices(m)

    cycles = obj.get("cycles")
    if not isinstance(cycles, list) or len(cycles) != 3:
        raise ValueError("decomposition JSON key cycles must be a list of length 3")
    cycle_dirs: list[list[Dir]] = []
    for t, c in enumerate(cycles):
        if isinstance(c, dict) and "dirs" in c:
            cycle_dirs.append(_parse_dir_list(c["dirs"], cycle=t, n=n))
        elif isinstance(c, list):
            cycle_dirs.append(_parse_dir_list(c, cycle=t, n=n))
        else:
            raise ValueError(
                "each cycles[t] must be either a dirs list or an object {\"dirs\": [...]}"
            )

    return Decomposition(m=m, cycle_dirs=(cycle_dirs[0], cycle_dirs[1], cycle_dirs[2]))


def verify_decomposition(decomp: Decomposition) -> VerifyResult:
    errors: list[str] = []

    m = decomp.m
    n = decomp.n
    c0, c1, c2 = decomp.cycle_dirs

    bad_vertices = 0
    for v in range(n):
        dirs = (c0[v], c1[v], c2[v])
        if dirs[0] == dirs[1] or dirs[0] == dirs[2] or dirs[1] == dirs[2]:
            bad_vertices += 1
            continue
        if set(dirs) != {0, 1, 2}:
            bad_vertices += 1
            continue
    if bad_vertices:
        errors.append(
            f"arc-disjoint/coverage failure: {bad_vertices} vertices do not use a permutation of directions {{0,1,2}}"
        )

    def check_cycle(cycle_dirs: Sequence[Dir], *, cycle: int) -> None:
        visited = bytearray(n)
        cur = 0
        for step in range(n):
            if visited[cur]:
                errors.append(
                    f"cycle {cycle} is not Hamiltonian: repeats vertex {cur} at step {step}"
                )
                return
            visited[cur] = 1
            cur = succ_idx(cur, cycle_dirs[cur], m)
        if cur != 0:
            errors.append(
                f"cycle {cycle} is not Hamiltonian: after {n} steps ends at {cur} instead of returning to 0"
            )

    check_cycle(c0, cycle=0)
    check_cycle(c1, cycle=1)
    check_cycle(c2, cycle=2)

    return VerifyResult(ok=(not errors), m=m, n_vertices=n, errors=errors)


def _cli(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Verify a decomposition of G_m into 3 arc-disjoint Hamiltonian directed cycles."
    )
    p.add_argument("--input", type=Path, required=True, help="decomposition JSON file")
    p.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="optional machine-readable output path",
    )
    args = p.parse_args(argv)

    decomp = load_decomposition_json(args.input)
    result = verify_decomposition(decomp)

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")

    if result.ok:
        print(f"OK: m={result.m} (n={result.n_vertices})")
        return 0

    print(f"FAIL: m={result.m} (n={result.n_vertices})")
    for e in result.errors:
        print(f"- {e}")
    return 2


if __name__ == "__main__":
    raise SystemExit(_cli())

