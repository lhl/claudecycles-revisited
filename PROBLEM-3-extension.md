# PROBLEM-3: Extension Brief (Beyond the Paper)

This file defines work that goes **beyond replication** of Knuth's "Claude's Cycles" (2026-02-28; rev
2026-03-02). For the replication-only problem statement, see `PROBLEM.md`. For the replication feature-parity
tracker, see `PROBLEM-2-followup.md`.

## What has been completed

- **Odd-`m` construction**: implemented, verified for odd `m ∈ [3,101]`, with proof (`proofs/claude_odd_m.md`).
- **Even-`m` failure**: the odd-`m` construction fails for all even `m ∈ [4,100]` under our verifier.
- **Even-`m` certificates**: CP-SAT (`AddCircuit`) found verifier-checked decompositions for `m=4,6,8` (see `artifacts/even_m4/`, `artifacts/even_m6/`, `artifacts/even_m8/`).
- **`m=3` counting parity**: reproduced `11502`, `1012`, `996`, `4554`, `760` (see `artifacts/knuth_m3/`).
- **Symmetry subcounts**: verified and archived as `artifacts/knuth_m3/symmetry_counts.json` (cycle-level `136` of `996`; decomposition-level `92` of `760`; `0` common to both rotations in either interpretation).
- **Claude-like theorem**: proved (`proofs/claude_like_generalizable.md`).
- **Verifier + search tooling**: `claudescycles/verify.py`, `claudescycles/csp.py`, `claudescycles/search.py`.

## What remains open in the paper

Knuth explicitly leaves these unresolved:

1. **Even `m ≥ 4`** — "This decomposition problem remains open for even values of m." (p.5)
   - Stappers empirically found decompositions for `4 ≤ m ≤ 16` (p.1).
   - Claude claimed solutions for `m=4,6,8` but "saw no way to generalize" (p.5).
   - Claude "got stuck" on the even case after solving odd (p.5).
   - `m=2` is provably impossible (Aubert & Schneider, 1982).

2. **"Nicest" decomposition** — Knuth examined several of the 760 valid Claude-like decompositions and
   "didn't encounter any that were actually nicer" than Claude's (p.4).

3. **Symmetry subcounts** — 136 of 760 remain generalizable under `ijk → jki`; none are common to all three
   cyclic mappings `{ijk, jki, kij}` (p.4). We verified symmetry counts and archived results as
   `artifacts/knuth_m3/symmetry_counts.json` (note: the paper’s wording appears ambiguous about whether `136`
   refers to cycles vs decompositions; the artifact reports both).

---

## E1: Even-`m` decomposition (PRIMARY TARGET)

This is the paper's main open problem. The goal is to find decompositions of `G_m` into 3 arc-disjoint
Hamiltonian cycles for even `m ≥ 4`, or to prove impossibility for specific even `m`.

### What we know

- `m=2`: impossible (Aubert & Schneider 1982).
- `m=4`: CP-SAT finds a verifier-checked decomposition (see `artifacts/even_m4/`). (Historical: our CSP returned `NO_HIT` within 50K nodes (~10s).)
- `m=6` and `m=8`: CP-SAT finds verifier-checked decompositions (see `artifacts/even_m6/`, `artifacts/even_m8/`).
- `m=4` has only 64 vertices (192 arcs), so the problem is small enough for SAT/CP-SAT.
- The odd-`m` Claude/Knuth construction fails structurally for even `m`: the "step by 2" coverage argument
  in the cycle 0 proof requires `gcd(2,m)=1`, which fails for even `m`.

### Suggested approach

**Phase 1: Find `m=4` with CP-SAT.**

Recommended solver: OR-Tools CP-SAT (installed). Use `AddCircuit` for Hamiltonian cycle constraints
— this is a purpose-built primitive that enforces a single cycle directly, avoiding hand-rolled
subtour elimination (no MTZ, no lazy cutting planes needed).

**CP-SAT model sketch:**

```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()
m = 4
n = m ** 3

# x[v][c][d] = 1 means "cycle c uses direction d at vertex v"
x = [[[model.NewBoolVar(f"x_{v}_{c}_{d}")
        for d in range(3)] for c in range(3)] for v in range(n)]

# (1) Arc partition: each direction d at vertex v is used by exactly one cycle
for v in range(n):
    for d in range(3):
        model.Add(sum(x[v][c][d] for c in range(3)) == 1)

# (2) Per-vertex permutation: each cycle c uses exactly one direction at vertex v
for v in range(n):
    for c in range(3):
        model.Add(sum(x[v][c][d] for d in range(3)) == 1)

# (3) Hamiltonicity: each cycle is a single directed cycle of length n
#     AddCircuit takes (tail, head, literal) triples
for c in range(3):
    arcs = []
    for v in range(n):
        for d in range(3):
            u = succ(v, d, m)  # successor of v along direction d
            arcs.append((v, u, x[v][c][d]))
    model.AddCircuit(arcs)

# (4) Symmetry breaking: fix permutation at v=000 (cycle labels are arbitrary)
model.Add(x[0][0][0] == 1)  # cycle 0 bumps i at (0,0,0)
model.Add(x[0][1][1] == 1)  # cycle 1 bumps j at (0,0,0)
model.Add(x[0][2][2] == 1)  # cycle 2 bumps k at (0,0,0)
```

Note: constraint (1) + (2) together enforce that each vertex gets a permutation of `{0,1,2}`
across the three cycles. Constraint (3) uses `AddCircuit` which natively handles subcycle
elimination. Constraint (4) breaks the 6-fold cycle-label symmetry.

**Repro knobs:** Always set and record `--seed`, `--time-limit`, `--num-workers`. Save solver
stats/logs alongside the solution JSON and verifier output as artifacts. Example:

```
artifacts/even_m4/
  solution.json        # per-vertex direction lists (verifier input format)
  verify.json          # verifier output
  solver_stats.json    # time, nodes, seed, workers, status
```

- **Any claimed solution must pass `claudescycles/verify.py`.**
- Alternative: improve our CSP (`claudescycles/csp.py`) with stronger propagation (arc consistency,
  fiber-layer decomposition, symmetry breaking).

**Phase 2: Analyze the `m=4` solution.**

Post-solve analysis checklist (this is where the research value lives):

- [ ] **Diff vs. odd-`m` rule**: how many vertices have a different permutation? Which `s`-layers
  or hyperplanes concentrate the differences?
- [ ] **Fiber structure**: does `σ(v)` depend only on `s = (i+j+k) mod m` and a few coordinates,
  as in the odd-`m` case? Or is the dependence more complex?
- [ ] **Boundary vs. interior**: is it "Claude-like" (depends only on whether `i,j,s` are `0`, `m-1`,
  or interior)? If not, what additional case distinctions are needed?
- [ ] **Invariants**: does `s` still increase by 1 each step? Are there other conserved quantities?
- [ ] **Canonicalization**: reduce under obvious symmetries (cycle relabeling, vertex translations,
  coordinate permutations `ijk → jki` etc.) so solutions can be meaningfully compared across runs
  and across different `m` values.
- [ ] Extract structural invariants that could guide a general even-`m` construction.

**Phase 3: Scale up.**

- Attempt `m=6,8` with the same solver. `m=6` has 216 vertices (feasible for CP-SAT); `m=8` has 512
  (may require stronger techniques or longer time limits).
- Apply the same post-solve analysis checklist to each solution.
- Look for patterns across even solutions. Are there "even-`m` Claude-like" constructions?
- If a general pattern emerges, prove it.

**Phase 4: If no pattern emerges, characterize the obstruction.**

- What structural property distinguishes even from odd?
- Is there a parity invariant that constrains even-`m` decompositions?
- Can we prove impossibility for any specific even `m > 2`?

### Existing tooling

- Verifier: `python -m claudescycles.verify --input <json>` — use this to validate any candidate.
- CSP solver: `python -m claudescycles.search --m 4 --family csp --max-nodes <N>` — current solver,
  insufficient for `m=4` without better pruning.
- Construction generator: `python -m claudescycles.generate --m <m> --family claude` — only works for odd `m`.
- Scanner: `python -m claudescycles.scan` — batch validation.

### Success criteria

- [x] Find a verified decomposition for `m=4` (JSON artifact + verifier `OK`).
- [x] Find verified decompositions for `m=6` and `m=8`.
- [ ] Complete post-solve analysis checklist for each even-`m` solution found.
- [ ] Characterize structural differences between even-`m` and odd-`m` solutions.
- [ ] Either propose a general even-`m` construction or identify the obstruction.

---

## E2: Symmetry verification and classification

### E2a: Verify the 136 / "none under all three" claims (run in parallel with E1)

This is a quick win that closes a paper-parity loose end while E1's solver runs. It requires
no new solver infrastructure — just a remapping over the existing 760 archived decompositions.

The paper states (p.4) that 136 of the 760 generalizable decompositions remain generalizable under
`ijk → jki`, but none are common to all three cyclic mappings `{ijk, jki, kij}`.

- Implement the `ijk → jki` remapping on decompositions.
- Filter the 760 archived decompositions and count.
- Archived result: `artifacts/knuth_m3/symmetry_counts.json`. (Cycle-level: `136` of `996` generalizable cycles remain generalizable under `ijk→jki`; decomposition-level: `92` of `760` all-generalizable decompositions map to another such decomposition under `ijk→jki`; `0` common to both rotations in either interpretation.)

### E2b: Classify the 760 decompositions

The paper asks whether any of the 760 are "nicer" than Claude's. Possible classification axes:

- Symmetry group (which coordinate permutations preserve the decomposition).
- Structural simplicity of the case table (fewer distinct cases = "nicer").
- Number of distinct fiber-layer permutation patterns.
- Whether the decomposition admits a compact closed-form description.

---

## E3: Proof tightening

Our proof writeup (`proofs/claude_odd_m.md`) can be strengthened in two places:

1. **Cycle 0**: The "block" argument is narrative; rewrite it as explicit state transitions with an
   algebraic orbit description (analogous to what we did for cycle 1).
2. **Cycle 2**: The orbit argument asserts single-orbit coverage without a parametric bijection; provide
   one (analogous to cycle 1's `v(r,t) = (-2t, r+t, t-r)`).

Goal: make all three cycle proofs machine-checkable (expressible as a finite set of algebraic equalities
that can be verified symbolically or by exhaustive checking at `m=3,5,7`).

---

## E4: Stretch goals

### Higher-dimensional generalization

The graph `G_m` is `Cay(Z_m^3, {e_0, e_1, e_2})` — the Cayley digraph of `Z_m^3` with standard generators.
The natural generalization is `Cay(Z_m^n, {e_0, ..., e_{n-1}})` for `n > 3`: can its arcs be decomposed
into `n` directed Hamiltonian cycles?

- `n=2`: classical; decompositions are known for all `m > 2` (related to Gray codes).
- `n=3`: the subject of this paper (odd `m` solved, even `m` open).
- `n=4` and beyond: wide open.

### Independent cross-check of `m=3` counts (P2-03)

Implement a second, independent enumeration path for the `m=3` counts (different algorithm or
independently written code) to confirm `11502`, `1012`, `996`, `4554`, `760`.

---

## Priority order

1. **E1** (even `m`) — the paper's main open problem; highest research value.
2. **E2a** (symmetry verification) — quick win, closes a replication gap.
3. **E3** (proof tightening) — improves rigor of existing results.
4. **E2b** (classification of 760) — interesting but lower priority.
5. **E4** (stretch goals) — only after E1–E3.

## Solver availability

- `z3-solver`: **installed** ✓
- `ortools` (CP-SAT): **installed** ✓
- `scipy.optimize.milp`: available (less suited to combinatorial search)

Both recommended solvers are ready for E1. CP-SAT (`ortools`) is likely the best fit
for the subcycle-elimination constraints in the decomposition problem.
