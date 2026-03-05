from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from .gm import n_vertices, succ_index


@dataclass(frozen=True)
class CycleCheck:
    ok: bool
    cycle_index: int
    error: Optional[str] = None


@dataclass(frozen=True)
class DecompositionCheck:
    ok: bool
    m: int
    n_vertices: int
    cycle_checks: List[CycleCheck]
    arc_partition_ok: bool
    arc_partition_violations: int
    error: Optional[str] = None


def _check_arc_partition(dirs: Sequence[Sequence[int]]) -> tuple[bool, int]:
    n = len(dirs[0])
    violations = 0
    for idx in range(n):
        mask = (1 << dirs[0][idx]) | (1 << dirs[1][idx]) | (1 << dirs[2][idx])
        if mask != 0b111:
            violations += 1
    return violations == 0, violations


def _check_hamilton_cycle(m: int, cycle_index: int, d: Sequence[int]) -> CycleCheck:
    n = n_vertices(m)
    if len(d) != n:
        return CycleCheck(
            False,
            cycle_index,
            f"cycle dirs length {len(d)} != m^3={n}",
        )

    visited = bytearray(n)
    cur = 0
    for step in range(n):
        if visited[cur]:
            return CycleCheck(
                False,
                cycle_index,
                f"revisited vertex idx={cur} at step={step} (cycle not Hamiltonian)",
            )
        visited[cur] = 1
        cur = succ_index(cur, int(d[cur]), m)

    if cur != 0:
        return CycleCheck(
            False,
            cycle_index,
            f"after m^3 steps, did not return to start (ended at idx={cur})",
        )

    return CycleCheck(True, cycle_index)


def verify_decomposition(m: int, dirs: Sequence[Sequence[int]]) -> DecompositionCheck:
    if not isinstance(m, int):
        raise TypeError("m must be int")

    if m <= 2:
        return DecompositionCheck(
            False,
            m,
            n_vertices(m),
            [],
            False,
            0,
            "m must be > 2",
        )

    if len(dirs) != 3:
        raise ValueError("expected exactly 3 cycles (dirs length must be 3)")

    n = n_vertices(m)
    for c in range(3):
        if len(dirs[c]) != n:
            return DecompositionCheck(
                False,
                m,
                n,
                [],
                False,
                0,
                f"cycle {c}: dirs length {len(dirs[c])} != m^3={n}",
            )

    arc_ok, arc_viol = _check_arc_partition(dirs)
    cycle_checks = [_check_hamilton_cycle(m, c, dirs[c]) for c in range(3)]
    cycles_ok = all(cc.ok for cc in cycle_checks)
    ok = arc_ok and cycles_ok

    err = None
    if not ok:
        if not arc_ok:
            err = f"arc partition violated at {arc_viol}/{n} vertices"
        else:
            for cc in cycle_checks:
                if not cc.ok:
                    err = f"cycle {cc.cycle_index} failed: {cc.error}"
                    break

    return DecompositionCheck(ok, m, n, cycle_checks, arc_ok, arc_viol, err)

