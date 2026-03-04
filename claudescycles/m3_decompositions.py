from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class DecompositionTriple:
    """
    An exact cover of the 81 arcs of G_3 by three Hamiltonian cycles.

    Indices refer to the ordering returned by the caller's cycle list.
    """

    a: int
    b: int
    c: int


def list_m3_decompositions_from_arc_masks(arc_masks: Sequence[int]) -> list[DecompositionTriple]:
    """
    Enumerate all unordered triples {a,b,c} of Hamiltonian cycles whose arc sets partition all arcs of G_3.

    The algorithm uses the fact that if masks A,B are disjoint, then the third mask must be exactly
    ALL ^ (A|B). Each decomposition is counted once via the ordering constraint a < b < c.
    """
    n_cycles = len(arc_masks)
    all_arcs_mask = (1 << (27 * 3)) - 1  # 81 bits

    mask_to_idx: dict[int, int] = {}
    for idx, m in enumerate(arc_masks):
        if m in mask_to_idx:
            raise ValueError("duplicate arc mask detected (cycle identity collision)")
        mask_to_idx[m] = idx

    out: list[DecompositionTriple] = []

    masks = arc_masks
    get = mask_to_idx.get
    for a in range(n_cycles):
        ma = masks[a]
        for b in range(a + 1, n_cycles):
            mb = masks[b]
            if ma & mb:
                continue
            union = ma | mb
            c_mask = all_arcs_mask ^ union
            c = get(c_mask)
            if c is None or c <= b:
                continue
            out.append(DecompositionTriple(a=a, b=b, c=c))

    return out


def count_m3_decompositions_in_subset(
    decomps: Iterable[DecompositionTriple], *, allowed: set[int]
) -> int:
    """
    Count decompositions whose three cycles are all in the given allowed index set.
    """
    c = 0
    for d in decomps:
        if d.a in allowed and d.b in allowed and d.c in allowed:
            c += 1
    return c

