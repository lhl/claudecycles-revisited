from __future__ import annotations

from functools import lru_cache
from typing import Sequence, cast

from .core import Dir, n_vertices, succ_idx, unidx


def _hat_m_to_3(x: int, m: int) -> int:
    if x == 0:
        return 0
    if x == m - 1:
        return 2
    return 1


@lru_cache(maxsize=None)
def map_vertices_to_m3(m: int) -> tuple[int, ...]:
    """
    Map each vertex index of G_m to a vertex index of G_3 using Knuth's "generalizable" rule.

    The paper defines (for odd m >= 3) a lifting from a Hamiltonian cycle on m=3 to one on m by
    reducing (I,J,S) to (i,j,s) in {0,1,2} via x^ in {0,1,2} and then setting k so i+j+k = s (mod 3).

    This function returns the mapping v_m -> v_3, as indices (0..m^3-1) -> (0..26).
    """
    if m <= 2:
        raise ValueError(f"m must be > 2, got {m}")
    n = n_vertices(m)
    hat = [_hat_m_to_3(x, m) for x in range(m)]

    out: list[int] = [0] * n
    for v in range(n):
        I, J, K = unidx(v, m)
        i = hat[I]
        j = hat[J]
        S = (I + J + K) % m
        s = hat[S]
        k = (s - i - j) % 3
        out[v] = (i * 3 + j) * 3 + k
    return tuple(out)


@lru_cache(maxsize=None)
def _succ_table(m: int) -> tuple[tuple[int, int, int], ...]:
    n = n_vertices(m)
    succ: list[tuple[int, int, int]] = []
    for v in range(n):
        succ.append(
            (
                succ_idx(v, cast(Dir, 0), m),
                succ_idx(v, cast(Dir, 1), m),
                succ_idx(v, cast(Dir, 2), m),
            )
        )
    return tuple(succ)


def generalizes_m3_cycle_to_m(*, base_dirs: Sequence[Dir], m: int, start_v: int = 0) -> bool:
    """
    Return True iff the Knuth "generalizable" lifting of a G_3 Hamiltonian cycle is Hamiltonian in G_m.

    base_dirs must be length 27 and define a functional digraph on G_3.
    """
    if m <= 2:
        raise ValueError(f"m must be > 2, got {m}")
    if len(base_dirs) != 27:
        raise ValueError(f"base_dirs must have length 27, got {len(base_dirs)}")

    n = n_vertices(m)
    if not (0 <= start_v < n):
        raise ValueError(f"start_v must be in [0,{n}), got {start_v}")

    to3 = map_vertices_to_m3(m)
    succ = _succ_table(m)

    visited = bytearray(n)
    cur = start_v
    for _ in range(n):
        if visited[cur]:
            return False
        visited[cur] = 1
        d = base_dirs[to3[cur]]
        cur = succ[cur][int(d)]
    return cur == start_v

