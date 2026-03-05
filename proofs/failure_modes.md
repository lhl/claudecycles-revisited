# Failure Modes and Unresolved Lemmas

## Verified Failure Modes

## F1: Arc-partition violation (sanity check)

- Construction: all three cycles pick direction `0` at every vertex.
- Evidence command:
  - `python - <<'PY' ... verify_decomposition(3, [all-0, all-0, all-0]) ... PY`
- Result:
  - `arc partition violated at 27/27 vertices`

## F2: Not Hamiltonian even when arc-partition is locally valid

- Construction: cycle 0 uses only `X`, cycle 1 only `Y`, cycle 2 only `Z`.
- Evidence command:
  - `python scripts/verify_decomp.py artifacts/smoke/invalid_m3_axes.json --json`
- Result:
  - local partition passes, but all cycles fail Hamiltonicity
  - first failure: `revisited vertex idx=0 at step=3`

## F3: Wrong odd-construction parameter `A`

- Construction family fixed, but choose `A` that violates gcd condition.
- Evidence command:
  - `python - <<'PY' ... construct_with_a(m=9, A=0) ... verify_decomposition ... PY`
- Result:
  - `cycle 0 failed: revisited vertex idx=0 at step=243`
- Control:
  - same command with `m=9, A=2` gives `ok=True`.

## F4: Applying odd-family template to even `m`

- Construction: same rule pattern with `m=6, A=0` (outside theorem scope).
- Evidence command:
  - `python - <<'PY' ... construct_with_a(m=6, A=0) ... verify_decomposition ... PY`
- Result:
  - `cycle 0 failed: revisited vertex idx=0 at step=72`

## Open Lemmas / Conjectures

## E1 (General even-`m` construction)

Find a closed-form construction that works for all even `m >= 4`.
Current status in this repo:

- computational existence evidence for sampled values via CP-SAT:
  - `m in {4,6,8,10,12}` all solved and verified
  - artifacts in `artifacts/solutions/` and summary in
    `artifacts/validation/cpsat_small_m_summary.json`
- no proven general formula yet.

## E2 (Scalable proof strategy for even `m`)

Need a theorem-level argument (not just search) that certifies:

- each cycle Hamiltonian (`m^3`),
- cycles arc-disjoint,
- full arc cover.

No such argument is currently established for all even `m`.

