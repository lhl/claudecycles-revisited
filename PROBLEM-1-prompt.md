Goal:
1) Build code to search/verify decompositions of the directed graph in `PROBLEM.md`.
2) Produce a rigorous proof (or clearly scoped partial proof) of your discovered construction.

Requirements:
- Follow `AGENTS.md` strictly (worklog/memory/checkpoint discipline).
- Start by creating deterministic verification code that checks:
  - each of 3 cycles is Hamiltonian (length m^3),
  - cycles are arc-disjoint,
  - union covers all arcs.
- Then build search tooling for small m to discover candidate patterns.
- Generalize candidate patterns and validate over broad ranges.
- Attempt a formal proof in a `proofs/` document with theorem/lemmas.
- If full proof fails, provide the strongest partial theorem with explicit unresolved lemmas.
- Record exact commands/results in `WORKLOG.md` and punchlist progress in `docs/IMPLEMENTATION.md`.
- Save machine-readable outputs in `artifacts/`.

Success criteria:
- Reproducible code + reproducible evidence + proof document (full or clearly bounded partial).
