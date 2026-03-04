# IMPLEMENTATION - claudescycles

## Objective

Solve the directed graph decomposition problem in `PROBLEM.md`: decompose the arcs of `G_m` into three directed Hamiltonian cycles for general `m`.

## Baseline

- Problem definition: `PROBLEM.md`
- Current status: initial workflow setup
- Evidence policy: every completed item must cite exact command(s) and outcomes

## Pre-Analysis (Update Before Each Major Item)

- Scope:
- Risks:
- Validation plan:
- Expected artifacts:

## Active Punchlist

- [x] P0-01: Bootstrap workflow files (`AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`)
- [x] P0-01a: Add `PROBLEM.md` (problem statement)
- [ ] P0-02: Add deterministic verifier script for decomposition validity
- [ ] P1-01: Build search/solver tooling to find decompositions for small `m` (start with `m=3`)
- [ ] P1-02: Discover valid decompositions and identify candidate construction patterns
- [ ] P1-03: Test candidate patterns on larger `m` values
- [ ] P1-04: Save discovery outputs under `artifacts/` with command provenance
- [ ] P2-01: Generalize candidate patterns and validate over broad `m` ranges
- [ ] P2-02: Investigate both odd and even `m` cases separately
- [ ] P3-01: Attempt a formal proof (or clearly scoped partial proof) in `proofs/`
- [ ] P3-02: Catalog failed constructions and failure modes
- [ ] P4-01: Write final summary of proven facts, open conjectures, and next experiments

## Deferrals

| ID | Item | Rationale | Risk | Target |
|---|---|---|---|---|

## Validation Log (Commands + Outcomes)

- Bootstrap: workflow files created
