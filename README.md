# claudescycles-revisited

This repo contains reproducible code, artifacts, and proofs for the directed graph arc-decomposition problem in
[`PROBLEM.md`](PROBLEM.md).

## Problem (G_m)

For an integer `m > 2`, define the directed graph `G_m` on vertices `(i,j,k) in Z_m^3` with 3 outgoing arcs per
vertex (increment exactly one coordinate by `+1 mod m`).

Goal: decompose the full arc set (size `3*m^3`) into **three arc-disjoint directed Hamiltonian cycles**, each of
length `m^3`.

## What This Repo Implements

- A deterministic verifier for candidate decompositions (Hamiltonicity + arc partition).
- CP-SAT search tooling to find decompositions for small `m` (and some larger `m`) and archive them as artifacts.
- An explicit, proven construction for **odd** `m >= 5` with broad-range validation outputs.
- A proof document with theorem/lemmas for the odd-m construction.
- Durable project memory (`docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`) per `AGENTS.md`.

## Repository Layout

- `claudescycles/`: core Python library (graph indexing, I/O, verifier, constructions).
- `scripts/`: CLIs for verification, CP-SAT search, construction generation, and range validation.
- `proofs/`: formal proof documents.
- `artifacts/`: machine-readable solver outputs, constructions, and validation summaries.
- `docs/`: punchlist/status and a failure-mode catalog.

## Quickstart

All commands below are intended to be run from the repo root.

### Verify a decomposition

Decompositions are stored as JSON files that contain `m` and three direction tables (`dirs`), where each table
specifies which of the 3 outgoing arcs the cycle takes at each vertex.

```bash
python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json
```

### Search for a decomposition (CP-SAT)

This uses OR-Tools CP-SAT with `AddCircuit`. For determinism the solver is run single-threaded and seeded.

```bash
python scripts/search_cp_sat.py 8 --time-limit-s 1800 --seed 0 --overwrite
python scripts/verify_decomp.py artifacts/solutions/cpsat_m8.json
```

For `m=16`, `--seed 1` was observed to be much faster than `--seed 0`:

```bash
python scripts/search_cp_sat.py 16 --time-limit-s 1800 --seed 1 --overwrite
python scripts/verify_decomp.py artifacts/solutions/cpsat_m16.json
```

### Generate the explicit odd-m construction (m >= 5)

```bash
python scripts/gen_construction_odd.py 11 --overwrite
python scripts/verify_decomp.py artifacts/constructions/odd_m11.json
```

### Validate the odd-m construction over a range

```bash
python scripts/validate_construction_odd.py --m-max 101
cat artifacts/validation/odd_construction_validation.json
```

## Status

### Proven (odd m)

- A general decomposition is implemented and proven for **odd `m >= 5`**:
  - Construction code: `claudescycles/constructions.py`
  - Proof: `proofs/odd_m_construction.md`
  - Broad validation output: `artifacts/validation/odd_construction_validation.json` (odd `m=5..101`)
- The small case `m=3` is not covered by this construction but is covered by an explicit verified solver artifact:
  `artifacts/solutions/cpsat_m3.json`.

### Computational evidence (even m)

Verified CP-SAT solutions are archived under `artifacts/solutions/` for even `m` including:
`m=4,6,8,10,12,14,16` (each with a matching `*.verify.json` report).

### Open (even m)

No general even-`m` construction/proof is included yet. See `docs/FAILED_ATTEMPTS.md` for documented restrictions
and failure modes (including an obstruction to overly-structured even-`m` families).

## Future Directions

- Find a general even-`m` construction, likely requiring essential dependence on additional coordinates beyond the
  odd-m proof's reduced-state representation.
- Add analysis tooling to infer structured rules from CP-SAT solutions (e.g., constrained program synthesis over
  modular arithmetic features).
- Extend CP-SAT evidence to additional even `m` and record scalability limits + solver parameter sensitivity.
- Strengthen partial theorems / impossibility results for restricted construction families.
- Write a final project summary of proven results, computational evidence, conjectures, and next experiments.

