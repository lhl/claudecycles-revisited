# CONTEXT CAPSULE

## Objective
Solve the `G_m` arc decomposition problem (see `PROBLEM.md`) with reproducible scripts and proofs.

## Current Best Known
- **Theorem 1**: For all m >= 3, G_m decomposes into 3 arc-disjoint directed Hamiltonian cycles.
- **Theorem 2**: For m = 2, no such decomposition exists.
- Computational verification: m=3..30 solved and verified via CP-SAT.
- Theoretical proof: existence for all m >= 3 via Cayley digraph literature (Westlund 2009).
- No closed-form algebraic construction found.

## Latest Validated Evidence
- 28 verified decompositions in `artifacts/decomposition_mN.json` (N=3..30).
- Batch summary in `artifacts/batch_summary.json`.
- Proof document in `proofs/decomposition_proof.md`.
- All solutions independently verifiable via `scripts/verify.py`.

## Key Scripts
- `scripts/verify.py` - Deterministic decomposition verifier
- `scripts/solve.py` - CP-SAT solver (OR-Tools, AddCircuit constraints)
- `scripts/batch_solve.py` - Batch solver for range of m values
- `scripts/deep_analyze.py` - Pattern analysis, cyclic symmetry solver
- `scripts/construct_lift.py` - Layer-lifting construction (proven infeasible)

## Failed Construction Approaches
1. Single diagonal derangement - INFEASIBLE
2. Diagonal-class-only dependence - INFEASIBLE
3. Pure rotation d_c(v) = (c + delta(v)) mod 3 - INFEASIBLE
4. Layer lifting with fixed normal assignment - INFEASIBLE

## Open Problems
1. Explicit closed-form construction for all m >= 3
2. Provably polynomial-time construction algorithm
3. Structural characterization of odd vs even m

## Next Actions
1. Write final summary (P4-01).
2. Investigate alternative construction strategies if desired.
