from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from . import gm


@dataclass(frozen=True)
class CycleCheck:
    ok: bool
    cycle_index: int
    error: str | None = None


@dataclass(frozen=True)
class DecompositionCheck:
    ok: bool
    m: int
    n_vertices: int
    cycle_checks: list[CycleCheck]
    arc_partition_ok: bool
    arc_partition_violations: int
    error: str | None = None


def _check_arc_partition(dirs: Sequence[Sequence[int]]) -> tuple[bool, int]:
    if len(dirs) != 3:
        raise ValueError(f"expected 3 cycles, got {len(dirs)}")
    n = len(dirs[0])
    violations = 0
    for idx in range(n):
        counts = [0, 0, 0]
        for cycle_dirs in dirs:
            d = int(cycle_dirs[idx])
            if d not in (0, 1, 2):
                return False, n
            counts[d] += 1
        if counts != [1, 1, 1]:
            violations += 1
    return violations == 0, violations


def _check_hamilton_cycle(m: int, cycle_index: int, d: Sequence[int]) -> CycleCheck:
    n = gm.n_vertices(m)
    if len(d) != n:
        return CycleCheck(
            ok=False,
            cycle_index=cycle_index,
            error=f"dirs length {len(d)} != m^3={n}",
        )

    seen = [-1] * n
    cur = 0
    for step in range(n):
        if seen[cur] != -1:
            return CycleCheck(
                ok=False,
                cycle_index=cycle_index,
                error=f"revisited vertex index {cur} at step {step}",
            )
        direction = int(d[cur])
        if direction not in (0, 1, 2):
            return CycleCheck(
                ok=False,
                cycle_index=cycle_index,
                error=f"invalid direction {direction} at vertex index {cur}",
            )
        seen[cur] = step
        cur = gm.succ_index(cur, direction, m)

    if cur != 0:
        return CycleCheck(
            ok=False,
            cycle_index=cycle_index,
            error=f"did not return to start after {n} steps; ended at vertex index {cur}",
        )

    if any(step == -1 for step in seen):
        missing = seen.index(-1)
        return CycleCheck(
            ok=False,
            cycle_index=cycle_index,
            error=f"missed vertex index {missing}",
        )

    return CycleCheck(ok=True, cycle_index=cycle_index)


def verify_decomposition(m: int, dirs: Sequence[Sequence[int]]) -> DecompositionCheck:
    n = gm.n_vertices(m)
    if len(dirs) != 3:
        return DecompositionCheck(
            ok=False,
            m=m,
            n_vertices=n,
            cycle_checks=[],
            arc_partition_ok=False,
            arc_partition_violations=n,
            error=f"expected exactly 3 cycles, got {len(dirs)}",
        )

    for cycle_index, cycle_dirs in enumerate(dirs):
        if len(cycle_dirs) != n:
            return DecompositionCheck(
                ok=False,
                m=m,
                n_vertices=n,
                cycle_checks=[],
                arc_partition_ok=False,
                arc_partition_violations=0,
                error=f"cycle {cycle_index}: dirs length {len(cycle_dirs)} != m^3={n}",
            )

    arc_ok, arc_violations = _check_arc_partition(dirs)
    cycle_checks = [_check_hamilton_cycle(m, cycle_index, dirs[cycle_index]) for cycle_index in range(3)]
    cycles_ok = all(check.ok for check in cycle_checks)
    ok = arc_ok and cycles_ok

    error = None
    if not ok:
        if not arc_ok:
            error = f"arc partition violated at {arc_violations}/{n} vertices"
        else:
            for check in cycle_checks:
                if not check.ok:
                    error = f"cycle {check.cycle_index} failed: {check.error}"
                    break

    return DecompositionCheck(
        ok=ok,
        m=m,
        n_vertices=n,
        cycle_checks=cycle_checks,
        arc_partition_ok=arc_ok,
        arc_partition_violations=arc_violations,
        error=error,
    )

