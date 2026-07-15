# Analysis: Multi-Agent Orchestration System (.claude + .codex)

Date: 2026-07-15. Analyst: Claude (Fable 5) top-level session, working inline per explicit user goal (meta-task on the orchestrator itself; specialist delegation intentionally not used).
Scope: `~/.claude/CLAUDE.md`, `~/.claude/skills/orchestrator/`, `~/.claude/agents/`, `~/.claude/skills/repatch-codex/`, `~/.claude/patches/`, codex plugin (`codex@openai-codex` 1.0.5, patched), `~/.codex/AGENTS.md`, `~/.codex/config.toml`, `~/.codex/agents/`, `~/.codex/skills/orchestrator/` (SKILL + references + scripts), runtime evidence in `~/.codex/.orchestrator/jobs/`.
Out of scope per user instruction: pre-existing improvement efforts (notably the experimental `.agentic/orchestrator` Python controller, schema v2 — its smoke jobs from 2026-07-14 exist in `.orchestrator/jobs/` but nothing in the instruction system references it and its `.codex/orchestrator-*.config.toml` profiles were removed; treated as inert evidence only).

## 1. System map (current)

Two mirrored orchestration stacks share one philosophy and one artifact convention (`plans/<slug>/` bundles in each project):

| Layer | Claude Code side | Codex side |
|---|---|---|
| Root instructions (always loaded) | `CLAUDE.md` (~12.0 KB): orchestrator-first trigger + specialist exemption, frontend rule, 5 paragraphs of orchestration/Codex/artifact/model policy, CodeGraph section, retrieval ladder | `AGENTS.md` (~15 KB): same trigger/exemption, frontend rule, one-owner/waiting policy, Dispatch Backends + Agent Reuse, Multi-Agent Model Routing + intelligence scale, CodeGraph, retrieval ladder, ctx7 |
| Orchestrator skill | `skills/orchestrator/SKILL.md` (41.9 KB, 459 lines): principles, artifact contract/ownership, retrieval, quality gates, roster, **Codex Delegation** (channel, safety, 4 full dispatch templates, routing, reconciliation, degradation), triage, Plan and Debug lanes, Stop-and-Ask, model guidance (Sonnet/Haiku), memory policy | `skills/orchestrator/SKILL.md` (40.4 KB, 422 lines): same skeleton plus waiting discipline, dispatch backends (native-collab vs codex-exec), agent affinity + followup/resume, durable-job retention/cleanup gate, routing matrix + intelligence scale, `references/codex-exec-passive-wait.md`, `references/native-agent-routing-migration.md`, `scripts/invoke-specialist.ps1` + worker |
| Specialists | 6 × `agents/*.md`, all `model: sonnet`, no `tools`/`effort`/enforcement fields | 6 × `agents/*.toml` with model+effort defaults (planner sol/xhigh; others terra/high), `developer_instructions`, nicknames |
| Cross-engine channel | `codex:codex-rescue` plugin subagent (sonnet, Bash-only, skills: codex-cli-runtime + gpt-5-4-prompting) → `codex-companion.mjs task --background` → `status --wait` loop → `result`; local patch adds `--agent <toml>` injection + `max` effort acceptance; `repatch-codex` skill restores the patch after plugin updates | none toward Claude (asymmetric by design) |
| Runtime evidence | plugin cache patched (verified); `.claude/plans/` empty; `.claude` is a git repo | jobs in `.orchestrator/jobs/` are all schema v2 (experimental controller); no runtime evidence for v1 `invoke-specialist.ps1` |

Roles and quality gates (both sides): codebase-explorer → context-map; integration-researcher → Integration Recipe; implementation-planner → plan bundle (plan.md, global-constraints.md, task briefs, progress.md); task-implementer-bdd → code + task report (outside-in BDD/TDD, PACK_GAP/NEEDS_CONTEXT honesty); implementation-reviewer → PASS/FAIL/PWRC from brief+report+diff; root-cause-debugger → evidence-based diagnosis. Claude side adds two-engine implementer routing (task-implementer-bdd vs Codex peer, mechanical constraints then ~50/50 effort balance) and Codex second opinions (criteria-gated adversarial review; automatic second diagnosis).

## 2. Verified environment facts

- **V1 — Claude Code (docs verified via claude-code-guide, code.claude.com):** agent frontmatter supports `name, description, tools (allowlist; omitting Agent blocks spawning subagents), disallowedTools, model (sonnet|opus|haiku|fable|<id>|inherit; default inherit), permissionMode, skills (preload), mcpServers, hooks, maxTurns, memory, effort (low..max), background, isolation: worktree, color, initialPrompt`. Skills support `references`-style progressive disclosure (SKILL.md ≤500 lines; linked files load on demand), `user-invocable`, `disable-model-invocation`, `context: fork`, `effort`, `model`. Runtime: subagents run **in background by default** (v2.1.198+) with completion notifications; **SendMessage resumes a completed subagent with context intact — same session only**; Agent-tool `model` param overrides frontmatter.
- **V2 — Codex:** codex-cli **0.144.4** installed (migration reference researched on 0.144.3, 2026-07-13). `developer_instructions` is a documented **top-level config key** ("Instruction Overrides: Additional user instructions are injected before AGENTS.md") ⇒ `invoke-specialist.ps1`'s `-c developer_instructions=<json> --strict-config` is valid. `config.toml`: model `gpt-5.6-sol`, `model_reasoning_effort = "max"`, `multi_agent = true`, `js_repl = false` (passive-wait wrapper relies on the exec/node_repl surface — one live check listed in the verification plan).
- **V3 — Plugin channel:** codex@openai-codex 1.0.5 with the local patch applied in cache (checked in source). Companion semantics: no `--model/--effort` ⇒ app-server thread uses config defaults ⇒ **every Claude→Codex dispatch today runs Sol/max**. `--agent` injects only `developer_instructions`; it does NOT apply the agent TOML's model/effort.
- **V4 — Cost scale of one Codex specialist run** (job f6a8497e, 2026-07-14): 28.5 min wall, 842K input tokens (92% cached), 3.5K output. Codex dispatches are expensive and slow; profile choice matters.
- **V5 —** `invoke-specialist.ps1` v1 (schema 1) has no surviving runtime evidence (all retained jobs are v2/experimental) ⇒ one smoke run belongs in the implementation verification plan. Static review of the script found no defects: approved-pair validation, sol-reserved-for-planner, Scheduled Task with `ExecutionTimeLimit=0`, atomic JSON writes, FileSystemWatcher wait ordered correctly, cleanup refuses active jobs, 32767-char CreateProcess ceiling check.
- **V6 —** `~/.claude/projects/C--Users-Pablo/memory/` is **empty** (breaks a documented dependency, see D5). `.claude` is a git repository; `.codex` is not.

## 3. Findings

Legend: **D** defect, **I** cross-side inconsistency/drift, **E** efficiency waste, **Q** quality gap. Each carries evidence.

### Defects
- **D1.** `.codex/AGENTS.md:1` points to `C:\Users\PcVIP\.codex\agents\` — a stale path from another machine (current user is `Pablo`). Any literal reader resolves a nonexistent directory.
- **D2.** `.codex/agents/root-cause-debugger.toml` output contract says `Confidence: state why confidence is high` — it **forces a high-confidence claim** and drops the honest `high|medium|low + why` of the Claude twin (`.claude/agents/root-cause-debugger.md:58`). It also lacks the **Hypotheses Handoff** section and any below-high-confidence escalation path. False-confidence risk on the Codex side.
- **D3.** Claude `SKILL.md` defines no `final-review.md`: the artifact tree (lines 30–42) and the Final Review dispatch list (lines 401–407) omit a review output path, so the final verdict lives only in the reviewer's chat message — contradicting "Final Synthesis … must come from artifacts" (line 444). Codex side has `final-review.md` throughout.
- **D4.** Planner-profile contradiction: Claude-side Codex-planning preset is `--model gpt-5.6-sol --effort max` (SKILL.md lines 144–148, repatch live-check), while the Codex-native planner is **fixed at sol/xhigh** (planner TOML, AGENTS.md:42, and `invoke-specialist.ps1:535` which *throws* on sol/max). Same role, two different profiles depending on entry point.
- **D5.** `repatch-codex/SKILL.md:22` routes patch-drift recovery to memory note `codex-plugin-agent-flag-patch` in `~/.claude/projects/C--Users-Pablo/memory/` — **that note does not exist** (directory empty). The recovery path for the load-bearing plugin patch is broken.
- **D6.** Claude `SKILL.md` dispatch mechanics predate current harness behavior: subagents now run **in background by default** with completion notifications, and completed agents can be **resumed via SendMessage** (same session). The skill still frames backgrounding as an exception ("run the Agent call itself in background", line 132), never records agent ids, and re-dispatches fresh agents in the fix loop. Consequences: ambiguity about waiting/parallelism, risk of double-dispatch, and a wasted context-reuse lever.
- **D7.** Role boundaries are prose-only on the Claude side. All six agents omit `tools`/`disallowedTools`, so the reviewer/explorer/debugger/researcher/planner can technically edit production code and **any specialist can spawn subagents** (roster shows "Tools: All tools"). The harness supports enforcement (V1).
- **D8.** Claude agents omit `effort`. Planner and reviewer run at whatever the session effort is; the documented per-agent `effort` field (quality-per-token lever) is unused.

### Cross-side inconsistencies (drift)
- **I1.** Stable finding IDs (`RC-01…`), ownership scope classification, and re-review rounds exist only in the Codex reviewer TOML; the Claude reviewer has none.
- **I2.** `## Remediation History` (append-only rounds) exists only in the Codex implementer TOML; the Claude implementer report has none.
- **I3.** Agent-affinity remediation (same implementer fixes, same reviewer re-reviews, context intact) exists only on the Codex side (`followup_task` / `-SessionId`). The Claude side now has the equivalent primitive (SendMessage) but doesn't use it.
- **I4.** Second-opinion machinery is asymmetric: Claude side has criteria-gated Codex adversarial review + automatic Codex second diagnosis; the Codex side has no analogous stronger-profile second pass at all (compounded by D2).
- **I5.** Routing philosophy split. Codex side: per-work-unit capability-floor routing on a user-approved intelligence scale, planner-owned. Claude side: flat Sonnet for Claude subagents and **config-default Sol/max for every Codex dispatch** (V3) — including mechanical fixes. Same system, opposite philosophies.
- **I6.** `progress.md` schemas diverge beyond what platforms require (simple ledger + engine tally vs backend/owner/jobs/cleanup ledger). No shared core ⇒ cross-engine bundles are not portable.
- **I7.** `final-review.md` exists only on the Codex side (= D3).
- **I8.** Debugger contracts diverge (= D2).
- **I9.** Brief schemas necessarily differ (`## Implementer` engine routing vs `## Implementation Execution Profile` model routing), but shared sections (Agent Boundary, Scope, Interfaces, Context Pack, Tests, Report) have started drifting textually.

### Efficiency waste
- **E1.** Always-loaded duplication. `CLAUDE.md` carries ~4 paragraphs of orchestrator process, Codex four-uses policy, artifact ownership, and model rules that duplicate SKILL.md — paid in **every session and every subagent spawn**. `AGENTS.md` similarly embeds dispatch backends + the full intelligence scale that also live in the Codex SKILL.md. The CodeGraph section and the retrieval ladder overlap ~40% in both root files.
- **E2.** Claude SKILL.md (~42 KB ≈ 10–11K tokens) is loaded whole for every orchestrated task, but ~180 lines (Codex Delegation details + 4 templates) are needed only when Codex is actually dispatched. Skills support on-demand reference files (V1).
- **E3.** Every Claude→Codex dispatch runs Sol/max (V3): peer-implementing a small well-specified brief costs planner-grade capability and ~30 min (V4). The Codex side's own scale would route such work to terra/high or luna-tier.
- **E4.** No middle lane. Triage jumps from "Trivial → Direct" to full Plan→Implement→Review. A single cohesive change (the most common real request) pays explorer+planner+bundle+review overhead or gets under-engineered in Direct.
- **E5.** Claude fix loop re-dispatches fresh reviewer/implementer each round: artifacts re-read, context rebuilt (= I3 cost).
- **E6.** `codex-rescue` runs on sonnet to execute 3 mechanical Bash calls in a loop; haiku suffices (plugin-owned file; patchable). Minor.
- **E7.** Effort not tuned per role (= D8): quality-per-token left on the table for planner/final review.

### Quality gaps
- **Q1.** Final review verdict not persisted (= D3).
- **Q2.** No explicit baseline-SHA capture step on the Claude side: briefs/dispatches reference "baseline SHA if git is available" but nothing instructs capturing/recording it in `progress.md` before wave 1 (Codex side allows it during waits; also implicit).
- **Q3.** Approval gate is unstructured ("get explicit user approval"): no AskUserQuestion usage, and no rule honoring an explicit standing pre-approval from the user (currently forces a redundant round-trip).
- **Q4.** Claude review verdicts have no finding IDs ⇒ fix-loop targeting and re-review verification are prose-matching (= I1).
- **Q5.** Codex debugger cannot honestly report medium/low confidence (= D2).
- **Q6.** Role boundaries unenforced (= D7).
- **Q7.** Patch recovery depends on a missing memory note (= D5).
- **Q8.** SendMessage's **same-session-only** resume limit is documented nowhere in the system; a resumed/compacted-into-new session could try to "resume" dead owners instead of re-dispatching from artifacts. Needs an explicit ownership-recovery rule (Codex side already has one for its backends).

### Non-findings (checked and fine)
- `invoke-specialist.ps1`/worker logic (V5), passive-wait design, durable-job retention + user-confirmed cleanup gate: sound.
- Artifact ownership model, PACK_GAP repair flow, planning-engine invariance, sole-writer rule, reviewer evidence bar, 50/50 engine-balance rationale: sound and worth preserving as-is.
- The `max`-effort patch edit remains needed regardless of D4's resolution (config default is max; users may explicitly request max).
- `gpt-5-4-prompting` naming is stale but plugin-owned; templates already follow its block grammar. Leave to plugin updates.
- CodeGraph guidance, ctx7 rule, memory policy: keep.

## 4. Cost model (why the design focuses where it does)

Recurring context cost per orchestrated feature (approx., before → after targets in design.md):
- Root file (CLAUDE.md/AGENTS.md): loaded 1 (orchestrator) + N (each specialist dispatch) times.
- SKILL.md: 1× per orchestrated session.
- Role prompt: 1× per dispatch (fixed).
- Artifacts: the intended currency — briefs/reports stay small; context-map front-loads discovery once.
The two structural levers with zero quality cost are (a) deduplicating always-loaded text into single owners, and (b) progressive disclosure for Codex machinery. The two behavioral levers are (c) the Quick lane for the most common request size, and (d) affinity resume in the fix loop. Quality levers that cost little: per-role `effort`, tools enforcement, RC-IDs everywhere, final-review artifact, honest confidence + symmetric second opinions.
