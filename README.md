# claudescycles-revisited

Reproducible search, verification, and proof work for decomposing all arcs of
the directed graph `G_m` (on `Z_m^3`) into three Hamiltonian directed cycles.

## Problem

Given `m > 2`, `G_m` has vertices `(i,j,k)` and outgoing arcs:

- `(i,j,k) -> (i+1,j,k)`
- `(i,j,k) -> (i,j+1,k)`
- `(i,j,k) -> (i,j,k+1)`

all mod `m`.

Goal: partition all `3m^3` arcs into 3 arc-disjoint Hamiltonian cycles
(each length `m^3`).

Primary problem statement: `PROBLEM.md`.

## What Is Implemented

## 1) Deterministic verification

- `claudescycles/verify.py`
- `claudescycles/gm.py`
- `claudescycles/io.py`
- `scripts/verify_decomp.py`

Checks:

- each cycle is Hamiltonian (`m^3` steps, no revisits, returns to start),
- cycles are arc-disjoint,
- union covers all arcs.

## 2) Exact search for small `m` (CP-SAT)

- `scripts/search_cp_sat.py`

Model:

- boolean arc-color assignment variables,
- per-arc exactly-one-cycle assignment,
- `AddCircuit` per cycle (single directed cycle),
- deterministic settings (`num_search_workers=1`, seed configurable).

## 3) Closed-form odd-`m` construction

- `claudescycles/constructions.py`
- `scripts/gen_construction_odd.py`
- `scripts/validate_construction_odd.py`

Construction currently covers odd `m >= 5` (with parameter selection via gcd
constraints).

## 4) Proof and analysis docs

- `proofs/odd_m_construction.md`: theorem+lemmas for odd `m >= 5`
- `proofs/failure_modes.md`: failed constructions and unresolved lemmas
- `docs/FINAL_SUMMARY.md`: status and next experiments

## Current Status

## Proven

- Full theorem for odd `m >= 5` (implemented construction is correct):
  - 3 Hamiltonian cycles,
  - arc-disjoint,
  - full arc coverage.

## Computationally validated

- CP-SAT solutions verified for:
  - `m in {3,4,6,8,10,12}`
- Odd construction batch-validated for:
  - all odd `m` in `[5,101]` (`49/49` passing).

## Open

- No general even-`m` closed-form construction/proof yet.

## Reproducibility Quick Start

## Verify an existing artifact

```bash
python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json --json
```

## Search a solution with CP-SAT

```bash
python scripts/search_cp_sat.py 6 --time-limit-s 180 --seed 0 --out artifacts/solutions/cpsat_m6.json
python scripts/verify_decomp.py artifacts/solutions/cpsat_m6.json
```

## Generate odd-construction artifact

```bash
python scripts/gen_construction_odd.py 11 --out artifacts/constructions/odd_m11.json
python scripts/verify_decomp.py artifacts/constructions/odd_m11.json
```

## Validate odd construction over a range

```bash
python scripts/validate_construction_odd.py --m-max 101 --out artifacts/validation/odd_construction_validation_m101.json
```

## Artifacts

- `artifacts/solutions/`: CP-SAT discovered decompositions
- `artifacts/constructions/`: explicit construction outputs
- `artifacts/validation/`: machine-readable validation summaries
- `artifacts/smoke/`: negative/sanity test fixtures

Important files:

- `artifacts/validation/cpsat_small_m_summary.json`
- `artifacts/validation/odd_construction_validation_m101.json`

## Repository Memory / Execution Discipline

Project memory files used and maintained during execution:

- `docs/IMPLEMENTATION.md` (punchlist + validation log)
- `WORKLOG.md` (chronological command/results log)
- `state/CONTEXT.md` (restart capsule)

## Future Directions

1. Infer structural invariants from even-`m` CP-SAT outputs and propose a
   parametric even-family construction.
2. Extend the odd-case lift proof strategy to an even-case family.
3. Add proof-oriented invariant checks as executable scripts/tests.
