# Design: Multi-Agent System v2 (.claude + .codex)

Companion to `analysis.md` (findings D/I/E/Q, verified facts V). This document is the buildable specification: target architecture, per-file specs, implementation plan, and verification.

> **STATUS: IMPLEMENTED 2026-07-15** — see `progress.md` for the as-built record, applied decisions (planner preset sol/xhigh; per-brief Codex routing ON; haiku rescue; git init; Edit allowed — denylist is `Agent` only; no Opus escalation), verification evidence, and deferred live checks. Where this spec and progress.md differ, progress.md reflects what was built.

## 0. Design tenets

1. **One philosophy, two runtimes.** Same lanes, artifacts, quality gates, and vocabulary on both sides; only execution mechanics differ (Agent tool/SendMessage vs native-collab/codex-exec). Cross-engine bundle portability is an explicit goal: a `plans/<slug>/` bundle authored on either side must be executable and reviewable on the other.
2. **Single owner for every sentence.** Root files (CLAUDE.md/AGENTS.md) own only what *every* session/agent needs: trigger + specialist exemption, frontend rule, retrieval doctrine. The skill owns orchestration process. Role files own role behavior. No paragraph appears twice.
3. **Progressive disclosure.** SKILL.md core stays lean; heavy, conditionally-needed machinery (Codex delegation templates, backend mechanics) moves to `references/` loaded only when that path is taken (documented pattern, V1).
4. **Enforce in config what is today enforced by prose.** `tools`/`disallowedTools`/`effort`/`model` in agent frontmatter; approved-pair validation already in `invoke-specialist.ps1`.
5. **Affinity by default in remediation.** Same implementer fixes; same reviewer re-reviews; stable RC-IDs; append-only rounds — on both sides (SendMessage / followup_task+resume). Fresh dispatch only when the owner is unrecoverable, with artifacts as the recovery path.
6. **Routing = capability floor, planner-owned.** Engine choice (Claude side) stays mechanical-constraints + ~50/50 balance (unchanged). Profile choice *within* an engine follows the user-approved intelligence scale on both sides: lowest pair that safely clears the work unit's real demand; orchestrator owns routing only for unplanned work.
7. **Quality gates keep their teeth.** Approval gate before implementation, PACK_GAP honesty, evidence-based verdicts, fix-loop caps, verbatim second opinions — all preserved; several strengthened (final-review artifact, baseline SHA, honest confidence).

## 1. Target architecture (what changes, at a glance)

| Area | Now | Target |
|---|---|---|
| CLAUDE.md | 12.0 KB, duplicates skill policy | ~6–7 KB: trigger+exemption, frontend rule, merged CodeGraph+retrieval. Everything orchestration-internal moves to the skill (E1) |
| Claude SKILL.md | 41.9 KB monolith | ~24–26 KB core + `references/codex-delegation.md` (~14 KB, loaded only on Codex dispatch) (E2) |
| Claude agents | model:sonnet only | + `effort`, `tools`/`disallowedTools` enforcement, RC-IDs/remediation ports, `color` (D7, D8, I1, I2) |
| Fix loop (Claude) | fresh dispatches | SendMessage affinity + agent-id ledger + same-session rule + artifact fallback (D6, I3, Q8) |
| Lanes (both) | Direct / full pipeline | + **Quick lane** with hard entry criteria and automatic upgrade (E4) |
| Final review (both) | Codex only persists | `final-review.md` both sides (D3) |
| Codex dispatch profiles from Claude | always Sol/max via config default | planner-assigned per brief from the approved scale; orchestrator-assigned for unplanned; sol reserved for planner (I5, E3) |
| Codex planner preset (Claude channel) | sol/max | **sol/xhigh** (matches TOML/AGENTS.md/script; D4) — open decision #2 |
| AGENTS.md | 15 KB incl. backends+scale | ~8–9 KB: trigger+exemption, frontend, merged CodeGraph+retrieval, ctx7; backends/routing live in the skill only (E1) |
| Codex SKILL.md | complete but asymmetric | + Quick lane, + symmetric second-opinion/second-diagnosis (stronger-profile), debugger parity (I4, D2) |
| Codex debugger TOML | forced high confidence | honest `high|medium|low` + Hypotheses Handoff + escalation (D2) |
| progress.md | two unrelated schemas | shared core columns + per-side extensions; cross-engine portable (I6) |
| Patch/recovery | broken memory pointer | memory note recreated; patcher extended; parity-check script (D5, Q7) |

## 2. Per-file specifications

### 2.1 `~/.claude/CLAUDE.md` (rewrite)

Keep, in this order:
1. **Orchestrator-first trigger + specialist exemption** (paragraph 1 verbatim minus nothing — it binds top-level sessions and tells specialists they're exempt; both audiences load this file).
2. **Frontend/UI skills rule** (paragraph 2 unchanged).
3. **Merged "Code retrieval" section**: fold the CodeGraph table + rules-of-thumb and the retrieval ladder into ONE section (~55% of current combined length). Content: the question→tool table (codegraph vs grep/glob), the 7-rung ladder in compact form, match-by-fit rule, failure-mode fallbacks, cost-gradient paragraph. Remove: duplicated rationale sentences, the "Refines the table above" framing (they become one section).

Move to SKILL.md (delete here): the "orchestrator only orchestrates" paragraph, artifact-handoff paragraph, token-discipline paragraph, model-choice paragraph, Codex four-uses paragraph, artifact-ownership paragraph. These bind only the orchestrator, which always has SKILL.md loaded. (Specialists get their boundary from their own role files — already present as "Specialist Boundary".)

Acceptance: CLAUDE.md ≤ 7 KB; contains zero sentences that also appear in SKILL.md; a specialist reading only CLAUDE.md + its role file still knows (a) it must not invoke `orchestrator`, (b) retrieval doctrine, (c) frontend rule.

### 2.2 `~/.claude/skills/orchestrator/SKILL.md` (v2 core)

Structure (sections in order):
1. **Frontmatter**: unchanged name/description.
2. **Operating Model + Core Principles**: current text, absorbing the paragraphs removed from CLAUDE.md (dedup — keep one canonical phrasing of each rule; several already exist here).
3. **Dispatch Mechanics (NEW — Claude Code runtime contract):**
   - Subagents run in background by default and notify on completion. Launch parallel wave members as parallel Agent calls; use `run_in_background: false` only when the next action depends on the result and nothing else can proceed.
   - Record every dispatched agent's id/name in `progress.md` (`Owner` column) at dispatch time; never reconstruct from memory.
   - **Affinity rule:** while the session is alive, remediation and re-review go to the recorded owner via SendMessage (context intact). SendMessage cannot cross sessions: in a resumed/new session, mark owners `stale` in `progress.md` and dispatch replacements from the artifacts (brief + report + review + diff). Never SendMessage a stale owner.
   - Sole-writer rule restated under background-default framing: never have a Codex write run and any Claude implementer live simultaneously; schedule waves accordingly.
   - **Baseline step:** before wave 1 (and before any Codex write run), capture `git rev-parse HEAD` and record it as `baseline` in `progress.md` (Q2).
   - Approval gate uses AskUserQuestion (plan summary + approve/adjust options). If the user already gave an explicit standing pre-approval in this conversation ("implement without asking"), record that in `progress.md` and skip the redundant round-trip (Q3). Silence is never approval.
4. **Artifact Handoff Contract + Ownership**: as today, plus `final-review.md` added to the tree and to Artifact Ownership ("reviewer owner, stable finding IDs, integrated verdict/evidence, append-only re-review rounds") (D3/I7). progress.md description gains `Owner` + `baseline` fields (see 2.6).
5. **Retrieval**: replace the two current sections (Token-Lean + Question-Driven, ~55 lines) with ~12 lines: pointer to the CLAUDE.md retrieval section (always in context) + the orchestrator-specific deltas only (address by symbol; read-hints are pre-edit approximations; review from diffs replaces re-reading, never verification).
6. **Role Quality Gates + Roster**: keep (compressed roster row for rescue).
7. **Triage (NEW row) + Quick lane:**

   | Request | Lane |
   |---|---|
   | Trivial edit/question | Direct |
   | Pure codebase question | One `codebase-explorer` if needed |
   | **Single cohesive change, bounded scope** | **Quick** |
   | New feature / non-trivial change | Plan → Implement → Review |
   | User-reported bug | Debug → (Quick or Plan) |

   **Quick lane** (E4): entry criteria — ONE cohesive task; touch set confidently known or discoverable with at most one focused explorer pass; no new public contracts, migrations, security surface, or cross-task interfaces; expected ≤ ~3 files. Mechanics: orchestrator writes a single `task-quick-<slug>-brief.md` (same brief schema, no bundle) capturing requirements + pointers + tests — this is a handoff, not a design: the implementer owns design within it; dispatch one implementer (engine per Implementer Routing unplanned rule); verification = implementer's tests + orchestrator running the brief's named checks; task review only per the standard triggers (contract/security/data/UX or DONE_WITH_CONCERNS), else skip. **Upgrade rule:** PACK_GAP, scope growth beyond the criteria, or a second correction round ⇒ stop and enter the Plan lane with a real bundle (the brief and report seed it). Quality floor: identical BDD/TDD + report contract; the lane only removes bundle/planner overhead, never testing or honesty.
8. **Lane: Plan → Implement → Review**: as today with these deltas:
   - Step 2 dispatches planner "model sonnet (agent default)"; remove per-dispatch model litany (frontmatter now owns it).
   - Step 3 approval per Dispatch Mechanics.
   - Step 4: wave scheduling under background-default; record Owner ids; sole-writer restated; keep "no worktrees unless the user explicitly asks" (documented `isolation: worktree` exists but merge semantics — worktrees branch from the default branch, not the working tree — make it a user-opt-in, not a default).
   - Step 5 (task review): unchanged criteria; reviewer dispatch includes review output path always.
   - Step 6 (final review): add `review output path: plans/<slug>/final-review.md`; keep adversarial-review criteria hook.
   - Step 7 (fix loop): **rewritten around affinity + RC-IDs** — classify each RC-id (same-task / cross-task / changed-contract); same-task → SendMessage the owning implementer ("Remediation round n. Read <brief>, <report>, <review>. Address RC-01, RC-03 only; append a remediation round to the same report."); then SendMessage the reviewer for re-review of exactly those IDs updating the same review file; cross-task/changed-contract → planner amends briefs (or orchestrator writes a Quick-style fix brief when no plan covers it); cap 2–3 rounds; stale owners → artifact-based replacement (Q8).
9. **Lane: Debug → Implement/Plan**: unchanged, plus localized fixes route through the Quick lane brief format.
10. **Stop and Ask / Final Synthesis**: unchanged; Final Synthesis now cites `final-review.md`.
11. **Model & Effort Guidance (Claude subagents)** (D8/E7):
    - Always set model explicitly? No longer per-dispatch: agent frontmatter now pins `model` + `effort` (2.4); the orchestrator overrides per-dispatch only downward to `haiku` for truly mechanical briefs, or per an explicit user pin. Table: planner sonnet/xhigh; reviewer sonnet/xhigh; explorer/researcher/implementer/debugger sonnet/high; mechanical-only haiku. Never leave model to inherit (inherit = Fable main-session model). Opus escalation: only if user approves open decision #1, add: "final review or planning of exceptional-risk scope (security/data/migration/public-contract) MAY escalate to opus with a one-line logged reason; never routine."
12. **Codex Delegation (SLIMMED):** keep in core only: the four sanctioned uses; opt-in-planning rule; read/write safety summary (read-only declaration for review/diagnosis; `--write` follows the deliverable; sole-writer); execution model summary (rescue is a self-waiting forwarder; dispatch it as a background Agent call; expect minutes-to-hours; verify termination before re-dispatch); Implementer Routing (engine choice — unchanged content); reconciliation summary (verbatim persistence, verdict ownership, disagreement path); degradation summary (retry once `--fresh`, then role-specific fallback, record in progress.md); hard caps. Then: **"Before composing any Codex dispatch, read `references/codex-delegation.md` and use its templates verbatim."**

Acceptance: core ≤ ~26 KB; no template bodies in core; every rule present exactly once across CLAUDE.md+SKILL.md+references.

### 2.3 `~/.claude/skills/orchestrator/references/codex-delegation.md` (NEW)

Contents (moved + updated, not new policy except where flagged):
1. **Channel mechanics** (from current Channel/Execution Control): rescue-only access, `${CLAUDE_PLUGIN_ROOT}` caveat, self-contained prompts (absolute paths, baseline SHA, full XML block), `--resume` vs `--fresh` semantics, long-run handling under background-default dispatch.
2. **Profile routing for Codex dispatches (CHANGED — I5/E3, open decision #3):** the approved intelligence scale table (terra/luna × effort, scores 55→33) + selection method (verbatim from Codex side, single canonical copy on the Claude side lives here); rules: planner-assigned per brief in `## Implementer` ("codex — terra/high; floor 46: multi-file with routine integration"), orchestrator-assigned for unplanned work with a compact routing record; `gpt-5.6-sol` reserved for the planner role; when the floor is genuinely unassessable → terra/max (scale's own rule); templates gain `--model <model> --effort <effort>` lines populated from the brief. Fallback: a brief without a profile ⇒ flags omitted ⇒ config default (Sol/max) — legal but must be logged as `profile: config-default` in progress.md.
3. **The four templates** (planner / adversarial review / second diagnosis / peer implementer), updated: planner preset `--model gpt-5.6-sol --effort xhigh` (pending open decision #2); peer implementer template gains the routed `--model/--effort`; XML bodies otherwise verbatim from today (they are good), including the Claude External Planning Contract; peer-implementer/planner boundary text unchanged.
4. **Codex Artifacts + Reconciliation detail + Degradation ladder** (moved verbatim from core, minus the summaries kept there).
5. **Patch dependency note**: `--agent`/`max` require the local plugin patch; on unknown-flag errors run `/repatch-codex` first (pointer, not procedure).

### 2.4 `~/.claude/agents/*.md` (six files)

Common changes to all six (D7/D8):
- Frontmatter additions: `effort:` (planner `xhigh`, reviewer `xhigh`, others `high`); `color:` (explorer cyan, researcher yellow, planner blue, implementer green, reviewer purple, debugger orange); tool enforcement via `disallowedTools` (denylist chosen over allowlist so MCP/codegraph/future tools keep working):
  - ALL six roles: `disallowedTools: Agent` only (**user decision 2026-07-15**): non-recursion is the one machine-enforced boundary; `Write` AND `Edit` stay available to every role so artifacts can be created and updated in place without full-file rewrites. The "read-only except own artifacts / no production code" boundary is enforced by the role prompt (as today), not by tool config — hermetic path-scoping via agent hooks considered and rejected, see §3. Keep the prose non-recursion sentence too (it explains *why*).
- Body: no mass rewrite; keep current text with the deltas below.

Role-specific deltas:
- **implementation-reviewer.md** (I1/Q4): add stable finding IDs (`RC-01…`) with `Scope: same-task|cross-task|changed-contract` and `Status: open|resolved|superseded` to Required Changes; add **Re-review mode** ("you may be resumed with a follow-up message after remediation: re-check only the named IDs against the updated report/diff, update the same review file with a Remediation Round, keep IDs stable, verdict current"); add `## Remediation History` to the report template; final-review output path is always provided and written.
- **task-implementer-bdd.md** (I2): add `## Remediation History` (append-only rounds: IDs, delta, RED/GREEN, concerns) + a **Remediation follow-up** section mirroring the Codex TOML (resume semantics via follow-up message; stay in original boundary; PACK_GAP/NEEDS_CONTEXT with finding ID when a fix exceeds the brief).
- **root-cause-debugger.md**: unchanged content (already has honest confidence + Hypotheses Handoff); frontmatter only.
- **codebase-explorer.md / integration-researcher.md**: frontmatter only.
- **implementation-planner.md** (I5): in `### Implementer Assignment`, extend the `codex` branch: "when assigning `codex`, also select its model/reasoning profile from the approved scale in the orchestrator's `references/codex-delegation.md` (compact table reproduced here) and write it into `## Implementer` with the one-line floor rationale; `gpt-5.6-sol` is reserved for planner-role dispatches." progress.md init gains `Owner` column + `baseline` line (2.6).

### 2.5 `~/.codex/` root + skill

- **AGENTS.md (rewrite; D1/E1):** fix the `PcVIP` path (use `$CODEX_HOME\agents\` phrasing — machine-portable). Keep: trigger + explicit-subagent-request sentence + specialist exemption; frontend rule; the one-owner/write-permission/waiting paragraph (paragraph 11) in compact form; artifact-ownership one-liner; merged CodeGraph+retrieval (same merge as CLAUDE.md); ctx7 block. **Move to SKILL.md** (delete here): "Dispatch Backends And Agent Reuse" details, "Multi-Agent Model Routing" + scale + selection method (SKILL.md already carries all of it — pure dedup; the planner TOML keeps its own embedded copy because specialists don't load the skill). Leave a two-line pointer: "Dispatch backends, agent affinity, model routing, and the approved intelligence scale are defined in `skills/orchestrator/SKILL.md`; specialists receive routing in their dispatch."
- **skills/orchestrator/SKILL.md (v2):** keep current content (it is the more evolved side) with: Quick lane added to Triage + a lane section (same criteria/mechanics/upgrade rule as 2.2 §7, with codex-exec/native-collab dispatch and orchestrator-owned routing record); `## Second Opinions (NEW — I4)`: (a) adversarial second review — same criteria list as the Claude side (security/data/migrations/concurrency/public contracts/critical UX, contested or limitation-laden verdict, reviewer recommendation, explicit user request) ⇒ dispatch a second `implementation-reviewer` at an **independent stronger profile** (≥ rank of the first reviewer; terra/max when unassessable) with "confirm or refute findings; hunt real defects only", persist to `plans/<slug>/second-review-final.md`, reconcile like the Claude side (verbatim, no silent drops, contested material risk → user); (b) second diagnosis — when the debugger returns BLOCKED or confidence below high, dispatch a second `root-cause-debugger` at a stronger profile with the Hypotheses Handoff framed strictly as hypotheses, persist to `plans/<slug>/second-diagnosis-<id>.md`, reconcile; cap 1 each, shared fix-loop rounds. Baseline-SHA capture step made explicit (mirrors 2.2). Final Synthesis/cleanup gate unchanged.
- **agents/root-cause-debugger.toml (D2):** restore `Confidence: high | medium | low, with reason`; add the Hypotheses Handoff block (verbatim from the Claude .md, AGENTS.md-adapted); add the BLOCKED/below-high addendum so the orchestrator's second-diagnosis trigger has a signal.
- **agents/implementation-planner.toml:** progress.md template gains the shared-core columns (2.6) while keeping its backend/jobs/cleanup extensions; add the second-review-final.md awareness line in plan.md risks ("state whether second-opinion review criteria apply" — mirrors Claude plan.md bullet).
- **agents/*.toml (all):** sync shared blocks textually with the post-port Claude .md twins (Specialist Boundary, Scope Discipline, Reading Protocol, Quality Bar, report/review schemas incl. RC-IDs and Remediation History — Codex already has these two; the sync direction is mostly Claude←Codex for remediation blocks and Codex←Claude for the debugger fix).
- **scripts / references:** `invoke-specialist.ps1`, worker, `codex-exec-passive-wait.md`, `native-agent-routing-migration.md` unchanged (V2/V5 validate them). Add one line to the migration reference noting current installed version 0.144.4 at last audit.
- **config.toml:** no system changes (top-level Sol/max is user preference for interactive sessions; the `[[skills.config]]` disabled-superpowers noise is harmless).

### 2.6 Shared contracts (both sides; written into both planners + both skills)

- **progress.md core schema (I6):**
  ```markdown
  # Progress: <feature>
  Planning: engine=<claude|codex> | model=<...> | effort=<...> | fallback=<none|route (reason)>
  Baseline: <sha | n/a>
  | Task | Status | Implementer | Owner | Brief | Report | Review | Notes |
  ```
  Claude-side extensions: `Implementer` = engine (`task-implementer-bdd|codex` + codex profile), `Owner` = Agent id / rescue job-session id; tally line (`codex n | task-implementer-bdd m …`). Codex-side extensions: `Owner` = `native-collab:<target>|codex-exec:<uuid>`; extra columns for follow-up mechanism, execution jobs/cleanup, planned/actual profile; Final Review block. Rule: core columns identical and first, extensions appended — either orchestrator can read the other's ledger.
- **Brief schema:** shared sections textually identical (Agent Boundary, Goal, Acceptance Criteria, Scope, Constraints, Interfaces, Context Pack, Patterns, Tests, Task Review, Named Risks, Report Path); engine-specific section: `## Implementer` (Claude side, now incl. codex profile when engine=codex) / `## Implementation Execution Profile` (Codex side). A bundle executed cross-engine uses whichever is present (documented in both planners).
- **Review schema:** identical on both sides after 2.4 (RC-IDs, scopes, statuses, Remediation History). `Reviewer/Agent Owner` header: Codex fills owner target; Claude side omits (orchestrator ledger holds ids).
- **final-review.md:** both sides, same schema as task review with integrated scope.

### 2.7 Tooling & recovery

- **`~/.claude/patches/codex-plugin-agent-patch.mjs`:** update the two doc-edit anchors that mention the planning preset if decision #2 lands on xhigh (usage strings keep `max` in VALID_REASONING_EFFORTS — still required); add one optional non-core edit: `agents/codex-rescue.md` frontmatter `model: sonnet → haiku` (open decision #4; mechanical forwarder, E6).
- **Memory note `codex-plugin-agent-flag-patch` (D5/Q7):** recreate at `~/.claude/projects/C--Users-Pablo/memory/codex-plugin-agent-flag-patch.md` (+ MEMORY.md index line): one file documenting each core edit's *intent* (helper loader; buildThreadParams/buildResumeParams/runAppServerTurn injection points; VALID_REASONING_EFFORTS + error string; buildTaskRequest/handleTask/background/foreground field threading) so anchors can be re-derived after plugin drift. Content source: the patch file's EDITS array (analysis.md V3).
- **`~/.claude/patches/agent-parity-check.mjs` (NEW, ~80 lines):** reads the six .md/.toml pairs, extracts the shared blocks (by heading), normalizes (CLAUDE.md↔AGENTS.md, rg↔Grep phrasing table), and prints per-pair drift. Run manually or via `/repatch-codex`-style skill (`repatch-codex` gains a "run parity check" step). Chosen over full single-source generation: generation adds escaping/build failure modes for marginal benefit; a drift detector preserves file-level authority (analysis §"rejected options").
- **`.codex` versioning:** `git init` in `~/.codex` with a `.gitignore` (`*.sqlite*`, `log/`, `sessions/`, `.tmp/`, `tmp/`, `cache/`, `sandbox*.log`, `history.jsonl`, `auth.json`, `.orchestrator/jobs/`, `agent-memory/`, `memories/`, `vendor_imports/`, state files) so instruction files get the same change safety `.claude` already has.

## 3. Rejected options (considered, deliberately not designed in)

- **Worktree-parallel writers by default** (`isolation: worktree`): worktrees branch from the default branch, not the live tree; merge/rebase burden would land on the orchestrator. Keep "no worktrees unless the user asks". Documented as available.
- **Single-source generation of role files** (.md/.toml from one template): kills drift but adds a build step + TOML-escaping failure modes to a system whose value is plain-text auditability. Parity-check script instead.
- **maxTurns caps on specialists:** hard mid-artifact stops create corrupt handoffs; PACK_GAP honesty + orchestrator monitoring is the right control.
- **Agent-scoped PreToolUse hooks to path-limit writes** (hermetic "artifacts only" enforcement for read-only roles): supported by the harness (agent frontmatter `hooks`, V1), but adds per-agent hook scripts to maintain on Windows and risks false-positive blocks on legitimate scratch writes (researcher probes, debugger scaffolding, scratchpad use). The `disallowedTools` denylist + role-prompt boundary is the chosen balance; revisit only if a real boundary violation is ever observed.
- **Softening the CLAUDE.md orchestrator-first trigger** for trivial asks: predictability wins; the cost is addressed by slimming the skill core instead.
- **`skills:` preloading (e.g., frontend-design) into implementer frontmatter:** pays the full skill cost on every dispatch incl. non-UI; keep on-demand Skill invocation per brief flag.
- **Adopting the experimental `.agentic` v2 controller:** out of scope per user instruction; nothing in this design depends on or conflicts with it (v1 script untouched, schema v1 self-contained).

## 4. Open decisions (user input wanted; defaults chosen so implementation can proceed)

1. **Opus escalation rung for Claude subagents** (currently forbidden by standing rule "Sonnet or Haiku only"). Recommendation: allow, narrowly — final review or planning of exceptional-risk scope, one-line logged reason, never routine. Default if undecided: keep Sonnet/Haiku only (design ships without the escalation sentence).
2. **Codex planner preset on the Claude channel:** unify at `sol/xhigh` (recommended: matches Codex-native fixed profile, the TOML, and invoke-specialist validation; xhigh chosen deliberately on the Codex side) vs keep `sol/max`. Default: sol/xhigh.
3. **Per-brief Codex profile routing from the Claude side** (replaces always-config-default Sol/max). Recommendation: yes (planner-owned, user-approved scale, big cost/latency win, philosophy unification). Default: yes, with `config-default` as the logged fallback when a brief lacks a profile.
4. **Patch `codex-rescue` model to haiku** (plugin file, restored by patcher after updates). Recommendation: yes (mechanical forwarder). Default: yes as optional non-core patch edit.
5. **`.codex` git init** for change safety. Recommendation: yes. Default: yes.

## 5. Implementation plan (for a future orchestrated session; nothing executed yet)

Wave 0 — Safety net
- T0.1 Commit current state of `~/.claude` (repo exists); `git init ~/.codex` + `.gitignore` + initial commit (decision #5).

Wave 1 — Cross-side contract fixes (independent, small)
- T1.1 `.codex/AGENTS.md` PcVIP path fix (D1) — can fold into T3.1.
- T1.2 `.codex/agents/root-cause-debugger.toml`: honest confidence + Hypotheses Handoff + BLOCKED addendum (D2).
- T1.3 Claude reviewer/implementer .md: RC-IDs, Remediation History, re-review/remediation sections (I1/I2).
- T1.4 `final-review.md` into Claude SKILL artifact tree + final-review dispatch + Final Synthesis (D3).
- T1.5 progress.md shared core into both planner role files (I6) + baseline line (Q2).

Wave 2 — Claude side structure
- T2.1 CLAUDE.md rewrite (2.1).
- T2.2 SKILL.md v2 core (2.2) + `references/codex-delegation.md` (2.3) — one task, they're one refactor.
- T2.3 Agent frontmatter enforcement + effort + colors (2.4 common).
- T2.4 planner .md codex-profile assignment (2.4/I5) — depends on T2.2 (reference file exists).

Wave 3 — Codex side structure
- T3.1 AGENTS.md rewrite (2.5).
- T3.2 Codex SKILL.md v2: Quick lane + Second Opinions + baseline step (2.5).
- T3.3 TOML shared-block sync with post-T1.3 texts (parity pass).

Wave 4 — Tooling & recovery
- T4.1 Patcher update (+ optional haiku edit per decision #4) + re-run against cache; memory note recreation + MEMORY.md index (2.7).
- T4.2 `agent-parity-check.mjs` + repatch-codex skill step (2.7).

Wave 5 — Verification (gate for "done")
- T5.1 Static: parity-check clean; `rg` sweeps: no `PcVIP`, no `sol.*max` planner preset remnants (per decision #2), no orphan references (`final-review.md` referenced everywhere it must be; every `references/*.md` linked from its SKILL core); size targets met (CLAUDE.md ≤7 KB, Claude SKILL core ≤26 KB, AGENTS.md ≤9 KB); Codex-side `quick_validate.py` passes on the orchestrator skill.
- T5.2 Claude-side live smoke (toy repo): (a) Quick lane end-to-end — brief → implementer (background) → report → orchestrator verification; (b) fix-loop affinity — reviewer FAIL with RC-01 → SendMessage implementer → SendMessage reviewer re-review → same files updated; (c) enforcement — confirm a reviewer dispatch cannot Edit (expect tool-denied) and a specialist has no Agent tool.
- T5.3 Codex-channel live smoke: `/repatch-codex` verification checks; one rescue dispatch `--agent task-implementer-bdd --model gpt-5.6-luna --effort low` trivial brief in a scratch workspace — validates patch + explicit profile routing end-to-end (decision #3).
- T5.4 Codex-side live smoke: one `invoke-specialist.ps1` start→`-Wait`→result cycle with luna/low echo prompt (fills the V5 evidence gap); confirm passive-wait wrapper runs under current Codex build (js_repl=false question, analysis V2); one second-opinion dry run at terra/high on a toy diff.
- T5.5 Token audit: before/after byte counts recorded in this bundle's progress notes.

Dependency notes: W1 independent of W2/W3 texts except T1.3→T3.3; T2.2 before T2.4; verification last. Each task is one-implementer sized with its own acceptance line above.

## 6. What stays untouched (explicitly)

`invoke-specialist.ps1` + worker + passive-wait + migration reference; plugin scripts (beyond the existing patch mechanism); `rules/context7.md`; `config.toml` semantics; the artifact-ownership model; PACK_GAP repair flow; planning-engine invariance; 50/50 engine balance; sole-writer rule; approval-gate existence; fix-loop caps; memory policy; the four-uses Codex boundary.
