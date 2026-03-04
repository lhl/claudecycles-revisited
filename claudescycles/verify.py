from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

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


def _check_arc_partition(dirs: Sequence[bytearray]) -> Tuple[bool, int]:
    """Check arc-disjointness + full arc coverage via per-tail direction partition.

    Since every arc is uniquely identified by (tail_vertex, direction), requiring that
    at each tail vertex the three cycles choose directions {0,1,2} implies:
      - arc-disjointness across cycles
      - union covers all arcs of G_m
    """

    n = len(dirs[0])
    violations = 0
    for idx in range(n):
        mask = (1 << dirs[0][idx]) | (1 << dirs[1][idx]) | (1 << dirs[2][idx])
        if mask != 0b111:
            violations += 1
    return (violations == 0, violations)


def _check_hamilton_cycle(m: int, cycle_index: int, d: bytearray) -> CycleCheck:
    n = n_vertices(m)
    if len(d) != n:
        return CycleCheck(
            ok=False,
            cycle_index=cycle_index,
            error=f"cycle dirs length {len(d)} != m^3={n}",
        )

    visited = bytearray(n)
    cur = 0
    for step in range(n):
        if visited[cur]:
            return CycleCheck(
                ok=False,
                cycle_index=cycle_index,
                error=f"revisited vertex idx={cur} at step={step} (cycle not Hamiltonian)",
            )
        visited[cur] = 1
        cur = succ_index(cur, int(d[cur]), m)

    if cur != 0:
        return CycleCheck(
            ok=False,
            cycle_index=cycle_index,
            error=f"after m^3 steps, did not return to start (ended at idx={cur})",
        )

    return CycleCheck(ok=True, cycle_index=cycle_index)


def verify_decomposition(m: int, dirs: Sequence[bytearray]) -> DecompositionCheck:
    if not isinstance(m, int):
        raise TypeError("m must be int")
    if m <= 2:
        return DecompositionCheck(
            ok=False,
            m=m,
            n_vertices=n_vertices(m),
            cycle_checks=[],
            arc_partition_ok=False,
            arc_partition_violations=0,
            error="m must be > 2",
        )
    if len(dirs) != 3:
        raise ValueError("expected exactly 3 cycles (dirs length must be 3)")

    n = n_vertices(m)
    for c in range(3):
        if len(dirs[c]) != n:
            return DecompositionCheck(
                ok=False,
                m=m,
                n_vertices=n,
                cycle_checks=[],
                arc_partition_ok=False,
                arc_partition_violations=0,
                error=f"cycle {c}: dirs length {len(dirs[c])} != m^3={n}",
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

    return DecompositionCheck(
        ok=ok,
        m=m,
        n_vertices=n,
        cycle_checks=cycle_checks,
        arc_partition_ok=arc_ok,
        arc_partition_violations=arc_viol,
        error=err,
    )

