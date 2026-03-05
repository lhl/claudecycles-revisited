from __future__ import annotations

import math

from .io import Decomposition


def _choose_a_odd_m(m: int) -> int:
    if m % 2 == 0 or m <= 2:
        raise ValueError("m must be odd and > 2")

    for a in range(0, m - 1):
        if math.gcd(m, 2 * a + 1) == 1 and math.gcd(m, 2 * a + 3) == 1:
            return a
    raise ValueError("no valid parameter A found (this happens for m=3)")


def construct_decomposition_odd_m(m: int) -> Decomposition:
    if m == 3:
        raise ValueError("odd-m construction does not cover m=3 (use solver artifact)")

    a = _choose_a_odd_m(m)
    n = m * m * m
    dirs = [bytearray(n), bytearray(n), bytearray(n)]
    majority0_rows = set(range(2, 2 + a))

    for i in range(m):
        for j in range(m):
            v = (i + j) % m
            for k in range(m):
                w = (v + k) % m
                idx = i * m * m + j * m + k

                if w == 0:
                    dirs[0][idx] = 2
                    dirs[2][idx] = 0 if v == 0 else 1
                    dirs[1][idx] = 1 if v == 0 else 0
                    continue

                if w == 1:
                    dirs[1][idx] = 2
                    dirs[2][idx] = 0 if v == 0 else 1
                    dirs[0][idx] = 1 if v == 0 else 0
                    continue

                dirs[2][idx] = 2
                if w in majority0_rows:
                    dirs[0][idx] = 1 if v == 0 else 0
                    dirs[1][idx] = 0 if v == 0 else 1
                else:
                    dirs[1][idx] = 1 if v == 0 else 0
                    dirs[0][idx] = 0 if v == 0 else 1

    meta = {
        "generator": "claudescycles.constructions.construct_decomposition_odd_m",
        "family": "odd_m_row_based_vw_construction",
        "m": m,
        "A": a,
        "notes": "Proved Hamilton decomposition for odd m>=5 via (u,v,w)=(i,i+j,i+j+k) lift argument; m=3 excluded.",
    }
    return Decomposition(m=m, dirs=dirs, meta=meta)
