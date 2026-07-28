# Claude's Cycles Revisited in the GPT-5.6 Sol Era

**Methodology review and proposed rerun protocol — 2026-07-28**

This document reviews the methodology of `claudescycles-revisited`, not just its mathematical output. It asks what the original GPT-5.2-era experiment actually established, what GPT-5.6 Sol changes, and how a new run should combine stronger models, a better research scheduler, verifier-gated autoloops, and honest result labeling.

It also indexes the full prompts and process records behind the recent mathematical case studies discussed here. Those sources have very different evidentiary status. A public prompt or transcript proves that a workflow occurred; it does not, by itself, prove the theorem claimed in its final answer.

## Verdict

The original harness was a real methodological improvement, but for **research reliability**, not for clean model comparison or open-ended discovery.

It did four things unusually well:

1. built an independent verifier before trusting a construction;
2. preserved exact commands, failures, artifacts, and decisions;
3. survived restarts through durable project memory; and
4. separated finite computational evidence from universal proof obligations.

Those properties made the work auditable months later. They are why this review can reconstruct the initial search, the exact moment the reference paper was accessed, and the later CP-SAT and counting results from checked-in evidence rather than memory.

The experiment nevertheless has two decisive limitations:

- Its clean-room boundary leaked after about 30 minutes when GPT-5.2 found and read `../claude-cycles.pdf`.
- The runs summarized in [COMPARISON.md](COMPARISON.md) were not controlled model evaluations. They differed in tools, interaction, budgets, stopping rules, and expected deliverables. They are useful case studies, but outcome differences cannot be attributed to model capability alone.

GPT-5.6 Sol materially changes the feasible search envelope: official guidance documents stronger long-horizon work, `max` reasoning, programmatic tool use, persisted reasoning, and multi-agent execution. The important methodological upgrade, however, is not “use a much longer prompt” or “tell the model to try harder.” It is to turn the harness into a **research scheduler** that:

- maintains genuinely different approaches;
- records what each failure rules out;
- transfers useful constructions, data, and solvers between approaches;
- searches actively for counterexamples and missing lemmas;
- assigns adversarial reviewers to promising candidates; and
- accepts a result only at its demonstrated evidence level.

The governing principle for a GPT-5.6 rerun should be:

> **Verification capacity must scale with search capacity.** More capable and more numerous agents generate more good ideas, but also more plausible, mutually reinforcing wrong proofs.

## Evidence policy for this review

This document uses the following result-status ladder. “Solved” should be reserved for the highest applicable levels, with the exact level always stated.

| Level | Status | What has actually been established |
|---:|---|---|
| 0 | No result claim | An attempt, hypothesis, failure map, or inconclusive run is recorded without asserting a mathematical result. |
| 1 | Model claim or candidate | A model produced an argument, construction, or counterexample. It may be valuable and fully written, but has not been independently checked. |
| 2 | Reproducible computation | Code or a finite certificate deterministically checks the stated finite instance or range. This does not prove an unbounded theorem. |
| 3 | Independent computational check | A second implementation, verifier, or team reproduces the certificate without relying on the generating path. |
| 4 | Complete formalization | A proof assistant checks the result, including an explicit audit of axioms, admitted lemmas, and trusted computation. |
| 5 | Expert or peer acceptance | Qualified humans have examined and accepted the proof or counterexample. This is social evidence as well as technical evidence. |

These levels are not perfectly linear. A human proof can be accepted before it is formalized, and a formalization can still encode the wrong statement. They are best treated as separate labels that prevent a Level-1 announcement from silently turning into a Level-5 claim.

No audited source in this review establishes the circulating “perfect IMO score” claim for GPT-5.6. The official release instead reports strong science and mathematics evaluations, including **89% on FrontierMath Tier 1–3 v2** and **83% on FrontierMath Tier 4 v2**. Likewise, recent Erdős and conjecture announcements are discussed below at their current verification levels, not repeated as settled results.

## What the original work established

### Reproducible mathematical results

The repository has strong local evidence for the following scoped claims:

- The deterministic verifier rejects an intentionally invalid `m=3` decomposition and accepts known valid ones.
- The Claude/Knuth construction verifies for every odd `m` in `[3,101]` and fails Hamiltonicity for every even `m` in `[4,100]` tested by the same scanner.
- The `m=3` counts `11502`, `1012`, `996`, `4554`, and `760` were reproduced with archived machine-readable outputs.
- CP-SAT produced independently verifier-checked decompositions for `m=4,6,8`.
- The “136” symmetry statement was disambiguated computationally: it is `136` of the `996` generalizable cycles under `ijk -> jki`, while the analogous decomposition count is `92` of `760`.

The relevant commands and artifacts are indexed in [README.md](README.md), [WORKLOG.md](WORKLOG.md), and [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md). The original prompt is preserved in [PROBLEM-1-prompt.md](PROBLEM-1-prompt.md), the later extension prompt in [PROBLEM-4-extension-prompt.md](PROBLEM-4-extension-prompt.md), and raw session evidence under [session-analysis](session-analysis/README.md).

### What the harness got right

| Method | Observable benefit | Remaining boundary |
|---|---|---|
| Verifier first | Candidate construction code had to satisfy a deterministic, problem-specific contract. Invalid and valid fixtures were both preserved. | A verifier can validate only the statement it implements; its own correctness and the universal proof still need independent review. |
| Exact experiment logging | Commands, parameters, outcomes, and keep/revert decisions can be reconstructed months later. | Some early logging happened after a batch rather than as an immutable event stream. |
| Restart-safe memory | `state/CONTEXT.md`, `docs/IMPLEMENTATION.md`, and `WORKLOG.md` prevented the context-loss failure Knuth reported in the original Claude workflow. | Durable memory can also preserve a leak or a mistaken premise. The initial memory explicitly named the hidden paper. |
| Machine-readable artifacts | Counts, solver certificates, scans, and verifier results can be rerun and compared mechanically. | Finite scans do not imply all-`m` correctness, and solver `HIT` does not explain structure. |
| Preserved failures | CSP scaling failures and even-`m` failures were not erased when the direction changed. | The log did not consistently extract a reusable “failure constraint” or state which entire approach class had been eliminated. |
| Claim-integrity rule | The repo usually distinguishes tested ranges, proof sketches, and open cases. | Later comparison prose initially overstated some literature/proof claims and needed an explicit audit. |

This is a substantial success. The harness converted an ephemeral chat into a durable research object.

### What the harness did not do

The original `AGENTS.md` is primarily a disciplined engineering and replication loop. It says how to choose a punchlist item, implement a minimal change, run tests, benchmark, log, and commit. It does not provide a sophisticated scheduler for mathematical conception.

In particular, it did not require:

- a registry of distinct mathematical approach families;
- an explicit statement of the structural reason each approach failed;
- periodic synthesis across surviving artifacts from unrelated failures;
- a novelty or duplication check before allocating another attempt;
- separate construction, counterexample, proof, and proof-audit roles;
- deliberate transfer of a solver or data representation from one approach to another; or
- a stagnation policy based on failure classes rather than merely elapsed attempts.

The unchecked P3 items in [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md)—the hypothesis backlog, iterative even-`m` exploration, and failure catalog—are almost exactly the missing discovery layer.

## The clean-room failure and why it matters

The repository began with a clean-room intention, but not a clean-room environment. Setup memory named `claude-cycles.pdf` as the primary source, and the file remained reachable one directory above the worktree.

The raw session timeline is unambiguous:

| UTC time on 2026-03-04 | Event |
|---|---|
| 19:00:51 | Autonomous phase begins; verifier and CSP search are built. |
| 19:27–19:30 | `m=3` succeeds; larger blind CSP attempts fail within their node budgets. |
| 19:30:58 | The model checks for stronger solver packages; none are installed. |
| 19:31:14 | It searches parent directories for a Claude Cycles PDF. |
| 19:31:24 | It reads `../claude-cycles.pdf`. |
| 19:33:40 | It is compiling the known odd-`m` construction. |

The independent-discovery window was therefore about 30 minutes. The model acted rationally given its visible context; the experiment design was porous.

A future blind run must enforce the evidence boundary outside the prompt:

- mount only the frozen problem workspace;
- prevent traversal above the workspace root;
- remove paper names, citations, and solution-bearing memory from the initial image;
- disable general web access or use a strict allowlist;
- log every opened path and URL; and
- make literature access a separately timed second phase.

Prompt instructions such as “do not read the paper” are not an isolation mechanism. The filesystem and network policy are.

## Why the existing comparison is not a model benchmark

[COMPARISON.md](COMPARISON.md) usefully records GPT-5.2, GPT-5.3-Codex, GPT-5.4, and Claude Opus 4.6 runs, but it should remain labeled an observational comparison.

| Confound | Why causal attribution fails |
|---|---|
| Solver availability | Some runs could use OR-Tools or stronger encodings; the original blind GPT-5.2 window could not. Search power changed independently of the model. |
| User interaction | Runs had different numbers and kinds of follow-up turns. Guidance, requests to continue, and requests for final documentation affect both search and stopping. |
| Budget | Wall time, active time, token use, and tool calls differed by orders of magnitude. A longer run samples more approaches. |
| Stopping rule | Some runs stopped after a partial theorem, some after artifacts, some after a README request, and some after literature access. |
| Deliverable scope | Proof length, code, tests, archived artifacts, and exposition requirements differed. Time spent polishing is not time spent discovering. |
| Prior state | Branch contents, memory files, installed packages, and solution-bearing artifacts were not identical in every comparison. |
| Sampling | Most cells are single runs. Mathematical search has high run-to-run variance, so a single success or failure is weak comparative evidence. |

The fact that GPT-5.4 independently reached the same skew-product odd construction as the 5.2/5.3 branches is interesting evidence about a strong attractor in the problem. It is not, on its own, a measured capability curve.

## The most relevant follow-up: `no-way-labs/residue`

The updated Knuth paper points to [`no-way-labs/residue`](https://github.com/no-way-labs/residue), which is the most directly comparable process experiment. Its [full system prompt](https://github.com/no-way-labs/residue/blob/main/prompt/residue.md) and [orchestration log](https://github.com/no-way-labs/residue/blob/main/logs/meta_log.md) expose mechanisms the original harness lacked.

### Methodological advances in Residue

Residue asks each agent to maintain a **Strategy Register** and to record every substantive attempt with fields for:

- the precise failure constraint;
- what class of approaches the failure rules out;
- surviving structure;
- newly visible reformulations;
- concrete computed artifacts;
- tested parameter ranges; and
- open questions.

It forces synthesis every five explorations, triggers an additional synthesis after three consecutive failures without a new approach class, and detects “grinding” when the strategy register has not changed in five explorations.

The experiment then adds orchestration. Two agents developed complementary styles: a top-down symbolic GPT agent and a bottom-up computational Claude agent. The orchestrator transferred the computational agent's even-`m` tables into the symbolic agent's preferred fiber coordinates, then transferred the former's solver. The symbolic agent adapted that solver using its theory. This is a much more specific multi-agent mechanism than asking several agents to “solve independently and vote.”

| Dimension | Original repo harness | Residue | Recommended GPT-5.6 system |
|---|---|---|---|
| Primary control structure | Engineering punchlist | Exploration log + strategy register | Both: milestone punchlist plus approach graph |
| Failure record | Command, result, decision | Constraint, eliminated class, surviving structure, reformulation, artifact | Residue schema in append-only machine-readable events |
| Synthesis | Human/model discretion | Every five explorations and on stagnation | Triggered by attempt count, stagnation, and newly compatible artifacts |
| Agent diversity | Mostly one main agent per run | Two providers with different emergent styles | Independent lanes with explicit approach-family contracts |
| Cross-agent transfer | Ad hoc | Orchestrator transfers data representations and tools | Logged artifact/tool transfer with source, recipient, rationale, and outcome |
| Verification | Strong repo-local deterministic verifier | Construction verifier and broad scans | Independent verifier lane, proof adversary, and formalization lane |
| Continuity | Memory files | Full exploration logs | Atomic state + append-only log + compact restart capsule |

### Important qualifications

Residue's own paper is appropriately candid about its limits:

- the experiment has only `n=2` solving agents;
- the orchestration record was partly reconstructed rather than written entirely in real time;
- the odd case and Knuth paper were already known, so the setup had partial prior knowledge;
- the even construction is computationally verified over large finite ranges, but its symbolic all-`m` proof remains open; and
- no complete proof-assistant formalization was finished.

As a local reproduction for this review, the released fast verifier was run with:

```bash
cd /tmp/residue/constructions
python3 verify.py --max-m 30 --fast
```

It passed all 28 values `m=3..30` in under one second. Because this reused the project's released verifier rather than an independently written checker, it is Level-2 evidence for the construction over this finite range. It is not a proof of the universal even-`m` claim.

## What GPT-5.6 Sol changes

The current [official model guide](https://developers.openai.com/api/docs/guides/latest-model) says that the `gpt-5.6` alias routes to `gpt-5.6-sol`. Relevant changes include:

- `max` reasoning effort, intended for demanding tasks needing more exploration and verification;
- a separate `pro` execution mode that performs more model work before returning one answer;
- Programmatic Tool Calling for bounded tool-heavy stages;
- persisted reasoning across turns;
- a Responses API multi-agent beta; and
- `ultra`, which coordinates four agents by default in the Codex product.

The [GPT-5.6 launch page](https://openai.com/index/gpt-5-6/) reports FrontierMath Tier 1–3 v2 at 89% and Tier 4 v2 at 83%, along with improvements on long-running agent and tool-use evaluations. These are genuine reasons to rerun the problem, but benchmark gains do not determine how much of the gain will transfer to one open-ended combinatorics task.

### Capability improvement should change the experiment, not the truth standard

| GPT-5.6 capability | Research opportunity | New methodological risk |
|---|---|---|
| More reasoning at `max` | Explore more construction families, test more edge cases, and revisit missing lemmas before stopping. | A longer coherent argument can conceal a deeper flaw and feel more authoritative. |
| Better long-horizon autonomy | Run substantial search/proof cycles with less human steering. | A mistaken premise can persist longer and contaminate more artifacts. |
| Programmatic tool use | Filter, enumerate, deduplicate, and check large candidate sets with fewer round trips. | Tool-generated summaries can drop counterexamples or citations unless their output contract is checked. |
| Persisted reasoning | Preserve assumptions and priorities across turns. | Hidden stale reasoning can survive after the problem representation changes; explicit durable state remains necessary. |
| Multi-agent/`ultra` execution | Develop independent approaches in parallel and reduce wall-clock time. | Agents can be correlated, duplicate one another, or amplify a shared false lemma during synthesis. |
| Greater token efficiency | Afford more independent replicates and more verification per dollar. | Cheap generation can outpace expensive expert or formal review. |

The strongest use of GPT-5.6 is therefore not merely replacing `gpt-5.2` with `gpt-5.6-sol` in the old run. The rerun should separately measure:

1. the **model effect** under the old prompt and harness;
2. the **scheduler effect** under the same GPT-5.6 model;
3. the **parallel-agent effect** under the same scheduler; and
4. the **verification effect** of independent and formal gates.

Without that separation, a successful new run will still be an excellent case study, but not evidence about which intervention caused the improvement.

## Prompting in 2026: lean task prompt, rich mechanical harness

OpenAI's [GPT-5.6 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6) recommends leaner, outcome-focused prompts. It emphasizes stating the goal, relevant context, hard constraints, required evidence, success criteria, output form, autonomy boundaries, and stopping behavior once. The model does not need repeated exhortations to “think hard,” nor does pro mode require a prompt that asks for pro mode.

For mathematical research, this suggests a clean split:

- The **task prompt** defines the theorem, evidence boundary, allowed actions, completion states, and deliverables.
- The **harness** owns attempt IDs, budgets, timers, strategy diversity, logging, compaction, verifier gates, and keep/revert decisions.
- The **verifier** owns executable correctness checks.
- The **review protocol** owns claim labels and blinded adjudication.

Putting every loop rule into one giant prompt consumes context, repeats itself after compaction, and asks the model to police its own evidence. Mechanical requirements should be mechanically enforced.

### Lessons from recent full prompts

#### Cycle Double Cover prompt

OpenAI's [full Cycle Double Cover prompt](https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_prompt.pdf) is best understood as a research-scheduler prompt. It authorizes up to 64 dynamically allocated agents, asks for a portfolio of independent approach families, maintains a registry of tried and blocked routes, assigns adversarial proof agents, defines theorem-strength completion, requires at least eight hours of work, and forbids returning a partial result as the requested final outcome.

The valuable mechanisms are diversity, route accounting, adversarial review, and an exact completion bar. The risky mechanism is outcome pressure. “Do not return a partial result” can discourage calibrated abstention unless the harness separately permits a budget-exhausted, unsolved state. The prompt PDF is strong provenance for the workflow and the proof it contains; this review does not independently certify its theorem claim.

#### Erdős candidate-proof runs

The [public workflow thread](https://threadreaderapp.com/thread/2080003441821163958.html) reports roughly 13 attempts, six candidate successes, and 6–32 hour Codex runs. The complete prompts are preserved in the [`ShouqiaoW/erdos`](https://github.com/ShouqiaoW/erdos) repository for problems [390](https://github.com/ShouqiaoW/erdos/blob/main/390/prompt.md), [486](https://github.com/ShouqiaoW/erdos/blob/main/486/prompt.md), [536](https://github.com/ShouqiaoW/erdos/blob/main/536/prompt.md), [788](https://github.com/ShouqiaoW/erdos/blob/main/788/prompt.md), [1002](https://github.com/ShouqiaoW/erdos/blob/main/1002/prompt.md), and [1038](https://github.com/ShouqiaoW/erdos/blob/main/1038/prompt.md).

As of this review, the corresponding Erdős Problems pages—[390](https://www.erdosproblems.com/390), [486](https://www.erdosproblems.com/486), [536](https://www.erdosproblems.com/536), [788](https://www.erdosproblems.com/788), [1002](https://www.erdosproblems.com/1002), and [1038](https://www.erdosproblems.com/1038)—still label all six problems `OPEN` and warn that submitted proof claims may not have been examined. Problem 536 is described as partial. These should be called **candidate proofs or proof claims**, not six solved Erdős problems, until independent review changes their status.

#### Dinitz–Garg–Goemans counterexample transcript

The [full public ChatGPT conversation](https://chatgpt.com/share/6a60b2eb-0b64-83ee-9c76-7931ca1de063) is especially instructive because the user prompts are short and the search trace is extensive. Its main path contains 94 tool messages and four user prompts:

1. “Construct a counterexample to general (non-planar) case of Dinitz Garg Goemans conjecture. You should do a breakthrough and find a structured counterexample.”
2. “please continue research and find a complete unconditional counterexample”
3. “Continue the search. Have a clear strategy obtained from deeper understanding of the problem structure.”
4. “it's enough of partial results. let's finish with a complete unconditional counterexample”

After each of the first three prompts, the model explicitly reported that it did not yet have a valid unconditional counterexample. After the fourth, it returned a small finite candidate with six source–terminal paths and eight unsplittable routings, designed for exhaustive integer-arithmetic checking.

The methodological lesson is not that refusing partial answers guarantees a theorem. It is that persistent search, active rejection of hybrid-path failures, and eventual reduction to a small exhaustive certificate can turn an initially vague open-problem attack into something independently auditable. The [primary announcement thread](https://threadnavigator.com/thread/2079904005652893709/) and [36Kr summary](https://eu.36kr.com/en/p/3907657849361795) provide context; independent expert acceptance was not established by this review.

#### Reddit prompt diffusion

The supplied [Reddit post](https://www.reddit.com/r/accelerate/comments/1uuqj41/solving_an_open_conjecture_with_gpt_56/) copies a CDC-style prompt into a Hilbert-function problem. The author explicitly disclaims independent verification. It is useful evidence that the portfolio/registry/adversarial-agent pattern is diffusing, not evidence that the conjecture is settled.

## Autoloops: from “keep going” to measured research state

The current [`lhl/pi-multiloop`](https://github.com/lhl/pi-multiloop) implementation is a much better substrate for this rerun than an unconstrained continuation prompt. Its [README](https://github.com/lhl/pi-multiloop/blob/main/README.md), [loop guide](https://github.com/lhl/pi-multiloop/blob/main/skills/multiloop/references/LOOP_GUIDE.md), and [state model](https://github.com/lhl/pi-multiloop/blob/main/docs/STATE.md) document:

- isolated experiment lanes and run tags;
- research, optimize, development, and punchlist modes;
- compound metrics plus mechanical guard and prompt-verifier gates;
- fail-closed behavior when a required verifier verdict is missing;
- append-only JSONL result history;
- atomic resume state;
- explicit keep, revert, and log decisions;
- escalation after repeated failure; and
- compaction-aware continuation and recovery.

For this mathematics project, a lane should be an **approach family**, not merely a different random continuation. Examples include algebraic skew products, SAT/CP-SAT certificate generation, symmetry/quotient constructions, exact-cover formulations, obstruction hunting, and proof formalization. Each lane should emit the same attempt schema so a synthesizer can compare them.

A suitable gated iteration is:

```text
hypothesis -> construct or derive -> run local checks -> adversarially probe
           -> record failure/survivors -> keep, reject, or transfer -> next
```

The compound acceptance gate should require all applicable checks:

1. **Mechanical guard:** formatting, build, schema, and deterministic verifier pass.
2. **Mathematical guard:** stated finite tests, independent counterexample search, and theorem-strength lemma checklist.
3. **Provenance guard:** prompt, model snapshot, tools, budget, opened paths/URLs, and source artifacts recorded.
4. **Claim guard:** final language matches the achieved evidence level.

`pi-multiloop` can make omission fail closed, but it cannot decide whether the verifier encodes the right theorem. That remains the job of an independently written verifier, proof reviewers, and ideally a proof assistant.

### Useful neighboring loop patterns

The [`devstack` autonomous-loop survey](https://github.com/lhl/devstack/blob/main/wiki/concepts/autonomous-loops.md) places this in a broader ecosystem:

| Project | Useful idea for this work | Limitation for theorem research |
|---|---|---|
| [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch) | Simple edit -> benchmark -> keep/revert loop. | Assumes a trustworthy scalar objective; proof quality is not scalar by default. |
| [`davebcn87/pi-autoresearch`](https://github.com/davebcn87/pi-autoresearch) | Polished branch workflow, live state, and confidence-aware measurement. | Primarily optimization-shaped and may want to own the benchmark script. |
| [`lhl/codex-autoresearch`](https://github.com/lhl/codex-autoresearch) | Multiple isolated loops, existing-script integration, guard gates, and escalation. | Lessons and state transfer still need theorem-specific semantics. |
| [`nicobailon/pi-boomerang`](https://github.com/nicobailon/pi-boomerang) | Compact handoffs between long iterations. | Compression can erase a small counterexample or qualification unless artifacts remain external and immutable. |
| [`tintinweb/pi-supervisor`](https://github.com/tintinweb/pi-supervisor) | A separate model checks goal adherence and redirects drift. | A supervisor sharing the same misconception is not independent verification. |
| [`nicobailon/pi-review-loop`](https://github.com/nicobailon/pi-review-loop) | Fresh-context review/fix/re-review until a clean exit. | Self-review improves presentation and catches local issues but does not establish peer acceptance. |

The synthesis for mathematical work is: use autoresearch mechanics for experiments, Residue semantics for failures and reformulations, multi-agent lanes for conception diversity, and a separately owned proof/certificate pipeline for truth.

## Status of the external case studies

This table states the highest evidence independently established **in this review**, not the strongest claim made by each source.

| Case | Public process evidence | Mathematical status used here |
|---|---|---|
| This repo, odd `m` | Full prompts, raw sessions, code, proof notes, scans, Knuth paper, and later Lean project are public. | Finite results independently reproducible; the odd theorem also has expert writeup and a public Lean formalization. |
| This repo, even `m=4,6,8` | CP-SAT solutions, statistics, and independent repo verifier outputs are archived. | Level 2–3 finite certificates. No all-even theorem from these artifacts. |
| Residue | Full prompt, two exploration logs, meta-log, code, and paper source are public. | Its released verifier was reproduced locally for `m=3..30`. Universal even correctness remains computational rather than symbolically proved in its paper. |
| Cycle Double Cover | OpenAI publishes the full multi-agent prompt and resulting proof document. | Level 1 provenance in this review; theorem not independently certified here. |
| Six Erdős announcements | Full prompts and run outputs are public. | Candidate proofs. The problem registry still says `OPEN`; 536 is partial. |
| Dinitz–Garg–Goemans | Full ChatGPT conversation and a small claimed exhaustive certificate are public. | Candidate counterexample, suitable for independent reproduction; peer acceptance not established here. |
| Reddit Hilbert-function post | Copied prompt and narrative are public. | Prompt-diffusion example; author disclaims verification. |

This is why broad statements such as “GPT-5.6 regularly solves Erdős problems and long-standing conjectures” need a denominator and a status label. The stronger supported statement is: **GPT-5.6-era systems are regularly producing serious candidate proofs and small checkable certificates for problems presented as open; some have unusually complete public process records, while independent acceptance often lags the announcement.**

## Proposed controlled GPT-5.6 rerun

### Questions to answer

The rerun should preregister four separate questions:

1. Under the original prompt and environment, does GPT-5.6 outperform the older model on the same blind milestones?
2. Holding GPT-5.6 fixed, does a Residue-style research scheduler improve outcomes over the original punchlist harness?
3. Holding model and scheduler fixed, do multiple independent approach lanes outperform a single lane at the same aggregate budget?
4. How often do stronger search configurations overclaim relative to an independent verifier/reviewer?

### Experimental cells

| Cell | Model | Task prompt | Research scheduler | Purpose |
|---|---|---|---|---|
| A | GPT-5.2 `xhigh`, if still reproducibly available | Original | Original | True historical-control rerun. If unavailable, existing logs are archival context only, not a causal control. |
| B | GPT-5.6 Sol `max` | Original | Original | Isolate the model change as closely as possible. |
| C | GPT-5.6 Sol `max` | Rerun prompt below | Residue + `pi-multiloop`, one solving lane | Measure the scheduler/prompt effect. |
| D | GPT-5.6 Sol `max` | Same as C | Four independent solving lanes plus synthesis and audit through the multi-agent API | Measure parallel search at a fixed aggregate budget without changing the underlying model setting. |

Run three pilot replicates per cell to validate infrastructure, then preregister at least five independent confirmatory replicates for any comparison used to make a capability claim. Do not silently pool pilot and confirmatory runs.

Product `ultra` can be added as a separate operational cell, but it should not be substituted silently for Cell D: that would combine a parallelism change with product-level orchestration differences and weaken the causal comparison.

### Locked run conditions

Each cell must use the same:

- frozen `PROBLEM.md` and problem-only commit;
- container image, CPU/RAM limits, Python and solver versions;
- initial artifact set and hidden verifier suite;
- output contract and mathematical milestones;
- blind filesystem and network policy;
- aggregate eight-hour wall-clock ceiling;
- aggregate token and price-normalized cost ceiling, chosen before the pilot results are inspected; and
- automated stop behavior.

Time, tokens, and cost cannot all be perfectly equalized because parallelism and models have different throughput. Declare one primary resource constraint, cap the other two, and report all three. For the multi-agent cell, token and cost limits are aggregate across every solver, synthesizer, and reviewer agent.

### Two evidence phases

**Phase I: strict blind discovery.** Only the problem statement, generic mathematics libraries, and the frozen toolchain are reachable. No paper title, author name, source PDF, existing solution branch, internet search, or solution-bearing memory is present.

**Phase II: literature-aware extension.** After Phase I artifacts are sealed, expose the archived Knuth papers, this repo's prior results, Residue, and other public work. The objective changes from rediscovery to simplification, proof completion, independent verification, or genuinely new extension. Never combine the two phase scores.

### Research scheduler

Maintain two linked structures:

1. a milestone punchlist for deliverables and verification; and
2. an approach graph whose nodes are hypotheses/representations and whose edges record derivation, contradiction, transfer, or refinement.

Every substantive attempt must emit a machine-readable record containing:

```json
{
  "attempt_id": "lane/run/sequence",
  "approach_family": "short stable label",
  "hypothesis": "falsifiable claim",
  "outcome": "supported|refuted|inconclusive|abandoned",
  "failure_constraint": "specific structural obstruction",
  "rules_out": ["bounded description of affected approach classes"],
  "surviving_artifacts": ["paths or content hashes"],
  "reformulations": ["new representations"],
  "tests": ["exact commands and verdicts"],
  "open_questions": ["next discriminating questions"],
  "claim_level": 0
}
```

The scheduler should synthesize after every five completed attempts, after three consecutive failures without a new approach class, and whenever artifacts from one lane satisfy a stated need in another. A transfer record must identify the source lane, destination lane, artifact/tool, reason, and observed effect.

Parallel lanes should start from deliberately different representations. Agent count is not approach diversity. If two lanes converge on the same premises and construction family, merge or redirect one rather than paying for correlated continuations.

### Adversarial verification roles

Promising candidates should pass through independent roles with fresh context:

- **counterexample hunter:** searches minimal and boundary cases, parity failures, and assumption violations;
- **proof auditor:** converts every “clearly,” “similarly,” and “it follows” into an explicit lemma obligation;
- **statement auditor:** verifies that the proved formal statement is exactly the requested theorem;
- **certificate engineer:** extracts a deterministic checker and compact witness where possible;
- **independent implementer:** writes a second verifier from the problem statement rather than adapting the generator; and
- **formalizer:** encodes the strongest stable theorem in Lean or another proof assistant and audits axioms/admissions.

The generating agent should not own the only verifier.

### Stop and completion rules

The run may end in any of these honest states:

- `PROVED`: complete proof passed independent statement and proof audit;
- `FORMALIZED`: proof assistant check passed with an explicit axiom/admission report;
- `CERTIFIED_RANGE`: deterministic certificates pass for an exact stated range;
- `COUNTEREXAMPLE`: finite certificate independently reproduced;
- `PARTIAL`: useful lemmas/constructions survive, with the missing theorem-strength obligations listed;
- `INCONCLUSIVE`: budget exhausted without a defensible mathematical result; or
- `BLOCKED`: infrastructure or evidence boundary failed, invalidating comparison.

No completion prompt should require the model to claim success. A budget-exhausted negative result with a good failure map is valid experimental data.

### Evaluation

The primary outcome is the highest independently adjudicated result level reached within budget. Secondary measures should include:

- time, tokens, and cost to first valid certificate;
- number of genuinely distinct approach families attempted;
- fraction of failed attempts with reusable failure constraints;
- number and value of cross-lane artifact/tool transfers;
- verifier and proof-audit failure rates;
- calibration: whether final language matches evidence status;
- reproducibility from a fresh checkout; and
- blinded reviewer assessment of novelty, correctness, and exposition.

Reviewers should receive anonymized artifact bundles without model, prompt-cell, or run-label metadata. The hidden verifier should be run only by the evaluation controller, and its failures should be archived rather than fed back selectively.

## Full rerun prompt

The task prompt should remain compact because the run controller and `AGENTS.md`-style harness enforce the mechanics. A proposed prompt for Cells C and D is below.

```text
You are conducting a clean-room mathematical investigation of the problem in
PROBLEM.md.

Outcome
Find the strongest correct result you can about the requested Hamiltonian
decomposition. A complete construction and proof is the target; a finite
certificate, obstruction, or partial theorem is valuable only when its scope
and missing obligations are stated exactly.

Evidence boundary
Use only files and tools exposed in this workspace. Do not infer or search for
hidden references. The controller will open a separate literature-aware phase
after blind artifacts are sealed.

Research method
- Begin with an independently specified deterministic verifier for finite
  candidates and negative fixtures.
- Maintain the experiment harness's approach register and attempt records.
  Record structural failure constraints, surviving artifacts, and useful
  reformulations before starting another substantive attempt.
- Keep approach lanes genuinely different. Transfer a construction, data
  representation, or tool when it answers a documented need in another lane.
- For every promising universal claim, search for counterexamples and list all
  theorem-strength lemmas. Assign a fresh-context adversary to attack it.
- Treat computation over a finite range as evidence for exactly that range,
  never as an all-m proof.

Autonomy
Read and edit in-scope workspace files, run non-destructive local tools, and
continue until a completion state or the controller's budget limit. Do not make
external writes or expand the evidence boundary. You may conclude PARTIAL or
INCONCLUSIVE; never manufacture completion to satisfy the target.

Deliverables
1. Reproducible code, fixtures, commands, and machine-readable artifacts.
2. A proof or scoped theorem note with every unresolved lemma marked.
3. A final status chosen from PROVED, FORMALIZED, CERTIFIED_RANGE,
   COUNTEREXAMPLE, PARTIAL, INCONCLUSIVE, or BLOCKED.
4. A concise report linking each claim to its verifier output, proof obligation,
   or external-review status.
```

For Cell D, the controller—not the task prompt—should assign separate approach lanes, aggregate budgets, synthesis checkpoints, and adversarial roles. This preserves a common task prompt while testing orchestration rather than prompt length.

## Full prompts and primary source index

### This project

- [Original one-shot GPT-5.2 prompt](PROBLEM-1-prompt.md)
- [Extension-run prompt](PROBLEM-4-extension-prompt.md)
- [Blind problem statement](PROBLEM.md)
- [Current execution harness](AGENTS.md)
- [Session-analysis methodology and timeline](session-analysis/README.md)
- [Historical cross-run comparison](COMPARISON.md)
- [Archived 2026-03-02 and 2026-03-16 papers](references/papers/README.md)

### Claude's Cycles follow-up ecosystem

- [Current Knuth paper](https://www-cs-faculty.stanford.edu/~knuth/papers/claude-cycles.pdf)
- [Residue repository](https://github.com/no-way-labs/residue)
- [Residue full prompt](https://github.com/no-way-labs/residue/blob/main/prompt/residue.md)
- [Residue orchestration/process log](https://github.com/no-way-labs/residue/blob/main/logs/meta_log.md)
- [Knuth odd-case Lean 4 formalization](https://github.com/kim-em/KnuthClaudeLean)

### GPT-5.6 and prompting

- [GPT-5.6 official launch page](https://openai.com/index/gpt-5-6/)
- [Official latest-model guide](https://developers.openai.com/api/docs/guides/latest-model)
- [Official GPT-5.6 Sol upgrade guide](https://developers.openai.com/api/docs/guides/upgrading-to-gpt-5p6-sol)
- [Official GPT-5.6 prompt guidance](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6)
- [Cycle Double Cover full prompt and output](https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_prompt.pdf)

### Other mathematical case studies

- [Erdős workflow thread](https://threadreaderapp.com/thread/2080003441821163958.html)
- [Erdős prompt/output repository](https://github.com/ShouqiaoW/erdos)
- Full prompts: [390](https://github.com/ShouqiaoW/erdos/blob/main/390/prompt.md), [486](https://github.com/ShouqiaoW/erdos/blob/main/486/prompt.md), [536](https://github.com/ShouqiaoW/erdos/blob/main/536/prompt.md), [788](https://github.com/ShouqiaoW/erdos/blob/main/788/prompt.md), [1002](https://github.com/ShouqiaoW/erdos/blob/main/1002/prompt.md), [1038](https://github.com/ShouqiaoW/erdos/blob/main/1038/prompt.md)
- [Dinitz–Garg–Goemans full ChatGPT conversation](https://chatgpt.com/share/6a60b2eb-0b64-83ee-9c76-7931ca1de063)
- [DGG primary announcement thread](https://threadnavigator.com/thread/2079904005652893709/)
- [DGG 36Kr secondary report](https://eu.36kr.com/en/p/3907657849361795)
- [Reddit Hilbert-function prompt example](https://www.reddit.com/r/accelerate/comments/1uuqj41/solving_an_open_conjecture_with_gpt_56/)

### Autoloops and orchestration

- [`lhl/pi-multiloop`](https://github.com/lhl/pi-multiloop): [README](https://github.com/lhl/pi-multiloop/blob/main/README.md), [loop guide](https://github.com/lhl/pi-multiloop/blob/main/skills/multiloop/references/LOOP_GUIDE.md), [state model](https://github.com/lhl/pi-multiloop/blob/main/docs/STATE.md)
- [`devstack` autonomous-loop survey](https://github.com/lhl/devstack/blob/main/wiki/concepts/autonomous-loops.md)
- [`karpathy/autoresearch`](https://github.com/karpathy/autoresearch)
- [`davebcn87/pi-autoresearch`](https://github.com/davebcn87/pi-autoresearch)
- [`lhl/codex-autoresearch`](https://github.com/lhl/codex-autoresearch)
- [`nicobailon/pi-boomerang`](https://github.com/nicobailon/pi-boomerang)
- [`tintinweb/pi-supervisor`](https://github.com/tintinweb/pi-supervisor)
- [`nicobailon/pi-review-loop`](https://github.com/nicobailon/pi-review-loop)

## Final assessment

The original project answered its most important process question: disciplined scaffolding can eliminate context loss, documentation drift, and unverifiable handoffs. It also exposed the next bottleneck. Reliability infrastructure does not automatically create mathematical conception, and a punchlist is not a strategy portfolio.

GPT-5.6 makes a serious rerun worthwhile because it can sustain longer reasoning, use tools more efficiently, and coordinate parallel work. Residue and the newer autoloop ecosystem show how to spend that capability: preserve the residue of failures, detect grinding, keep approaches diverse, transfer the right artifact at the right time, and gate every claim.

The best next experiment is therefore not “give GPT-5.6 the old problem and see whether it solves it.” It is a preregistered comparison that cleanly separates model, scheduler, and parallelism effects—and treats a compact executable certificate or formally audited proof as the result, not the confidence of the prose announcing it.
