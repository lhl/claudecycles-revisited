Goal:
1) Review `README.md` and all prior work to understand what has been replicated, what remains open, and what evidence already exists.
2) Implement and attempt to solve the extension agenda in `PROBLEM-3-extension.md` (especially E1: even-`m`), using the available solvers.

Requirements:
- Follow `AGENTS.md` strictly (worklog/memory/checkpoint + commit discipline).
- Before making new claims, re-validate the current baseline with deterministic commands:
  - Re-run the verifier on at least one known-good artifact (e.g. `artifacts/claude_m5.json` or `artifacts/csp_m3.json`).
  - Re-run the `m=3` parity CLI once (`python -m claudescycles.knuth_m3 --out-dir artifacts/knuth_m3`) to ensure the environment matches repo state.
- Start extension work by reading (in this order): `state/CONTEXT.md`, `docs/IMPLEMENTATION.md`, `WORKLOG.md`, `README.md`,
  then `PROBLEM-2-followup.md`, then `PROBLEM-3-extension.md`.
- For E1 (even-`m`):
  - Primary approach: OR-Tools CP-SAT, encoding 3 coupled Hamiltonian cycles; prefer `AddCircuit` over hand-rolled subtour elimination.
  - Secondary approach: Z3 (useful for UNSAT-style evidence / alternative encoding), if needed.
  - Treat `m=4` as the first target. Any candidate must be verified with `claudescycles/verify.py` and saved as JSON.
  - Use symmetry breaking (at minimum: fix the cycle-labeling at vertex `000`) and record all such assumptions in artifacts/logs.
  - Every solver run must record: exact command, solver params (time limit, seed, workers), and outcome (HIT/NO_HIT/UNSAT/timeout).
  - Save machine-readable outputs under `artifacts/` (solution JSONs, verifier JSON outputs, and solver stats/logs if available).
- Also attempt quick “paper-closure” items if they are low-effort:
  - E2a: verify the paper’s symmetry subclaims (e.g. the `136` count under `ijk → jki`) and archive results as JSON.
- If you fail to find `m=4` within a reasonable budget, do not overclaim. Instead:
  - write the strongest partial result you can (e.g. “no hit within X seconds / Y conflicts / Z branches”),
  - record hypotheses and failure modes,
  - propose the smallest next change that could plausibly unblock progress.
- Logging discipline:
  - After each meaningful experiment batch, update `WORKLOG.md` with exact commands + key results.
  - Update punchlist status in `docs/IMPLEMENTATION.md`.
  - Refresh `state/CONTEXT.md` whenever the best-known approach changes.

Success criteria:
- A reproducible, verifier-checked decomposition for `m=4` found via CP-SAT (artifact + verifier `OK`), plus notes on its structure.
- Ideally: verified decompositions for at least one additional even `m` (`m=6` and/or `m=8`).
- Machine-readable symmetry verification output for the `136`/rotation claims (or a clearly scoped “not yet verified” result).
- Durable repo memory reflects the new results (`WORKLOG.md`, `docs/IMPLEMENTATION.md`, `state/CONTEXT.md`), and evidence is archived under `artifacts/`.
