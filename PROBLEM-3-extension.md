# PROBLEM-3: Extension Brief (Beyond the Paper)

This file defines work that goes **beyond replication** of Knuth's "Claude's Cycles" (2026-02-28; rev
2026-03-02). For the replication-only problem statement, see `PROBLEM.md`. For the replication feature-parity
tracker, see `PROBLEM-2-followup.md`.

## What has been completed

- **Odd-`m` construction**: implemented, verified for odd `m ∈ [3,101]`, with proof (`proofs/claude_odd_m.md`).
- **Even-`m` failure**: the odd-`m` construction fails for all even `m ∈ [4,100]` under our verifier.
- **`m=3` counting parity**: reproduced `11502`, `1012`, `996`, `4554`, `760` (see `artifacts/knuth_m3/`).
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
   cyclic mappings `{ijk, jki, kij}` (p.4). We have not independently verified these claims.

---

## E1: Even-`m` decomposition (PRIMARY TARGET)

This is the paper's main open problem. The goal is to find decompositions of `G_m` into 3 arc-disjoint
Hamiltonian cycles for even `m ≥ 4`, or to prove impossibility for specific even `m`.

### What we know

- `m=2`: impossible (Aubert & Schneider 1982).
- `m=4`: Stappers found a solution empirically; our CSP returned `NO_HIT` within 50K nodes (~10s).
- `m=4` has only 64 vertices (192 arcs), so the problem is small enough for SAT/CP-SAT.
- The odd-`m` Claude/Knuth construction fails structurally for even `m`: the "step by 2" coverage argument
  in the cycle 0 proof requires `gcd(2,m)=1`, which fails for even `m`.

### Suggested approach

**Phase 1: Find `m=4` with a strong solver.**

- Use `z3-solver` or `ortools` CP-SAT (both installed).
- Encode the decomposition problem as SAT or CP-SAT:
  - Variables: at each vertex `v`, a choice of permutation `σ(v) ∈ S_3` (6 choices → can encode as 3 bits
    or use CP-SAT's integer domain).
  - Constraints: for each cycle `c ∈ {0,1,2}`, the functional digraph induced by following direction `σ(v)[c]`
    must be a single cycle of length `m^3`. This is the hard constraint — subcycle elimination.
  - Standard technique: use subtour elimination constraints (MTZ formulation or lazy cutting planes).
- Alternative: improve our CSP (`claudescycles/csp.py`) with stronger propagation (arc consistency,
  fiber-layer decomposition, symmetry breaking).
- **Any claimed solution must pass `claudescycles/verify.py` and be archived as a JSON artifact.**

**Phase 2: Analyze the `m=4` solution.**

- Once we have a verified `m=4` decomposition, characterize its structure:
  - Does it have any fiber-layer regularity? (Does `σ(v)` depend only on `s = (i+j+k) mod m` and a few
    coordinates, as in the odd-`m` case?)
  - Is it "Claude-like" (depends only on whether `i,j,s` are `0`, `m-1`, or interior)?
  - Compare with the odd-`m` rule: where specifically do they differ?
- Extract structural invariants that could guide a general even-`m` construction.

**Phase 3: Scale up.**

- Attempt `m=6,8` with the same solver. `m=6` has 216 vertices (feasible for SAT); `m=8` has 512
  (may require stronger techniques).
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

- [ ] Find a verified decomposition for `m=4` (JSON artifact + verifier `OK`).
- [ ] Find verified decompositions for `m=6` and `m=8`.
- [ ] Characterize structural differences between even-`m` and odd-`m` solutions.
- [ ] Either propose a general even-`m` construction or identify the obstruction.

---

## E2: Symmetry verification and classification

### E2a: Verify the 136 / "none under all three" claims

The paper states (p.4) that 136 of the 760 generalizable decompositions remain generalizable under
`ijk → jki`, but none are common to all three cyclic mappings `{ijk, jki, kij}`.

- Implement the `ijk → jki` remapping on decompositions.
- Filter the 760 archived decompositions and count.
- Expected: 136 survive under one rotation, 0 survive under all three.
- Archive result as `artifacts/knuth_m3/symmetry_counts.json`.

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
