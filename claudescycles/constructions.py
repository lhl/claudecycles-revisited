from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from .io import Decomposition


def _choose_a_odd_m(m: int) -> int:
    """Choose A in [0, m-2] with gcd(m,2A+1)=gcd(m,2A+3)=1.

    This parameter controls how many w-rows in {2,...,m-1} assign cycle0 as the
    "majority i-edge" cycle (the remainder assign cycle1).

    Existence: for all odd m >= 5 (exception m=3).
    """

    if m % 2 == 0 or m <= 2:
        raise ValueError("m must be odd and > 2")
    for a in range(0, m - 1):  # 0..m-2 inclusive
        if math.gcd(m, 2 * a + 1) == 1 and math.gcd(m, 2 * a + 3) == 1:
            return a
    raise ValueError("no valid parameter A found (this happens for m=3)")


def construct_decomposition_odd_m(m: int) -> Decomposition:
    """Explicit 3-cycle decomposition for odd m >= 5.

    Produces direction tables in the canonical (i,j,k)-lex vertex order.

    Direction encoding per vertex:
      0: increment i
      1: increment j
      2: increment k
    """

    if m == 3:
        raise ValueError("odd-m construction does not cover m=3 (use solver artifact)")
    a = _choose_a_odd_m(m)

    n = m * m * m
    dirs: List[bytearray] = [bytearray(n), bytearray(n), bytearray(n)]

    # In (u,v,w) coordinates with:
    #   u = i
    #   v = i + j
    #   w = i + j + k
    # the construction depends only on (v,w). We compute (v,w) on the fly:
    #   v = (i+j) % m
    #   w = (v+k) % m
    #
    # Row assignment (which cycle takes k-edge everywhere on that w-row):
    #   w = 0 -> cycle0 takes dir2
    #   w = 1 -> cycle1 takes dir2
    #   w >= 2 -> cycle2 takes dir2
    #
    # For w=0 and w=1 we force cycle2 to be the "minority i-edge" cycle.
    # For w>=2, we choose the first `a` rows to make cycle0 majority, the rest cycle1.
    majority0_rows = set(range(2, 2 + a))  # subset of {2,...,m-1}

    for i in range(m):
        for j in range(m):
            v = (i + j) % m
            for k in range(m):
                w = (v + k) % m
                idx = i * (m * m) + j * m + k

                if w == 0:
                    # cycle0: k-edge
                    dirs[0][idx] = 2
                    # cycle2 (minority): i-edge only at v==0, else j-edge
                    dirs[2][idx] = 0 if v == 0 else 1
                    # cycle1 gets the remaining direction
                    dirs[1][idx] = 1 if v == 0 else 0
                    continue

                if w == 1:
                    # cycle1: k-edge
                    dirs[1][idx] = 2
                    dirs[2][idx] = 0 if v == 0 else 1
                    dirs[0][idx] = 1 if v == 0 else 0
                    continue

                # w >= 2: cycle2 takes k-edge
                dirs[2][idx] = 2
                if w in majority0_rows:
                    # cycle0 majority (i-edge except v==0)
                    dirs[0][idx] = 1 if v == 0 else 0
                    dirs[1][idx] = 0 if v == 0 else 1
                else:
                    # cycle1 majority
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

