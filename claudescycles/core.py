from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Literal, Sequence

Dir = Literal[0, 1, 2]  # 0: +i, 1: +j, 2: +k


def n_vertices(m: int) -> int:
    return m * m * m


def idx(i: int, j: int, k: int, m: int) -> int:
    return (i * m + j) * m + k


def unidx(v: int, m: int) -> tuple[int, int, int]:
    mm = m * m
    i, r = divmod(v, mm)
    j, k = divmod(r, m)
    return i, j, k


def succ_idx(v: int, direction: Dir, m: int) -> int:
    mm = m * m
    if direction == 0:
        i, r = divmod(v, mm)
        if i + 1 < m:
            return v + mm
        return r  # wrap to i=0
    if direction == 1:
        i, r = divmod(v, mm)
        j, k = divmod(r, m)
        if j + 1 < m:
            return v + m
        return i * mm + k  # wrap to j=0
    # direction == 2
    if (v + 1) % m:
        return v + 1
    return v - (m - 1)  # wrap to k=0


@dataclass(frozen=True)
class Decomposition:
    m: int
    cycle_dirs: tuple[Sequence[Dir], Sequence[Dir], Sequence[Dir]]

    def __post_init__(self) -> None:
        if self.m <= 2:
            raise ValueError(f"m must be > 2, got {self.m}")
        expected = n_vertices(self.m)
        for t, dirs in enumerate(self.cycle_dirs):
            if len(dirs) != expected:
                raise ValueError(
                    f"cycle {t} dirs length must be {expected}, got {len(dirs)}"
                )

    @property
    def n(self) -> int:
        return n_vertices(self.m)


def iter_vertices(m: int) -> Iterator[tuple[int, int, int]]:
    for i in range(m):
        for j in range(m):
            for k in range(m):
                yield i, j, k


def iter_vertex_indices(m: int) -> Iterator[int]:
    return iter(range(n_vertices(m)))

