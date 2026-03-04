# WORKLOG - claudescycles

## 2026-03-05

### Task: Workflow bootstrap
- Plan: Create shared-memory and execution-control docs for autonomous discovery work.
- Commands: Created `AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`, `PROBLEM.md`, `PROBLEM-1-prompt.md`
- Result: Workflow files created with punchlist and restart templates.
- Decision: Continue with P0-02 (deterministic verifier script).

### Task: Deterministic verifier (initial)
- Plan: Implement a deterministic verifier for candidate decompositions (Hamiltonicity + arc partition).
- Commands: `python -m py_compile claudescycles/*.py scripts/verify_decomp.py`
- Result: Syntax OK.
- Commands: `python scripts/verify_decomp.py artifacts/examples/trivial_m3_nonham.json`
- Result: Expected FAIL (arc partition OK, each cycle revisits start at step=3 < 27).
- Decision: Verifier appears to catch obvious non-Hamilton decompositions; next build CP-SAT search to find a real PASS instance (m=3).

### Task: CP-SAT search (m=3)
- Plan: Use OR-Tools CP-SAT + `AddCircuit` to find a 3-cycle arc decomposition for `m=3`, then verify with the deterministic verifier.
- Commands: `time -p python scripts/search_cp_sat.py 3 --time-limit-s 60 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m3.json` (OR-Tools 9.15.6755; wall_time_s≈0.013; branches=1743; conflicts=10).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json`
- Result: PASS (3 Hamiltonian cycles, arc partition OK).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json --json > artifacts/solutions/cpsat_m3.verify.json`
- Result: Machine-readable verification report saved.
- Decision: Proceed to solve additional small m (m=4,5,...) and inspect solutions for patterns suitable for a general construction + proof.

### Task: CP-SAT search batch (m=4..8)
- Plan: Generate additional verified decompositions for small m to support pattern discovery.
- Commands: `time -p python scripts/search_cp_sat.py 4 --time-limit-s 300 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m4.json` (wall_time_s≈0.080).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m4.json --json > artifacts/solutions/cpsat_m4.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 5 --time-limit-s 300 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m5.json` (wall_time_s≈0.265).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m5.json --json > artifacts/solutions/cpsat_m5.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 6 --time-limit-s 600 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m6.json` (wall_time_s≈1.289).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m6.json --json > artifacts/solutions/cpsat_m6.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 7 --time-limit-s 1200 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m7.json` (wall_time_s≈9.217).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m7.json --json > artifacts/solutions/cpsat_m7.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 8 --time-limit-s 1800 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m8.json` (wall_time_s≈3.191).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m8.json --json > artifacts/solutions/cpsat_m8.verify.json`
- Result: PASS report saved.
- Decision: Start fitting/synthesizing a general construction from the small-m direction tables; if needed, add solver-side structure constraints to search for more regular solutions.

### Task: Odd-m explicit construction + proof (m>=5)
- Plan: Derive a structured construction in transformed coordinates, implement it, validate broadly, and write a proof.
- Commands: `python scripts/gen_construction_odd.py 5 --overwrite`
- Result: Wrote `artifacts/constructions/odd_m5.json` (verified in-script).
- Commands: `python scripts/gen_construction_odd.py 7 --overwrite`
- Result: Wrote `artifacts/constructions/odd_m7.json` (verified in-script).
- Commands: `python scripts/gen_construction_odd.py 9 --overwrite`
- Result: Wrote `artifacts/constructions/odd_m9.json` (verified in-script).
- Commands: `python scripts/gen_construction_odd.py 11 --overwrite`
- Result: Wrote `artifacts/constructions/odd_m11.json` (verified in-script).
- Commands: `time -p python scripts/validate_construction_odd.py --m-max 101`
- Result: PASS for all odd m in {5,7,...,101}; summary saved to `artifacts/validation/odd_construction_validation.json` (runtime ~7.7s).
- Output: Proof written in `proofs/odd_m_construction.md` (theorem for odd m>=5 + explicit note that m=3 is handled by solver artifact).
- Decision: Odd m case now has a general, proven construction (m>=5) + explicit m=3 example; next focus is even m (search for pattern or partial results + failure-mode catalog).

### Task: CP-SAT evidence for larger even m (10..16)
- Plan: Extend CP-SAT search to larger even m and archive verified solutions as computational evidence.
- Commands: `time -p python scripts/search_cp_sat.py 10 --time-limit-s 3600 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m10.json` (wall_time_s≈10.437).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m10.json --json > artifacts/solutions/cpsat_m10.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 12 --time-limit-s 7200 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m12.json` (wall_time_s≈2.936).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m12.json --json > artifacts/solutions/cpsat_m12.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 14 --time-limit-s 7200 --seed 0 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m14.json` (wall_time_s≈9.889).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m14.json --json > artifacts/solutions/cpsat_m14.verify.json`
- Result: PASS report saved.
- Commands: `time -p python scripts/search_cp_sat.py 16 --time-limit-s 14400 --seed 0 --overwrite`
- Result: Terminated after ~709s without solution (killed to avoid long run).
- Commands: `time -p python scripts/search_cp_sat.py 16 --time-limit-s 1800 --seed 1 --overwrite`
- Result: FOUND; wrote `artifacts/solutions/cpsat_m16.json` (wall_time_s≈36.586).
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m16.json --json > artifacts/solutions/cpsat_m16.verify.json`
- Result: PASS report saved.
- Decision: Evidence supports existence through at least m=16; even-m general construction still not identified.

### Task: Repo README + commit packaging
- Plan: Add a top-level README describing the work/status and commit all deliverables in logical chunks with detailed messages.
- Commands: `git status -sb`
- Commands: `python -m py_compile claudescycles/*.py scripts/verify_decomp.py`
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json`
- Result: Commits created (hash -> subject):
  - `93d00a7` feat: add deterministic verifier and JSON I/O
  - `1074f43` feat: add CP-SAT search tool (OR-Tools AddCircuit)
  - `be4c879` artifacts: add verified CP-SAT solutions (m=3..8,10,12,14,16)
  - `43bd69b` feat: implement explicit odd-m (>=5) decomposition construction
  - `8967ced` artifacts: add odd-m construction outputs + range validation
  - `dc0fd37` proof: odd m>=5 Hamiltonian 3-cycle decomposition
  - `da5e0a0` docs: add README and failure-mode catalog
- Decision: Working state is now cleanly committed; next step is even-m synthesis/proof work.
