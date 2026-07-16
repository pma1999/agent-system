# Codex Delegation — Channel, Profiles, Templates

Read this file before composing any Codex dispatch. Policy (the four sanctioned uses, read/write safety, reconciliation, degradation, caps, engine routing) lives in the skill core; this file owns the mechanics: how to reach Codex, how to route its model/effort, and the exact dispatch templates.

## Channel Mechanics

- Reach Codex only through the `codex:codex-rescue` subagent (Agent tool, main session only; specialists cannot spawn it).
- Never call `codex-companion.mjs` directly (`${CLAUDE_PLUGIN_ROOT}` is unset in the main session) and never invoke `/codex:review` or `/codex:adversarial-review` (user-only commands).
- The rescue agent is a thin forwarder with no repo access: every dispatch prompt must be self-contained — absolute artifact paths, baseline SHA, and the full XML task block. It cannot read briefs for you.
- Always pass `--wait` so Codex stdout returns in the rescue agent's final message. The rescue agent launches the companion job in a detached worker and stays alive blocking on `status --wait` foreground calls until the job ends; it never ends its turn to "wait". Its Agent call therefore runs as long as Codex does (minutes to an hour): run it in the background, continue only non-conflicting orchestration, and verify a run actually terminated before ever re-dispatching.
- Use `--resume` only to continue the immediately preceding Codex run in this repo with zero intervening Codex dispatches, sending only the delta instruction. Otherwise use `--fresh` plus artifact pointers.
- **Patch dependency:** `--agent <name>` injection and `max` effort acceptance come from a local plugin patch that plugin updates wipe. On unknown `--agent`/`max` errors, run `/repatch-codex` first, then re-dispatch.

## Profile Routing (model/effort per dispatch)

Every Codex dispatch carries an explicitly selected `--model`/`--effort` pair from this user-approved intelligence scale:

| Rank | Model / reasoning effort | Intelligence |
|---:|---|---:|
| 1 | `gpt-5.6-terra` / `max` | 55 |
| 2 | `gpt-5.6-luna` / `max` | 52 |
| 3 | `gpt-5.6-terra` / `xhigh` | 51 |
| 4 | `gpt-5.6-luna` / `xhigh` | 49 |
| 5 | `gpt-5.6-terra` / `high` | 49 |
| 6 | `gpt-5.6-luna` / `high` | 46 |
| 7 | `gpt-5.6-terra` / `medium` | 46 |
| 8 | `gpt-5.6-terra` / `low` | 40 |
| 9 | `gpt-5.6-luna` / `medium` | 38 |
| 10 | `gpt-5.6-luna` / `low` | 33 |

Selection method — treat intelligence as a capability floor, not a score to maximize:

1. Assess the work unit on scope/coupling, ambiguity/novelty, correctness/blast-radius risk, and verification difficulty.
2. Take the highest load-bearing demand. Scores are ordinal, not additive: do not average dimensions; move up when several difficult dimensions interact or a failure would be hard to detect or reverse.
3. Choose the lowest-intelligence approved pair that safely clears that demand — excess capability is never bought without a task-specific quality reason.
4. At equal intelligence, choose by task fit, then the lower reasoning effort. Do not invent price, latency, or specialization claims. Luna is eligible at every listed effort; never treat it as simple-task-only.
5. If the floor or fit cannot be assessed confidently, use `gpt-5.6-terra` / `max`.

Calibration anchors: **33** mechanical single-target work, exact pattern and tests; **38-40** bounded local work, small judgment calls; **46** moderate multi-symbol/multi-file work, known architecture, routine integration; **49** complex cross-component behavior, shared contracts, difficult state/error/UI/data reasoning; **51-52** very complex or high-risk work — security/migration/concurrency/public-contract concerns, broad impact; **55** exceptional ambiguity, novelty, blast radius, or an unassessable floor.

Ownership and recording:

- **Planned tasks:** the planner selects the profile in each Codex-assigned brief's `## Implementer` line (`codex — <model>/<effort>; floor <score>: <one-line reason>`). The orchestrator dispatches exactly that pair or overrides with a logged reason.
- **Unplanned work** (adversarial review, second diagnosis, Quick-lane or fix briefs routed to Codex): the orchestrator selects at dispatch time and records `profile: <model>/<effort> (<score>) — <reason>` in `progress.md` (or the quick folder's ledger). Reviews guarding material risk typically need rank ≤3; size independently, never inherit the implementer's profile.
- **Reserved:** `gpt-5.6-sol` is the planner-role model only; never select it for any other dispatch (matches the Codex-native fixed planner profile).
- **Fallback:** a dispatch without flags legally falls through to `~/.codex/config.toml` defaults — log it as `profile: config-default` and treat it as an omission to fix, not a routing decision.
- Planner runtime flags are provenance only: never copy them into briefs, the 50/50 tally, peer-implementer prompts, review, or diagnosis.

## Prompt Composition

Compose per `gpt-5-4-prompting`: one task per run; XML blocks — `<task>`, an output contract, `<claude_external_planning_contract>` for planning, `<grounding_rules>` for review/diagnosis, and `<action_safety>`/`<verification_loop>`/`<completeness_contract>` for write work. Every dispatch states the Codex-side boundary: delegated specialist inside an externally orchestrated workflow; do not apply the `orchestrator` skill; do not spawn subagents.

Templates follow (the prompt handed to the `codex:codex-rescue` Agent). Placeholders in `<...>` are filled by the orchestrator.

## Template: Plan Bundle Author (write-capable, explicit user request only)

Resolve the optional model/effort flags from the user's request:

| Explicit planning request | Runtime flags added |
|---|---|
| No model and no effort | `--model gpt-5.6-sol --effort xhigh` |
| Model only | `--model <requested>`; leave effort unset |
| Effort only | `--effort <requested>`; leave model unset |
| Model and effort | pass both requested values |

These overrides belong only to the planner run. `--agent implementation-planner` injects `~/.codex/agents/implementation-planner.toml` as developer instructions; do not modify that TOML for this Claude-only routing feature — the XML contract below supplies the two-engine routing delta. The Codex planner owns the normal bundle (`plan.md`, `global-constraints.md`, task briefs, initialized `progress.md`); its stdout is only a completion pointer or numbered product questions. Record provenance in `progress.md`: engine `codex`, only flags actually passed, fallback `none`. Product questions, `PACK_GAP`, or `NEEDS_CONTEXT` are not runtime failures — resolve them normally (`--resume` only if this was the immediately preceding Codex run). Runtime failure handling: skill core, Degradation.

```text
--wait --write --fresh --agent implementation-planner <resolved model/effort flags>
Write-capable planning task (only plan-bundle Markdown artifacts are deliverables).
<task>You are acting as the delegated `implementation-planner` inside an externally
orchestrated Claude workflow; your general planner role is injected as developer
instructions. Follow it exactly except for the explicit Claude External Planning Contract
below, which governs implementer assignment and bundle schema for this handoff. Do not
apply the `orchestrator` skill; do not spawn subagents; do not write production code.
Author the dispatch-ready bundle at <abs plans/<slug>/> from user requirements <complete
requirements>, context maps <abs paths>, Integration Recipes <abs paths or None>, settled
product decisions <complete list or None>, and baseline SHA <sha or unavailable>.</task>
<claude_external_planning_contract>
The downstream implementation engines are `task-implementer-bdd` (Claude) and `codex`
(Codex peer implementer). They are equal-rank and equally capable. Assign by mechanical
constraints first: an explicit user engine pin; tasks writing in a parallel wave, UI/frontend
tasks, and briefs with unresolved context -> `task-implementer-bdd`; fix-loop escalation ->
the engine opposite the failed attempt. Balance every remaining task near 50/50 by estimated
effort, never by perceived capability, type, size, or difficulty. Never split one brief.
Codex-assigned briefs must be fully self-contained and must include a `## Implementer`
model/effort profile chosen from the approved scale: `codex — <model>/<effort>; floor
<score>: <one-line reason>` (approved pairs: terra or luna at max/xhigh/high/medium/low;
sol is reserved for the planner role; lowest pair that safely clears the task's demand).

`plan.md` must state tasks/waves, contract independence, cross-task interfaces, verification,
the task/effort split per engine, deviations from 50/50, and whether adversarial-review risk
criteria apply. Every task brief must use an engine-neutral Agent Boundary, include
`## Implementer` with `task-implementer-bdd | codex` plus a one-line routing reason (and the
profile line for codex), and retain the normal acceptance/scope/interfaces/context/tests/
review/risks/report contract. `progress.md` must include compact planning provenance
(engine `codex`, only model/effort flags actually passed, fallback `none`), a `Baseline:`
line, an Implementer column, an Owner column, and an implementation tally:
`codex 0 | task-implementer-bdd 0 (completed tasks; keep near 50/50 by effort)`.
Planner model/effort is provenance only and must never influence task assignment or appear
in implementer dispatch requirements.</claude_external_planning_contract>
<action_safety>Write only inside the named plan bundle. No production code, config, commits,
branches, plugin files, or unrelated artifacts.</action_safety>
<completeness_contract>Return numbered product questions only when a genuine product choice
blocks a decision-complete plan. Otherwise write the complete bundle and verify every brief
is executable without the full plan. A partial bundle is not done.</completeness_contract>
<compact_output_contract>Return only: Plan bundle: <path>; Approach: <one line>;
Tasks/waves: <one line>; Key contracts: <one line>; Risks: <one line>. If blocked, return only
numbered questions.</compact_output_contract>
```

## Template: Adversarial Review (read-only)

Profile: orchestrator-selected per Profile Routing (material-risk scope typically rank ≤3; `terra/max` when the floor is unassessable). Persist stdout verbatim to `plans/<slug>/codex-review-<id|final>.md`.

```text
--wait --fresh --model <model> --effort <effort>
Read-only adversarial review. Do not edit any files.
<task>Adversarially review this repository's change from baseline <SHA> to the working tree.
Intent: <one line>. Plan: <abs plan.md>; constraints: <abs global-constraints.md>.
Hunt real defects only: correctness, security, data integrity, migrations, concurrency,
public-contract breaks, critical UX. Do not restyle or invent requirements.</task>
<grounding_rules>Every finding cites file:line from the actual diff/code and a concrete
failure scenario. No speculative or taste findings.</grounding_rules>
<structured_output_contract>Findings ordered by severity (CRITICAL/HIGH/MEDIUM/LOW):
severity, file:line, defect, failure scenario, suggested direction. End with
"FINDINGS: <n>" plus a one-line risk assessment, or "NO MATERIAL FINDINGS".</structured_output_contract>
<default_follow_through_policy>Verify claims in code; do not ask questions; mark residual
uncertainty inline.</default_follow_through_policy>
```

## Template: Second Diagnosis (read-only)

Profile: orchestrator-selected per Profile Routing (typically rank ≤5; escalate for intermittent/concurrency mechanisms). Persist stdout verbatim to `plans/<slug>/codex-diagnosis-<id>.md`.

```text
--wait --fresh --model <model> --effort <effort>
Read-only diagnosis. Do not edit any files.
<task>Independently diagnose this bug. Symptoms/repro: <...>. A prior investigation
stalled; its partial findings are at <abs debug-diagnosis.md | inline Hypotheses Handoff>.
Treat everything there strictly as hypotheses and partial evidence — confirm, refute,
or replace them.</task>
<grounding_rules>Anchor every claim to code paths, logs, or reproduced behavior; label
anything unverified as hypothesis.</grounding_rules>
<verification_loop>Trace to the earliest violated assumption; rule out competing
hypotheses before concluding.</verification_loop>
<structured_output_contract>Return exactly: Root Cause (one sentence); Location
(file -> symbol); Mechanism; Evidence; Trigger Conditions; Confidence (high|medium|low + why);
Fix Direction (symbol-addressed); Disagreements with the prior investigation (or "None").</structured_output_contract>
```

## Template: Peer Implementer (write-capable)

`--agent task-implementer-bdd` makes the runtime resolve `~/.codex/agents/task-implementer-bdd.toml` and inject its `developer_instructions` natively at thread start; no file-read instruction is needed (patch dependency above). `--model`/`--effort` come from the brief's `## Implementer` profile; if the brief lacks one, either have the planner/orchestrator assign it or dispatch flag-free and log `profile: config-default`. The sole-writer rule applies for the whole run.

```text
--wait --write --agent task-implementer-bdd --model <model> --effort <effort>
Write-capable implementation task (explicit --write: code and the report file are deliverables).
<task>You are acting as the delegated implementer `task-implementer-bdd` inside an
externally orchestrated workflow; your role prompt is injected as developer instructions.
Follow it exactly. Do not apply the `orchestrator` skill; do not spawn subagents.
Implement exactly one task: bundle <abs plans/<slug>/>, brief <abs task-<id>-brief.md>,
report <abs task-<id>-report.md>, baseline SHA <sha>.</task>
<action_safety>Touch only the brief's scope. No unrelated refactors, no commits, no
branch or config changes.</action_safety>
<verification_loop>Outside-in BDD/TDD per the role prompt: failing test first, implement,
run the brief's tests; record RED/GREEN in the report.</verification_loop>
<completeness_contract>Writing the report file per the role template is part of done.
If inputs are insufficient, stop with PACK_GAP/NEEDS_CONTEXT in both the report and your
final message instead of guessing.</completeness_contract>
<compact_output_contract>End your final message with exactly: Status: <...>; Report: <path>;
Tests: <one line>; Changed: <files/symbols>; Needs: <only if blocked>.</compact_output_contract>
```

## Recording Codex Dispatches

- `progress.md` records each dispatch: purpose, artifact path, Codex session id from stdout, the `profile:` actually passed (or `config-default`), and any fallback taken. Planning model/effort stays provenance, excluded from the implementation tally.
- The Codex planner writes the normal plan bundle — never create a parallel `codex-plan-*` artifact or treat its stdout as a second opinion; its bundle becomes authoritative only after the normal approval gate.
- The Codex implementer writes the normal `task-<id>-report.md`; the reviewer does not distinguish implementers, by design.
- If the Codex implementer never writes its report: reconstruct the delta from `git diff <baseline>`, allow one `--resume` re-dispatch with the delta instruction "write the report at <path> per your role prompt; change nothing else"; if still missing, the reviewer reviews from the diff alone and records the limitation.
