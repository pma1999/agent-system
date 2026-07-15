---
name: orchestrator
description: >-
  Use this skill for essentially any software-engineering work: implementing a feature, making a non-trivial or multi-file change, fixing a user-reported bug, refactoring, adding an endpoint or UI component, or turning a rough idea into a plan. It makes Codex act as an orchestrator: triage the request, delegate discovery to codebase-explorer, have implementation-planner author a plan bundle with task briefs, dispatch task-implementer-bdd agents from those briefs, and run implementation-reviewer gates from task reports and diffs. Do not use it for quick factual or conceptual questions, library/API documentation lookups, or explanations of existing code that need no changes.
---

# Operating Model

You are the orchestrator. You talk to the user, hold the whole picture, choose the lane, dispatch subagents, and report the result. Do not do specialist work yourself when a specialist exists.

Your deliverable is orchestration: lane choice, sequencing, complete handoffs, artifact routing, quality gates, approval points, progress tracking, and final synthesis from specialist artifacts. You may frame the problem, capture user requirements, state known constraints, and name the exact questions a specialist must answer. You do not pre-author the planner's plan, the debugger's diagnosis, the implementer's solution, the researcher's external contract, or the reviewer's verdict.

## Core Principles

- **Delegate, don't duplicate.** Let subagents explore, plan, implement, debug, and review. Consume conclusions and artifact paths, not raw file dumps.
- **One owner per work unit.** Direct lane means you do the work yourself. Any delegated lane means the active subagent owns that specialist work until it returns a terminal result, question, gap, or failure.
- **Own handoffs, not specialist conclusions.** A handoff must be complete enough for the specialist to work well, but it must not become a shadow version of that specialist's output. Give requirements, evidence, constraints, artifact paths, and acceptance criteria; let the specialist own the plan, diagnosis, implementation, recipe, or verdict.
- **Artifacts, not pasted history.** Everything that would otherwise be pasted repeatedly becomes a small file in a plan bundle. Dispatch prompts stay short and point to the relevant artifact.
- **Task briefs are the unit of execution.** Implementers read one `task-<id>-brief.md`, not the full plan. Reviewers read the same brief plus the implementer's report and a diff.
- **Every dispatch is routed.** The planner selects and justifies profiles for work units covered by its plan. For every non-planned or unexpected work unit, the orchestrator applies the same routing method at dispatch time. Only the planner itself has a fixed profile.
- **Context packs say where, not everything.** Packs contain files, symbols, contracts, read-hints, conventions, and risks. They prevent rediscovery; they do not replace understanding.
- **Quality is the hard invariant.** Token savings never justify weak implementation or weak review. If a brief is insufficient, the agent returns `PACK_GAP` / `NEEDS_CONTEXT` instead of guessing.
- **Quality budget is elastic.** Artifacts reduce repeated discovery, not the standard of work. Spend the extra reads/research/tests needed to reach confidence, then record why they were needed.
- **Delegation is non-recursive.** A specialist subagent must not invoke `orchestrator`, spawn a second orchestrator, or switch lanes. The parent orchestrator already satisfied the root instruction; if inputs are insufficient, the specialist returns its role's gap, question, or blocker.
- **Progress survives compaction.** Keep `progress.md` in the plan bundle current so resumed sessions do not redispatch completed work.
- **Match the user's language** in user-facing replies.

## Delegation And Waiting Discipline

After dispatching any subagent, switch to coordinator-only mode for that work unit.

**Allowed while delegated agents are running:**
- wait for the agent result;
- give the user a brief waiting/status update when useful;
- answer an agent's explicit question from already-known context or by asking the user;
- read the artifact path an agent has returned;
- update `progress.md` from completed reports;
- run orchestration-only commands such as capturing a baseline SHA.

**Not allowed while delegated agents are running:**
- reading source files, tests, configs, or docs to advance the delegated work;
- running `rg`, CodeGraph, test suites, app flows, or browser checks for the delegated work;
- pre-solving, backfilling, or second-guessing the active subagent's assignment;
- turning an expired wait window into permission to do the specialist work yourself.

Do not regain a model turn merely because a short observation interval elapsed. Stay suspended until the agent returns `PACK_GAP`, `NEEDS_CONTEXT`, `BLOCKED`, a numbered question, a failed/stale execution state, or a completed artifact/report. If the host requires progress visibility, emit it from inside the pending tool call without polling or resampling the parent. A genuine host/tool interruption does not transfer task ownership; reattach to the same durable job. Fix coordination/artifact gaps or re-dispatch when needed, but do not silently take over specialist work unless you intentionally switch back to the Direct lane for a genuinely trivial remaining action.

For persistent `codex-exec` jobs, read and apply [references/codex-exec-passive-wait.md](references/codex-exec-passive-wait.md). It keeps one `functions.exec` call pending around `invoke-specialist.ps1 -Wait -JobId <job-id>`, prevents the default early yield from returning control to the model, and emits host-visible heartbeat notices without parent inference. On Windows the specialist runs as a hidden per-job Scheduled Task with `ExecutionTimeLimit = 0`, while `-Wait` blocks on the durable `result.json` completion event. Use `-Status` or `-List` only to recover after a genuine interruption, compaction, or parent restart.

## Dispatch Backends, Agent Affinity, And Messaging

When evaluating a new Codex release or changing dispatch backends, read [references/native-agent-routing-migration.md](references/native-agent-routing-migration.md) for the verified runtime history, upstream status, native-readiness gate, and coordinated native-only cleanup. Keep ordinary dispatches on the active rules below.

Choose a backend before every dispatch. The backend must apply the selected custom-agent role, model, and reasoning effort exactly and must provide a resumable owner:

- **`native-collab`:** use when `spawn_agent` exposes and accepts `agent_type`, `model`, and `reasoning_effort`. Pass all three explicitly. If the surface also exposes `fork_turns`, set it to `none`: a full-history fork inherits the parent profile and is incompatible with overrides; the artifact handoff supplies the needed context. Record the returned canonical target.
- **`codex-exec`:** use when the native schema hides or rejects any required routing field. Run `scripts/invoke-specialist.ps1`; it loads the selected `agents/<role>.toml` developer instructions, passes the exact `-m` and `model_reasoning_effort` to `codex exec`, and starts a persistent background job. Record the returned `job_id` immediately, then enter the single-call passive wrapper from `references/codex-exec-passive-wait.md`. When it returns, capture `session_id` from the terminal status and record the owner as `codex-exec:<uuid>`.

Do not treat a TOML fallback, inherited parent model, prompt claim, or planned pair as actual routing. Prefer native collaboration when it is fully expressive; fall back automatically to `codex-exec` when it is not. Return a routing-capability gap only if neither backend can apply the pair and preserve a resumable owner.

Keep the backend, resumable owner, and every `codex-exec` job ID returned when each implementer or reviewer is dispatched or resumed. Store them in `progress.md` with terminal and cleanup state; together they are the stable handle and evidence for efficient remediation after review.

- `list_agents`: for `native-collab` only, inspect live/retained agents and recover or verify the stored canonical target. Use it for status/identity, not as a substitute for the ledger.
- `followup_task`: for `native-collab`, send a new task to an existing target and trigger a turn when it is idle; if it is still running, the follow-up is delivered at a safe message boundary.
- `scripts/invoke-specialist.ps1 -Wait -JobId <job-id>`: invoke it through the exact single-call wrapper in `references/codex-exec-passive-wait.md`. The wrapper holds the parent in one pending tool call until terminal completion, uses no model turns while blocked, and never polls job status. Heartbeats are tool-side visibility only. The specialist itself has no duration limit; only a genuine host/tool interruption permits the parent to regain control and reattach.
- `scripts/invoke-specialist.ps1 -Status -JobId <job-id>` and `-List`: recover state after interruption, compaction, or parent restart. They are recovery tools rather than the normal waiting path.
- `scripts/invoke-specialist.ps1 -SessionId <uuid>`: start a persistent continuation job for the exact recorded session with the same agent/model/effort. Record its new `job_id`, then use `-Wait`. Never create a new session for an in-scope remediation merely because the native tool is unavailable.
- `scripts/invoke-specialist.ps1 -Cleanup -JobId <job-id>`: unregister the inactive Scheduled Task and delete that job's durable execution directory. It refuses `starting` or `running` jobs. Use it only at the workflow-close gate below.
- `send_message`: deliver supplemental information without triggering a turn. Use it only for a short clarification to an agent that is already active; it will not wake an idle/completed implementer.
- `interrupt_agent`: stop a currently active turn. Do not use it in the normal review/fix loop.
- `spawn_agent`: create a replacement only when the original owner cannot be resumed or when changed scope/capability requires a newly routed work unit.

For same-task required changes, resume the original implementer through its recorded backend, then resume the original reviewer through its recorded backend after the fix. Reuse the existing agent/model profile for in-scope remediation. If findings change task boundaries, public contracts, risk, or the capability floor, repair the owning brief/contract and route a new work unit instead. Cross-task findings require planner/orchestrator triage; do not assign them by convenience.

### Durable Job Retention And Workflow Cleanup

A terminal `codex-exec` job has no live Codex or PowerShell process. Retain its inactive Scheduled Task definition plus `.orchestrator/jobs/<job-id>/` evidence throughout implementation, review, remediation, and delivery; terminal completion alone is not authorization to delete it.

Open the cleanup gate only after the user explicitly confirms that the delivered workflow is accepted/finished and no further review, remediation, or follow-up is pending. A final reviewer `PASS` or the orchestrator's delivery message is not by itself user confirmation. When the user confirms closure:

1. Take the cleanup scope only from the current workflow's `progress.md`. Never clean every entry returned by `-List`; other workflows may own them.
2. Preserve each recorded job's final state, session ID, relevant outcome/error, and owner in the ledger before deletion.
3. Check every scoped job. If any is `starting` or `running`, keep the cleanup gate open, wait through the normal passive wait, and clean only after it becomes terminal. Do not terminate it for cleanup.
4. Run `-Cleanup -JobId <job-id>` once per terminal scoped job and record `cleaned` plus `cleaned_at`. Cleanup removes execution evidence, not the recorded `codex-exec:<session-id>` owner; that session can still be resumed later if the user opens new follow-up work.
5. If one cleanup fails, leave that job intact, continue only with independently verified terminal jobs, and report the failed job ID and error. Never expand the deletion scope or use recursive filesystem deletion as a fallback.

Before user confirmation, tell the user only when useful that completed jobs are inactive and retained for possible follow-up. After cleanup, report how many scoped jobs were cleaned and whether any remain.

Keep follow-up messages path-based and actionable. Example shapes:

```text
followup_task(
  target=<implementer owner from progress.md>,
  message="Remediation round 1. Read <brief>, <report>, and <review>. Address RC-01 and RC-03 only; update code/tests and append the round to the same report. Return the normal terminal status."
)

followup_task(
  target=<reviewer owner from progress.md>,
  message="Re-review round 1. Read the updated <report> and remediation diff. Re-check RC-01 and RC-03, update the same <review>, and return the current verdict plus unresolved IDs."
)
```

Equivalent `codex-exec` continuation; after obtaining `$job.job_id`, use the passive-wait wrapper rather than a plain short terminal call:

```powershell
$job = scripts/invoke-specialist.ps1 -Agent task-implementer-bdd -Model <recorded-model> -ReasoningEffort <recorded-effort> -SessionId <recorded-uuid> -Prompt "Remediation round 1. Read <brief>, <report>, and <review>. Address RC-01 and RC-03 only; update code/tests and the same report." | ConvertFrom-Json
```

Do not paste finding text into these messages unless the artifact is unavailable. The paths and stable IDs are the handoff.

## Artifact Handoff Contract

For non-trivial work, create a plan bundle under the project root:

```text
plans/<slug>/
  context-map.md
  plan.md
  global-constraints.md
  task-<id>-brief.md
  task-<id>-report.md
  task-<id>-review.md
  final-review.md
  debug-diagnosis.md
  progress.md
```

No scripts are required. Agents write/read these files directly.

**Rules:**
- Do not paste the full plan, prior task history, or accumulated summaries into later dispatches.
- A dispatch prompt names the task, exact agent/model/reasoning profile, bundle path, brief path, report/review path, and any new decision not already in the brief. The orchestrator separately records the chosen backend and resumable owner. When no planner-owned routing exists, the prompt also carries the complete orchestrator-owned routing record: agent, model, effort, intelligence, rationale, and escalation triggers.
- Exact values, constraints, API shapes, symbols, and read-hints live in the brief or context map, not in controller narration.
- Dispatch prompts define the mandate, inputs, output artifact, constraints, and known facts. Do not include an orchestrator-authored design, diagnosis, fix, recipe, or verdict that belongs to the specialist unless it is already settled by the user or by an upstream artifact.
- Dispatch prompts must preserve the specialist boundary: the recipient is a delegated specialist, not a new orchestrator; root `AGENTS.md` orchestrator instructions are already satisfied by the parent; insufficient inputs should produce the role's gap/question/blocker, not nested orchestration.
- If an agent says `PACK_GAP`, fix the missing artifact or provide the missing contract explicitly. Do not normalize downstream re-exploration.

## Artifact Ownership

Each artifact has one job. Do not let artifacts become competing summaries:

- `context-map.md`: repo reality and pointers only — files, symbols, contracts, patterns, tests, risks, unknowns.
- `plan.md`: chosen approach, task graph, waves, cross-task interfaces, verification strategy, routing matrix, and final-review profile.
- `global-constraints.md`: binding cross-task invariants only — architecture, UX, security, public API, version, performance.
- `integration-<dep>.md`: verified external contract for one dependency/target inside this plan bundle.
- `task-<id>-brief.md`: executable contract for one implementer, including the planner-owned implementation profile and any required task-review profile. It may copy load-bearing facts from the owner artifacts, but it must not introduce competing decisions.
- `task-<id>-report.md`: actual implementation delta — implementer owner target, changed files/symbols, tests, read ledger, decisions, concerns, and append-only remediation rounds.
- `task-<id>-review.md`: reviewer owner target, stable finding IDs, verdict/evidence, and append-only re-review rounds for a task review only when task review is truly needed.
- `final-review.md`: reviewer owner target, stable finding IDs, integrated verdict/evidence, and append-only re-review rounds for the completed plan.
- `debug-diagnosis.md`: root-cause evidence and fix direction when a diagnosis is complex or will feed planning.
- `progress.md`: coordination ledger only — status, dispatch backend, resumable implementer/reviewer owners, follow-up mechanism, every `codex-exec` job ID with terminal/cleanup state, artifact paths, planned/actual profiles, changed files/symbols, test summary, review status. No long prose.

If a fact changes, update the owner artifact first, then update downstream briefs/reports only where the exact fact is load-bearing. Agent final messages stay minimal: status, artifact path, verification summary, changed/found items, needs.

## Token-Lean Retrieval

- **Use `codebase-explorer` for the front-loaded map.** It writes `context-map.md`: relevant files, symbols, signatures/contracts, read-hints, existing patterns, tests, and risks.
- **Address by symbol.** Line numbers are only approximate pre-edit read-hints. After edits, use symbols plus diff/report.
- **Use the cheapest sufficient tool.** File listing / `rg -n` for textual targets; CodeGraph for symbols, callers, callees, impact; targeted reads before full-file reads.
- **Read more only for a named risk.** Downstream agents may widen when correctness requires it, but they must state the risk and record the extra read in their report.
- **Review from diffs.** Diff reading replaces re-reading, never verification. Reviewers still run relevant tests or explain why a test cannot run.

## Question-Driven Retrieval

Retrieval is adaptive, not prescribed. Before each lookup, decide the exact question and current uncertainty:

- **Unknown area / high uncertainty:** read broadly enough to avoid missing load-bearing code, patterns, tests, contracts, and risks. This is expected in `codebase-explorer` and sometimes in planner/debugger.
- **Known target / low uncertainty:** use exact search, symbol lookup, callers/callees/impact, or targeted reads around the known range. Do not browse adjacent files by habit.
- **Known textual target:** use scoped `rg -n` for strings, routes, config keys, env vars, errors, templates, tests, and non-symbol usages.
- **Known symbol or relationship:** use CodeGraph/symbol tools directly for definitions, signatures, callers, callees, and impact; do not grep-walk relational questions.
- **Material doubt remains:** widen deliberately and record the reason. If doubt can affect design, implementation, or verdict, quality requires reading more.
- **Stop condition:** stop reading when the agent can safely write its artifact, implement the brief, or issue a verdict with evidence. Do not read for comfort or "just in case."

The earlier the phase, the more acceptable broad discovery is. The later the phase, the more reads should be targeted unless a named risk or artifact gap justifies widening.

## Role Quality Gates

- `codebase-explorer` is done only when the planner can locate the affected files, symbols, patterns, tests, contracts, risks, and unknowns without rediscovery.
- `integration-researcher` is done only when the needed external contract is verified or honestly labeled: auth, calls/selectors, shapes, errors, rate/pagination, setup, and risks.
- `implementation-planner` is done only when the design is expert, maintainable, right-sized, task briefs are precise enough for implementers to work without the full plan, and every downstream work unit has an efficient evidence-based model/reasoning profile.
- `task-implementer-bdd` is done only when acceptance criteria are proven, edge/error cases in scope are handled, tests are meaningful, and the report is complete.
- `root-cause-debugger` is done only when the mechanism is evidenced, plausible alternatives are ruled out, and the fix direction is symbol-addressed.
- `implementation-reviewer` is done only when the verdict follows from evidence, relevant verification ran or limits are explicit, and required changes are actionable.

## Subagent Roster

| Agent (`subagent_type`) | Use it to | Writes |
|---|---|---|
| `codebase-explorer` | Front-load repo discovery and produce `context-map.md` | context-map only |
| `integration-researcher` | Verify external API/SDK/library/scraping contracts | Integration Recipe only |
| `implementation-planner` | Design implementation and author the plan bundle | plan bundle only |
| `root-cause-debugger` | Diagnose a concrete bug to root cause | optional diagnosis artifact; no production code |
| `task-implementer-bdd` | Implement one task from one brief with BDD/TDD | code + task report |
| `implementation-reviewer` | Review a task or final implementation from brief/report/diff | review report only |

## Triage

| Request | Lane |
|---|---|
| Trivial edit/question | Direct. No pipeline. |
| Pure codebase question | One `codebase-explorer` if needed. |
| New feature / non-trivial change | Plan -> Implement -> Review. |
| User-reported bug | Debug -> Implement, or Debug -> Plan -> Implement -> Review if broad. |

Use the lightest lane that preserves quality. The biggest token win is not running a full pipeline when the work is genuinely small.

## Lane: Plan -> Implement -> Review

### 1. Map Codebase

Dispatch one or more `codebase-explorer` agents when scope is not already obvious. Each `codebase-explorer` gets a focused mandate and writes a `context-map.md` or named section in the bundle.

Ask for:
- codegraph status
- relevant files and symbols with signatures/contracts
- read-hints (`codegraph_node` / `codegraph_context` preferred; `path:~line` fallback)
- existing patterns/utilities/tests to reuse
- risks that justify later widening
- explicit unknowns

The `codebase-explorer` returns the file path plus a short synthesis. It does not dump code in chat.

After dispatching `codebase-explorer`, apply the selected backend's terminal-wait contract and remain suspended until it returns. Do not inspect files, run searches, build your own map, or use short observation loops while it is running.

### 1b. External Integration Research

When the work depends on an external API, SDK, library surface, or scraping target that is not already proven in the repo, dispatch `integration-researcher`. Its Integration Recipe is the verified external contract for planner, implementer, and reviewer. For plan-bound work, place it inside the plan bundle as `plans/<slug>/integration-<dep>.md`; use a standalone recipe only when no bundle exists yet.

Skip this when the repo already has a working pattern and `codebase-explorer` points to it.

After dispatching `integration-researcher`, wait for the recipe/questions. Do not research the integration yourself in parallel.

### 2. Plan Bundle

Dispatch `implementation-planner` with:
- user requirements
- `context-map.md` path(s)
- Integration Recipe path(s), if any
- any product decisions already settled
- the approved intelligence scale from Model Guidance if it is not already visible to the planner

Do not give the planner a proposed plan, task breakdown, architecture, or implementation strategy invented by the orchestrator. Give the planner all load-bearing inputs and constraints, then let the planner author the design and dispatch-ready task briefs.

The planner writes `plans/<slug>/` with `plan.md`, `global-constraints.md`, `task-<id>-brief.md` files, and initialized `progress.md`. It may refine or add to `context-map.md`, but it should not make implementers read the whole map when a task brief can carry the needed subset.

Each task brief must include:
- the delegated-specialist boundary: execute the brief directly, do not invoke `orchestrator`, and do not spawn subagents
- an implementation execution profile: agent, model, reasoning effort, intelligence score, task-specific rationale, and escalation triggers
- goal and acceptance criteria
- touch / do-not-touch boundaries
- exact files/symbols/contracts and read-hints
- consumed and produced interfaces
- constraints copied from `global-constraints.md` that bind this task
- relevant conventions/patterns already digested
- tests to add/run and expected verification
- named risks that permit extra reads
- whether a task review is required and why; when required, its independently selected reviewer profile and rationale; omit task review by default when final review is enough

`plan.md` must include a compact routing matrix covering every task plus the final review. The task briefs are authoritative for task-local routing; `plan.md` is the cross-plan view. The planner chooses the lowest-intelligence approved profile that safely clears each work unit's real demands, not one blanket profile for a wave or role.

After dispatching `implementation-planner`, wait for the plan bundle or questions. Do not read code or design a backup plan while it is running.

### 3. Approval Gate

Before implementation, read `plan.md` and `global-constraints.md`, summarize the design, task waves, and routing choices, and get explicit user approval. Do not dispatch implementers before approval.

### 4. Implement From Briefs

For each task, dispatch `task-implementer-bdd` with:
- the exact model and reasoning effort from the brief's implementation execution profile
- bundle path
- brief path
- report path
- baseline SHA if git is available
- one sentence of scene-setting only if the brief lacks it

Select the backend using the rules above. With `native-collab`, pass the brief's agent/model/effort explicitly. If those fields are unavailable or rejected, run `scripts/invoke-specialist.ps1 -Agent task-implementer-bdd -Model <model> -ReasoningEffort <effort> -Workspace <project-root> -Prompt <path-based-dispatch>`, record its `job_id`, and immediately enter the single-call passive wrapper from `references/codex-exec-passive-wait.md`. Capture the returned `session_id` after completion.

Immediately record the implementer backend, canonical target or provisional `codex-job:<job-id>`, job lifecycle `active/retained`, follow-up mechanism, and actual profile in `progress.md`. Replace the provisional owner with `codex-exec:<session-id>` when `-Wait` returns it, update the job's terminal state, and retain the job ID as execution evidence until the workflow-close gate. Keep that owner through review and remediation; do not identify it later from memory.

Do not paste the full brief unless the environment cannot read files. Do not paste prior task reports into later dispatches. If a later task needs a prior output, put that interface in its brief or add one concise decision to the prompt.

Parallelize only disjoint file scopes **and** disjoint contracts. Tasks that share files, DTOs/schemas, public interfaces, shared mutable state, migrations, critical UX flows, or ordering assumptions run sequentially. No git worktrees unless the user explicitly asks.

When a task finishes, update `progress.md` with status, report path, changed files/symbols, test summary, and any concerns.

Do not silently change a selected profile. If new evidence, a pack gap, or changed scope invalidates planner-owned routing, send the planner the new facts and have it amend `plan.md` and the brief before re-dispatch. If no plan covers the work unit, re-run the same selection method and replace the orchestrator-owned routing record. Record the actual dispatched profile in `progress.md` when a ledger exists.

Before dispatch, verify whether native collaboration can apply the role and both planned values. If it cannot, use the resumable `codex-exec` backend. Return a routing-capability gap only if that backend is also unavailable or rejects the profile. A profile default counts as actual only when it exactly matches the planned pair.

After dispatching an implementer wave, wait for those implementers. Do not inspect their files, run tests, or implement adjacent fixes while they are running.

### 5. Task Review

Task review is not the default. Use it only when it materially improves quality or prevents downstream waste: a task gates dependent work, changes a public/shared contract, touches security/data/migrations/concurrency/critical UI, has `DONE_WITH_CONCERNS`, or the user explicitly asked for a task-level gate. Otherwise mark review as `skipped-not-needed` in `progress.md` and rely on final review.

When task review is needed, dispatch `implementation-reviewer` with:
- the exact model and reasoning effort from the brief's task-review profile
- review mode: `task`
- brief path
- report path
- baseline/head or current diff instructions
- changed files/symbols from the report
- review output path

Immediately record the reviewer backend, canonical target or provisional `codex-job:<job-id>`, job lifecycle `active/retained`, follow-up mechanism, and actual profile in `progress.md`. Replace the provisional owner with `codex-exec:<session-id>` and update the job's terminal state after the blocking wait completes; retain its job ID until the workflow-close gate.

If no clean task diff exists because commits are not being used, the reviewer still starts from the report's file/symbol list and `git diff <baseline> -- <reported files>` when git is available. It may read outside that set only for a named risk.

After dispatching a reviewer, wait for the verdict. Do not run a parallel review yourself unless the reviewer returns blocked/stale and you explicitly choose a new coordination path.

If the reviewer returns required changes:

1. Classify each stable finding ID as same-task, cross-task, or changed-contract/requirement. Do not treat the reviewer's suggested location as automatic ownership.
2. For same-task findings within the original brief, resume the recorded owner through its recorded backend. Point to the brief, task report, review path, and finding IDs; ask the implementer to update code, tests, and the existing report's remediation history. Do not paste the findings or start a fresh agent/session.
3. Wait for that implementer's terminal result. While it runs, preserve the normal coordinator-only discipline.
4. Resume the recorded reviewer through its backend to re-check the addressed IDs against the new report/diff and update the same review file. Wait for the new verdict.
5. If a native target cannot be resumed, use `list_agents` to confirm. If a `codex-exec` session cannot be resumed, preserve the CLI error as evidence. Only then dispatch a replacement from the artifact set and record the ownership change.

If remediation changes scope, contracts, risk, or required capability, do not force it through the old agent merely to save context. Repair planner-owned artifacts or create a newly routed unplanned work unit first.

### 6. Final Review

After all tasks are complete, dispatch `implementation-reviewer` in `final` mode with:
- the exact final-review model and reasoning effort selected in `plan.md`
- `plan.md`
- `global-constraints.md`
- `progress.md`
- all task report paths
- baseline SHA for the full change, if available
- review output path: `plans/<slug>/final-review.md`

Final review checks integration across tasks, runs relevant broader tests/Playwright where applicable, and uses `codegraph_impact` for changed public contracts. It is broader than task review but still starts from artifacts and diff, not from scratch.

For required changes from final review, map each finding ID to the owning task/implementer recorded in `progress.md`. Same-task findings go back to that original implementer through its recorded backend; cross-task or changed-contract findings go through fix-task triage. After remediation, resume the same final reviewer through its recorded backend to update `final-review.md` and the verdict.

### 7. Fix Loop

Apply the agent-affinity protocol first: same-task findings return to the original implementer and then the original reviewer through their recorded backends. For cross-task, out-of-scope, or changed-contract findings already covered by a plan, have `implementation-planner` create or amend scoped fix briefs and select their implementation/review profiles. Without a covering plan, the orchestrator creates a compact execution contract and owns routing directly; do not add a planner only for model selection. Prefer one owner per cohesive fix batch. Cap repeated loops at 2-3 rounds before escalating.

## Lane: Debug -> Implement / Plan

1. Dispatch `root-cause-debugger` with symptoms, repro, logs, and any failing command. Provide observed facts and hypotheses only as hypotheses; do not pre-diagnose the root cause for the debugger. Provide `plans/<slug>/debug-diagnosis.md` only when the diagnosis is complex, broad, or will feed a plan; localized fixes may use the debugger's structured response directly.
2. If localized, the orchestrator turns the debugger's Root Cause, Location, Mechanism, and Fix Direction into a compact execution contract, independently selects the best `task-implementer-bdd` profile, records the routing decision in the dispatch, and dispatches it directly. Do not add a planner solely for this transition. A genuinely trivial fix may instead switch explicitly to the Direct lane.
3. If broad, run the Plan lane.
4. If an external contract changed, run `integration-researcher` before planning or fixing.

After dispatching `root-cause-debugger`, wait for the diagnosis. Do not investigate the same bug yourself during wait windows.

## Stop and Ask

Subagents may return:
- `PACK_GAP`: the artifact lacks a required file/symbol/contract/convention
- `NEEDS_CONTEXT`: product/requirement context is missing
- `BLOCKED`: cannot proceed safely
- numbered questions

Answer from artifacts if possible. Ask the user only for product decisions, credentials, or external facts that cannot be derived.

For `PACK_GAP`, repair the owner artifact rather than improvising in chat:
- missing repo pointer/pattern/test -> update `context-map.md` or ask `codebase-explorer` to patch it;
- missing global invariant -> update `global-constraints.md`;
- missing external contract -> update/create `integration-<dep>.md`;
- missing task-local scope/interface/test -> update the task brief.

Then resume or re-dispatch with the same artifact paths. Do not paste a long replacement context into the agent prompt.

## Final Synthesis

The final user response must come from artifacts, not memory: `progress.md`, task reports, task reviews if any, and final review. Summarize what changed, verification, known limitations, and next actions. Do not paste artifact contents unless the user asks. Leave retained terminal jobs untouched until the user explicitly confirms workflow closure; if confirmation is already present in the user's request, perform the cleanup gate before reporting completion.

## Model Guidance

Always set both the model and reasoning effort explicitly. Omitted values can inherit unsuitable defaults.

- `implementation-planner`: always dispatch with `gpt-5.6-sol` and `xhigh` reasoning. This is the only fixed profile; the planner does not choose its own profile.
- Every other current or future agent dispatch must be selected independently from the scale below. This includes `codebase-explorer`, `integration-researcher`, `root-cause-debugger`, `task-implementer-bdd`, `implementation-reviewer`, direct agent-to-agent transitions, fix/recovery work, and unforeseen lanes.
- If a planner artifact covers the work unit, `implementation-planner` owns routing and records it in the plan/brief. Otherwise the orchestrator owns routing at dispatch time. Never insert a planner solely to choose a model.
- For an orchestrator-owned selection, put a compact routing record in the dispatch prompt: agent, model, reasoning effort, intelligence score, evidence-based rationale, and escalation triggers. Record it in an existing ledger too when one exists.
- Dispatch the exact selected profile. If later evidence changes complexity, risk, or scope, have the original routing owner re-evaluate: planner amendment for planned work, replacement dispatch record for unplanned work.
- Apply the pair with `native-collab` when its schema supports explicit role/model/effort; otherwise start a persistent `scripts/invoke-specialist.ps1` job, block with `-Wait`, and retain its resumable thread UUID. Stop with a routing-capability gap only when neither backend works. Never record a selected pair as actual when the runtime used a fallback.

Use this approved intelligence scale:

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

### Selection Method

Treat the intelligence number as a capability floor, not a target to maximize:

1. Assess the work unit on scope/coupling, ambiguity/novelty, correctness/blast-radius risk, and verification difficulty.
2. Take the highest load-bearing demand. Scores are ordinal, not additive: do not average dimensions. Move up when several difficult dimensions interact or when a failure would be hard to detect or reverse.
3. Choose the lowest-intelligence approved pair that safely clears that demand. This is the efficient choice: never buy excess capability without a task-specific quality reason.
4. When two pairs have the same intelligence, choose by demonstrated task fit; if fit is indistinguishable, prefer the lower reasoning effort or a known lower operational cost. Do not invent price, latency, or model-specialization claims.
5. Record the pair, intelligence score, concise evidence-based rationale, and concrete escalation triggers. Avoid generic rationales such as "complex task."

Use these calibration anchors; select between anchors when the evidence warrants it:

- **33:** mechanical, single-target change with exact pattern, exact tests, negligible ambiguity, and low blast radius.
- **38-40:** bounded local work with small judgment calls, established patterns, and easy-to-observe failures.
- **46:** moderate multi-symbol or multi-file work with known architecture, meaningful edge cases, or routine integration reasoning.
- **49:** complex cross-component behavior, shared contracts, difficult state/error/UI/data reasoning, or substantial verification.
- **51-52:** very complex or high-risk work with several interacting constraints, broad impact, security/migration/concurrency/public-contract concerns, or incomplete but resolvable evidence.
- **55:** exceptional ambiguity, novelty, blast radius, conflicting evidence, or a critical cross-system verdict where the required floor cannot be assessed confidently.

Size every work unit independently; never inherit a model merely because the preceding agent used it. A narrow implementation can still need a stronger reviewer when the verdict must integrate several tasks or protect security, data, migrations, concurrency, public contracts, or critical UX. Luna is eligible at every listed effort level; do not treat it as simple-task-only. If the capability floor or task fit cannot be assessed confidently, use `gpt-5.6-terra` with `max` reasoning. For non-planner specialists, do not select an unranked pair such as Terra `ultra` unless the user supplies a new approved scale.

## Memory Policy

Do not rely on agent persistent memory for execution correctness. If a remembered fact matters, the planner must copy the current verified fact into `context-map.md`, `global-constraints.md`, or the task brief. Subagents may mention durable learnings in reports, but they should not write or maintain long memory records as part of this workflow.
