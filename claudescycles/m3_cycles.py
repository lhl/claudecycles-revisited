from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, cast

from .core import Dir, succ_idx


@dataclass(frozen=True)
class HamiltonianCycle:
    """
    A directed Hamiltonian cycle in G_3, represented by its per-vertex outgoing direction.

    dirs[v] in {0,1,2} is the coordinate bumped when leaving vertex v.
    """

    dirs: tuple[Dir, ...]  # length 27
    arc_mask: int  # 81-bit mask over arcs (v,dir) with bit index = 3*v + dir


def _arc_mask_from_dirs(dirs: Iterable[Dir]) -> int:
    mask = 0
    for v, d in enumerate(dirs):
        mask |= 1 << (3 * v + int(d))
    return mask


def iter_hamiltonian_cycles_m3(*, start_v: int = 0) -> Iterator[HamiltonianCycle]:
    """
    Enumerate all directed Hamiltonian cycles in G_3, rooted at start_v.

    Rooting at start_v ensures each cycle is counted exactly once (every Hamiltonian cycle contains every vertex).
    """

    m = 3
    n = 27
    if not (0 <= start_v < n):
        raise ValueError(f"start_v must be in [0,{n}), got {start_v}")

    succ: list[list[int]] = [[0, 0, 0] for _ in range(n)]
    for v in range(n):
        succ[v][0] = succ_idx(v, cast(Dir, 0), m)
        succ[v][1] = succ_idx(v, cast(Dir, 1), m)
        succ[v][2] = succ_idx(v, cast(Dir, 2), m)

    dirs_out: list[int] = [-1] * n

    def dfs(cur: int, visited_mask: int, depth: int) -> Iterator[HamiltonianCycle]:
        if depth == n - 1:
            for d in (0, 1, 2):
                nxt = succ[cur][d]
                if nxt == start_v:
                    dirs_out[cur] = d
                    dirs: tuple[Dir, ...] = tuple(cast(Dir, x) for x in dirs_out)
                    yield HamiltonianCycle(dirs=dirs, arc_mask=_arc_mask_from_dirs(dirs))
            dirs_out[cur] = -1
            return

        for d in (0, 1, 2):
            nxt = succ[cur][d]
            bit = 1 << nxt
            if visited_mask & bit:
                continue
            dirs_out[cur] = d
            yield from dfs(nxt, visited_mask | bit, depth + 1)
            dirs_out[cur] = -1

    dirs_out[start_v] = 0  # overwritten before first yield
    yield from dfs(start_v, 1 << start_v, 0)


def list_hamiltonian_cycles_m3(*, start_v: int = 0) -> list[HamiltonianCycle]:
    return list(iter_hamiltonian_cycles_m3(start_v=start_v))

