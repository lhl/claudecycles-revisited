from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator
from typing import cast

from .core import Decomposition, Dir, n_vertices, unidx


@dataclass(frozen=True)
class CyclicShiftLinearMod3:
    """
    Construction family:

      g(i,j,k) = (a*i + b*j + c*k + offset) mod 3
      cycle t uses direction (g + t) mod 3

    This automatically enforces arc-disjointness + full arc coverage (each vertex uses
    directions {0,1,2} across the 3 cycles). Hamiltonicity must be verified.
    """

    a: int
    b: int
    c: int
    offset: int

    def dirs(self, m: int) -> tuple[list[Dir], list[Dir], list[Dir]]:
        n = n_vertices(m)
        c0: list[Dir] = [0] * n
        c1: list[Dir] = [0] * n
        c2: list[Dir] = [0] * n
        for v in range(n):
            i, j, k = unidx(v, m)
            g = (self.a * i + self.b * j + self.c * k + self.offset) % 3
            c0[v] = cast(Dir, g)
            c1[v] = cast(Dir, (g + 1) % 3)
            c2[v] = cast(Dir, (g + 2) % 3)
        return c0, c1, c2

    def build(self, m: int) -> Decomposition:
        return Decomposition(m=m, cycle_dirs=self.dirs(m))


def iter_cyclic_shift_linear_mod3_params() -> Iterator[CyclicShiftLinearMod3]:
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for offset in range(3):
                    yield CyclicShiftLinearMod3(a=a, b=b, c=c, offset=offset)
