# WORKLOG - claudescycles

## 2026-03-05

### Task: Workflow bootstrap
- Plan: Create shared-memory and execution-control docs for autonomous discovery work.
- Commands: Created `AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`, `PROBLEM.md`, `PROBLEM-1-prompt.md`
- Result: Workflow files created with punchlist and restart templates.
- Decision: Continue with P0-02 (deterministic verifier script).

## 2026-03-06

### Task: Deterministic verifier + odd-construction source rebuild
- Plan: Recreate the missing `claudescycles` source tree from the local repo state, add deterministic JSON I/O and a verifier for arc-partition + Hamiltonicity, then smoke-test the odd-`m` generator through the CLI.
- Commands: `mkdir -p artifacts/solutions artifacts/validation proofs tests`
- Commands: `uv run pytest -q`
- Commands: `python scripts/gen_construction_odd.py 5 --out artifacts/solutions/odd_m/m5.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/odd_m/m5.json`
- Result: Added `claudescycles/{gm,io,verify,constructions}.py`, solver/generator/verifier scripts, and tests. First `pytest` run failed at collection because the repo root was not on `sys.path`; after adding `tests/conftest.py`, `uv run pytest -q` passed with `9 passed in 0.13s`. The generated odd-`m` artifact for `m=5` verified with `arc_partition_ok=true` and all three cycles marked `ok=true`.
- Decision: Mark P0-02 complete and move to P1 search tooling plus broad odd-`m` validation artifacts.

### Task: Small-`m` exact search + broad validation sweep
- Plan: Use the new CP-SAT searcher to produce exact solver artifacts for small cases, then validate the explicit odd family over a broader range and archive machine-readable verifier outputs.
- Commands: `python scripts/search_cp_sat.py 3 --time-limit 60 --out artifacts/solutions/cpsat_m3.json`
- Commands: `python scripts/search_cp_sat.py 4 --time-limit 60 --out artifacts/solutions/cpsat_m4.json`
- Commands: `python scripts/search_cp_sat.py 6 --time-limit 120 --out artifacts/solutions/cpsat_m6.json`
- Commands: `python scripts/search_cp_sat.py 8 --time-limit 180 --out artifacts/solutions/cpsat_m8.json`
- Commands: `python scripts/search_cp_sat.py 10 --time-limit 300 --out artifacts/solutions/cpsat_m10.json`
- Commands: `python scripts/search_cp_sat.py 12 --time-limit 300 --out artifacts/solutions/cpsat_m12.json`
- Commands: `python scripts/search_cp_sat.py 14 --time-limit 900 --out artifacts/solutions/cpsat_m14.json`
- Commands: `python scripts/validate_construction_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_m_validation.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m3.json > artifacts/validation/cpsat_m3.verify.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m4.json > artifacts/validation/cpsat_m4.verify.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m6.json > artifacts/validation/cpsat_m6.verify.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m8.json > artifacts/validation/cpsat_m8.verify.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m10.json > artifacts/validation/cpsat_m10.verify.json`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m12.json > artifacts/validation/cpsat_m12.verify.json`
- Result: Exact solver artifacts verified for `m=3` (`0.013s`), `m=4` (`0.073s`), `m=6` (`1.154s`), `m=8` (`2.896s`), `m=10` (`9.252s`), `m=12` (`2.525s`), and `m=14` (`8.963s`). The odd construction validation sweep passed for all odd `m` from `5` through `31` (`14` values). Machine-readable verifier reports were archived under `artifacts/validation/` for the completed solver artifacts.
- Decision: Mark solver tooling and artifact archival complete. Use the odd family as the proved theorem, keep the even cases as computational evidence only, and treat the still-running `m=16` search as an optional frontier check rather than part of the required baseline.

### Task: Proof packaging + final validation
- Plan: Write the strongest partial theorem with explicit unresolved extensions, add a repo-level summary, validate the return-map formulas used in the proof, and rerun the final test batch.
- Commands: `python scripts/check_return_maps_odd.py --m-min 5 --m-max 31 --out artifacts/validation/odd_return_map_checks.json`
- Commands: `uv run pytest -q`
- Commands: `python scripts/verify_decomp.py --json artifacts/solutions/cpsat_m14.json > artifacts/validation/cpsat_m14.verify.json`
- Commands: `ps -eo pid=,args= | rg 'python scripts/search_cp_sat.py 16 --time-limit 900 --out artifacts/solutions/cpsat_m16.json'`
- Commands: `kill 846548`
- Result: Added `proofs/partial_theorem.md` with theorem/lemmas, failure modes, and unresolved lemmas; added `docs/SUMMARY.md`; checked the odd return-map formulas for all odd `m` in `5..31`; reran the test suite (`9 passed in 0.15s`); and archived the verifier report for `m=14`. The optional `m=16` frontier search was stopped intentionally after it ceased to be necessary for the required deliverable.
- Decision: Mark the current turn complete with a proved odd family, verified solver witnesses for selected even/small cases, and explicit open problems for the unresolved even theory.

### Task: README + commit packaging
- Plan: Add a top-level README that explains the problem, the proved result, the computational evidence, reproduction commands, and the open even-`m` direction; then stage and commit the full tree with an explicit reviewed diff.
- Commands: Created `README.md`
- Result: Added a top-level project summary with status, artifact layout, reproduction commands, proof summary, and future directions aligned with the current proof boundary.
- Decision: Stage explicit paths, review the staged diff, and commit all current work in one detailed commit.
