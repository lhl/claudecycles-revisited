from __future__ import annotations

from typing import cast

from .core import Decomposition, Dir, n_vertices, unidx


def claude_vertex_perm(i: int, j: int, k: int, m: int) -> tuple[Dir, Dir, Dir]:
    """
    Per-vertex permutation used in Knuth's note ("Claude's Cycles") for odd m.

    Returns a triple (d0, d1, d2) where cycle c takes direction dc at vertex (i,j,k).

    Directions:
      0 -> bump i
      1 -> bump j
      2 -> bump k
    """
    s = (i + j + k) % m
    if s == 0:
        d = "012" if (j == m - 1) else "210"
    elif s == m - 1:
        d = "120" if (i > 0) else "210"
    else:
        d = "201" if (i == m - 1) else "102"
    return (cast(Dir, int(d[0])), cast(Dir, int(d[1])), cast(Dir, int(d[2])))


def claude_decomposition(m: int) -> Decomposition:
    n = n_vertices(m)
    c0: list[Dir] = [0] * n
    c1: list[Dir] = [0] * n
    c2: list[Dir] = [0] * n
    for v in range(n):
        i, j, k = unidx(v, m)
        d0, d1, d2 = claude_vertex_perm(i, j, k, m)
        c0[v] = d0
        c1[v] = d1
        c2[v] = d2
    return Decomposition(m=m, cycle_dirs=(c0, c1, c2))

