from __future__ import annotations

from typing import Iterator, Tuple

Vertex = Tuple[int, int, int]


def n_vertices(m: int) -> int:
    return m * m * m


def index_of(v: Vertex, m: int) -> int:
    i, j, k = v
    return i * m * m + j * m + k


def vertex_of(idx: int, m: int) -> Vertex:
    m2 = m * m
    i = idx // m2
    rem = idx - i * m2
    j = rem // m
    k = rem - j * m
    return i, j, k


def vertices(m: int) -> Iterator[Vertex]:
    for i in range(m):
        for j in range(m):
            for k in range(m):
                yield i, j, k


def succ_index(idx: int, d: int, m: int) -> int:
    if d not in (0, 1, 2):
        raise ValueError(f"direction must be in {{0,1,2}}; got {d}")

    m2 = m * m
    i = idx // m2
    rem = idx - i * m2
    j = rem // m
    k = rem - j * m

    if d == 0:
        if i + 1 < m:
            return idx + m2
        return idx - (m - 1) * m2

    if d == 1:
        if j + 1 < m:
            return idx + m
        return idx - (m - 1) * m

    if k + 1 < m:
        return idx + 1
    return idx - (m - 1)


def pred_index(idx: int, d: int, m: int) -> int:
    if d not in (0, 1, 2):
        raise ValueError(f"direction must be in {{0,1,2}}; got {d}")

    m2 = m * m
    i = idx // m2
    rem = idx - i * m2
    j = rem // m
    k = rem - j * m

    if d == 0:
        if i > 0:
            return idx - m2
        return idx + (m - 1) * m2

    if d == 1:
        if j > 0:
            return idx - m
        return idx + (m - 1) * m

    if k > 0:
        return idx - 1
    return idx + (m - 1)

