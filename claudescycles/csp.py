from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator, Sequence

from .core import Decomposition, Dir, n_vertices
from .verify import verify_decomposition

# Each vertex chooses one of the 6 permutations of directions across the 3 cycles.
PERMS: tuple[tuple[Dir, Dir, Dir], ...] = (
    (0, 1, 2),
    (0, 2, 1),
    (1, 0, 2),
    (1, 2, 0),
    (2, 0, 1),
    (2, 1, 0),
)


def _preds(v: int, m: int) -> tuple[int, int, int]:
    """
    Predecessor indices of v along the 3 generator directions.

    If u0 is returned as first element, then succ_idx(u0, 0, m) == v, etc.
    """
    mm = m * m
    i, r = divmod(v, mm)
    j, k = divmod(r, m)

    pred_i = ((i - 1) % m) * mm + j * m + k
    pred_j = i * mm + ((j - 1) % m) * m + k
    pred_k = i * mm + j * m + ((k - 1) % m)
    return pred_i, pred_j, pred_k


@dataclass(frozen=True)
class Constraint:
    cycle: int
    pred0: int
    pred1: int
    pred2: int

    def vars(self) -> tuple[int, int, int]:
        return self.pred0, self.pred1, self.pred2


@dataclass(frozen=True)
class CspStats:
    nodes: int
    max_nodes: int
    hit_max_nodes: bool


@dataclass(frozen=True)
class CspResult:
    solutions: list[Decomposition]
    stats: CspStats


def _opt_dir(opt: int, cycle: int) -> int:
    return PERMS[opt][cycle]


def _domain_iter(mask: int) -> Iterator[int]:
    for opt in range(6):
        if mask & (1 << opt):
            yield opt


def _domain_size(mask: int) -> int:
    return mask.bit_count()


def _prune_for_constraint(
    domains: list[int],
    constraint: Constraint,
    *,
    var: int,
) -> bool:
    """
    Enforce generalized arc consistency of one var domain w.r.t. a single constraint.

    Returns True if var's domain changed.
    """
    cycle = constraint.cycle
    pred0, pred1, pred2 = constraint.pred0, constraint.pred1, constraint.pred2

    if var not in (pred0, pred1, pred2):
        return False

    wanted_dir = 0 if var == pred0 else 1 if var == pred1 else 2
    other1, other2 = (
        (pred1, pred2) if var == pred0 else (pred0, pred2) if var == pred1 else (pred0, pred1)
    )

    before = domains[var]
    after = before

    for opt in _domain_iter(before):
        lit_var = _opt_dir(opt, cycle) == wanted_dir
        supported = False
        for opt1 in _domain_iter(domains[other1]):
            lit1 = _opt_dir(opt1, cycle) == (0 if other1 == pred0 else 1 if other1 == pred1 else 2)
            for opt2 in _domain_iter(domains[other2]):
                lit2 = _opt_dir(opt2, cycle) == (
                    0 if other2 == pred0 else 1 if other2 == pred1 else 2
                )
                if (lit_var + lit1 + lit2) == 1:
                    supported = True
                    break
            if supported:
                break
        if not supported:
            after &= ~(1 << opt)

    if after != before:
        domains[var] = after
        return True
    return False


def _propagate(
    domains: list[int],
    constraints_by_var: list[list[int]],
    constraints: list[Constraint],
    *,
    initial_queue: Iterable[int] | None = None,
) -> bool:
    if initial_queue is None:
        queue = list(range(len(constraints)))
    else:
        queue = list(initial_queue)

    in_queue = bytearray(len(constraints))
    for i in queue:
        in_queue[i] = 1

    while queue:
        c_idx = queue.pop()
        in_queue[c_idx] = 0
        c = constraints[c_idx]
        for var in c.vars():
            changed = _prune_for_constraint(domains, c, var=var)
            if not changed:
                continue
            if domains[var] == 0:
                return False
            for other_c_idx in constraints_by_var[var]:
                if not in_queue[other_c_idx]:
                    in_queue[other_c_idx] = 1
                    queue.append(other_c_idx)
    return True


def _select_unassigned(domains: Sequence[int]) -> int | None:
    best_v: int | None = None
    best_size = 10**9
    for v, mask in enumerate(domains):
        sz = _domain_size(mask)
        if sz <= 1:
            continue
        if sz < best_size:
            best_size = sz
            best_v = v
    return best_v


def _domains_to_decomposition(m: int, domains: Sequence[int]) -> Decomposition:
    n = n_vertices(m)
    c0: list[Dir] = [0] * n
    c1: list[Dir] = [0] * n
    c2: list[Dir] = [0] * n
    for v, mask in enumerate(domains):
        if _domain_size(mask) != 1:
            raise ValueError("not a full assignment")
        opt = next(_domain_iter(mask))
        d0, d1, d2 = PERMS[opt]
        c0[v] = d0
        c1[v] = d1
        c2[v] = d2
    return Decomposition(m=m, cycle_dirs=(c0, c1, c2))


def solve_csp(
    m: int,
    *,
    max_solutions: int = 1,
    max_nodes: int = 2_000_000,
    allowed_options_mask: int | None = None,
    fix_vertex0_option: int | None = 0,
    fixed_options: dict[int, int] | None = None,
) -> CspResult:
    """
    Solve the indegree=1 constraints for all 3 cycles with per-vertex permutation coupling.

    Returns decompositions that also pass the Hamiltonian-cycle verifier.
    """
    if m <= 2:
        raise ValueError("m must be > 2")
    n = n_vertices(m)

    constraints: list[Constraint] = []
    for v in range(n):
        p0, p1, p2 = _preds(v, m)
        for cycle in range(3):
            constraints.append(Constraint(cycle=cycle, pred0=p0, pred1=p1, pred2=p2))

    constraints_by_var: list[list[int]] = [[] for _ in range(n)]
    for idx, c in enumerate(constraints):
        for v in c.vars():
            constraints_by_var[v].append(idx)

    all_opts = (1 << 6) - 1
    base_mask = all_opts if allowed_options_mask is None else allowed_options_mask
    if base_mask & ~all_opts:
        raise ValueError("allowed_options_mask contains invalid bits")
    domains: list[int] = [base_mask] * n

    merged_fixes: dict[int, int] = {}
    if fix_vertex0_option is not None:
        if not (0 <= fix_vertex0_option < 6):
            raise ValueError("fix_vertex0_option must be in [0,6)")
        merged_fixes[0] = fix_vertex0_option
    if fixed_options:
        merged_fixes.update(fixed_options)

    for v, opt in merged_fixes.items():
        if not (0 <= v < n):
            raise ValueError("fixed_options contains out-of-range vertex index")
        if not (0 <= opt < 6):
            raise ValueError("fixed_options values must be in [0,6)")
        domains[v] = 1 << opt
        if (domains[v] & base_mask) == 0:
            raise ValueError("fixed option not allowed by allowed_options_mask")

    if not _propagate(domains, constraints_by_var, constraints):
        return CspResult(
            solutions=[],
            stats=CspStats(nodes=0, max_nodes=max_nodes, hit_max_nodes=False),
        )

    solutions: list[Decomposition] = []
    nodes = 0

    def backtrack(domains: list[int]) -> None:
        nonlocal nodes
        if len(solutions) >= max_solutions:
            return
        if nodes >= max_nodes:
            return
        nodes += 1

        v = _select_unassigned(domains)
        if v is None:
            decomp = _domains_to_decomposition(m, domains)
            if verify_decomposition(decomp).ok:
                solutions.append(decomp)
            return

        mask = domains[v]
        for opt in _domain_iter(mask):
            child = domains.copy()
            child[v] = 1 << opt
            if not _propagate(
                child,
                constraints_by_var,
                constraints,
                initial_queue=constraints_by_var[v],
            ):
                continue
            backtrack(child)
            if len(solutions) >= max_solutions or nodes >= max_nodes:
                return

    backtrack(domains)
    return CspResult(
        solutions=solutions,
        stats=CspStats(nodes=nodes, max_nodes=max_nodes, hit_max_nodes=(nodes >= max_nodes)),
    )
