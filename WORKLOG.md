# WORKLOG - claudescycles

## 2026-03-05

### Task: Workflow bootstrap
- Plan: Create shared-memory and execution-control docs for autonomous discovery work.
- Commands: Created `AGENTS.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `state/CONTEXT.md`, `PROBLEM.md`, `PROBLEM-1-prompt.md`
- Result: Workflow files created with punchlist and restart templates.
- Decision: Continue with P0-02 (deterministic verifier script).

### Task: P0-02 deterministic verifier implementation
- Plan: Reconstruct missing source modules and implement deterministic decomposition verification (Hamiltonicity + arc partition checks) with a CLI and JSON loader/saver.
- Commands: `python - <<'PY' ... marshal/disassembly on claudescycles/__pycache__/*.pyc and scripts/__pycache__/*.pyc ... PY`
- Commands: `python - <<'PY'\nfrom pathlib import Path\nimport json\nfrom claudescycles.verify import verify_decomposition\nfrom claudescycles.io import save_decomposition, Decomposition\nm=3\nn=m**3\ndirs1=[bytearray([0]*n), bytearray([0]*n), bytearray([0]*n)]\nr1=verify_decomposition(m, dirs1)\ndirs2=[bytearray([0]*n), bytearray([1]*n), bytearray([2]*n)]\nr2=verify_decomposition(m, dirs2)\np=Path('artifacts/smoke/invalid_m3_axes.json')\nsave_decomposition(p, Decomposition(m=m, dirs=dirs2, meta={'kind':'smoke-invalid'}))\nprint('wrote', p)\nprint('r1', r1.error)\nprint('r2', r2.error)\nPY`
- Commands: `python scripts/verify_decomp.py artifacts/smoke/invalid_m3_axes.json --json`
- Result: Added `claudescycles/gm.py`, `claudescycles/io.py`, `claudescycles/verify.py`, `scripts/verify_decomp.py`; verifier correctly rejects invalid cases with explicit diagnostics (arc partition violation and cycle revisit).
- Decision: Mark P0-02 complete and start P1-01 by rebuilding CP-SAT search tooling for small `m` (starting with `m=3`).

### Task: P1/P2 search tooling, construction discovery, and validation artifacts
- Plan: Rebuild CP-SAT solver tooling and odd-`m` constructive generator, then validate both odd and even tracks with machine-readable artifacts.
- Commands: `python scripts/search_cp_sat.py 3 --time-limit-s 60 --seed 0 --out artifacts/solutions/cpsat_m3.json`
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json --json`
- Commands: `python scripts/gen_construction_odd.py 5 --out artifacts/constructions/odd_m5.json && python scripts/verify_decomp.py artifacts/constructions/odd_m5.json --json`
- Commands: `python scripts/validate_construction_odd.py --m-max 101 --out artifacts/validation/odd_construction_validation_m101.json`
- Commands: `python scripts/search_cp_sat.py 4 --time-limit-s 120 --seed 0 --out artifacts/solutions/cpsat_m4.json`
- Commands: `python scripts/search_cp_sat.py 6 --time-limit-s 180 --seed 0 --out artifacts/solutions/cpsat_m6.json`
- Commands: `python scripts/search_cp_sat.py 8 --time-limit-s 300 --seed 0 --out artifacts/solutions/cpsat_m8.json`
- Commands: `python scripts/search_cp_sat.py 10 --time-limit-s 600 --seed 0 --out artifacts/solutions/cpsat_m10.json`
- Commands: `python scripts/search_cp_sat.py 12 --time-limit-s 900 --seed 0 --out artifacts/solutions/cpsat_m12.json`
- Commands: `for m in 7 9 11; do python scripts/gen_construction_odd.py $m --out artifacts/constructions/odd_m${m}.json; done`
- Commands: `for f in artifacts/constructions/odd_m*.json; do python scripts/verify_decomp.py "$f"; done`
- Commands: `python - <<'PY'\nimport json\nfrom pathlib import Path\nfrom claudescycles.io import load_decomposition\nfrom claudescycles.verify import verify_decomposition\nout=Path('artifacts/validation/cpsat_small_m_summary.json')\nout.parent.mkdir(parents=True,exist_ok=True)\nrows=[]\nfor p in sorted(Path('artifacts/solutions').glob('cpsat_m*.json')):\n    d=load_decomposition(p)\n    r=verify_decomposition(d.m,d.dirs)\n    rows.append({'path':str(p),'m':d.m,'ok':r.ok,'error':r.error,'wall_time_s':d.meta.get('wall_time_s'),'branches':d.meta.get('branches'),'conflicts':d.meta.get('conflicts'),'seed':d.meta.get('random_seed')})\npayload={'generator':'inline-summary','all_ok':all(r['ok'] for r in rows),'count':len(rows),'results':rows}\nout.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\\n',encoding='utf-8')\nprint('wrote',out)\nPY`
- Result: Implemented `scripts/search_cp_sat.py`, `claudescycles/constructions.py`, `scripts/gen_construction_odd.py`, and `scripts/validate_construction_odd.py`. Generated verified decomposition artifacts for `m in {3,4,6,8,10,12}` via CP-SAT and `m in {5,7,9,11}` via odd construction. Batch odd validation succeeded for all odd `m=5..101` (`49/49`, `all_ok=true`).
- Decision: Proceed to P3 proof write-up with scoped claim: full constructive proof for odd `m>=5`, computational evidence for sampled even `m`, and unresolved general even-case theorem.

### Task: P3/P4 proof, failure catalog, and final summary
- Plan: Convert discovered odd construction into theorem+lemma proof, record explicit failure modes, and publish current proven/open boundary.
- Commands: `python - <<'PY'\nfrom claudescycles.verify import verify_decomposition\n\ndef construct_with_a(m,a):\n    n=m*m*m\n    dirs=[bytearray(n),bytearray(n),bytearray(n)]\n    majority0_rows=set(range(2,2+a))\n    for i in range(m):\n        for j in range(m):\n            v=(i+j)%m\n            for k in range(m):\n                w=(v+k)%m\n                idx=i*m*m+j*m+k\n                if w==0:\n                    dirs[0][idx]=2\n                    dirs[2][idx]=0 if v==0 else 1\n                    dirs[1][idx]=1 if v==0 else 0\n                elif w==1:\n                    dirs[1][idx]=2\n                    dirs[2][idx]=0 if v==0 else 1\n                    dirs[0][idx]=1 if v==0 else 0\n                else:\n                    dirs[2][idx]=2\n                    if w in majority0_rows:\n                        dirs[0][idx]=1 if v==0 else 0\n                        dirs[1][idx]=0 if v==0 else 1\n                    else:\n                        dirs[1][idx]=1 if v==0 else 0\n                        dirs[0][idx]=0 if v==0 else 1\n    return dirs\n\nfor m,a in [(9,0),(9,2),(6,0)]:\n    r=verify_decomposition(m,construct_with_a(m,a))\n    print({'m':m,'A':a,'ok':r.ok,'error':r.error})\nPY`
- Result: Failure evidence captured for wrong-parameter and even-out-of-scope variants (`(m=9,A=0)` and `(m=6,A=0)` fail; `(m=9,A=2)` passes). Added `proofs/odd_m_construction.md`, `proofs/failure_modes.md`, and `docs/FINAL_SUMMARY.md`.
- Decision: Project now has reproducible code + artifacts + rigorous odd-case theorem and explicit unresolved even-case scope.

### Task: Final reproducibility sanity pass
- Plan: Confirm no syntax regressions and rerun representative verifier/validator commands on generated artifacts.
- Commands: `python -m compileall claudescycles scripts proofs`
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m3.json`
- Commands: `python scripts/verify_decomp.py artifacts/solutions/cpsat_m12.json`
- Commands: `python scripts/verify_decomp.py artifacts/constructions/odd_m11.json`
- Commands: `python scripts/validate_construction_odd.py --m-values 5 7 9 11 --out artifacts/validation/odd_construction_validation_sample.json`
- Result: compile and runtime checks all pass; sample odd batch validation passes and writes machine-readable output.
- Decision: Ready for user review with current strongest result (full odd-case theorem, even-case open).

### Task: Repository packaging for handoff
- Plan: Add root README with usage/status/future directions and prepare a single detailed commit containing all generated code, proofs, and artifacts.
- Commands: `git status -sb`
- Commands: `git add README.md WORKLOG.md docs/IMPLEMENTATION.md docs/FINAL_SUMMARY.md state/CONTEXT.md claudescycles scripts proofs artifacts`
- Commands: `git diff --staged --name-only`
- Result: README added; staged set includes implementation code, proof docs, memory files, and machine-readable artifacts.
- Decision: Commit staged changes with detailed message body for reproducible handoff.
