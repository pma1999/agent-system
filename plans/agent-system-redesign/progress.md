# Progress: agent-system-redesign (v2 implementation)

Implemented: 2026-07-15, inline by the top-level session per explicit user instruction ("por ti solo, sin subagentes") — meta-work on the orchestration system itself.
Decisions applied (user 2026-07-15): Opus escalation NOT added (Sonnet/Haiku rule kept); Codex planning preset unified at **sol/xhigh**; per-brief Codex profile routing ON; codex-rescue → **haiku** (patch edit); git init both repos; **Edit allowed for all roles** — denylist is `Agent` only.

Baselines: `.claude` @ 43425ce, `.codex` @ 606f754 (root commits, pre-change snapshots).

| Task | Status | Deliverable |
|---|---|---|
| T0 safety net | done | git init + .gitignore (whitelist) + baseline commits, both repos |
| T1 CLAUDE.md rewrite | done | 12.0 KB → 4.9 KB; owns trigger/exemption + frontend rule + merged retrieval only |
| T2 Claude SKILL v2 + reference | done | core 41.9 → 32.2 KB (adds Quick lane, Dispatch Mechanics, RC-ID fix loop, final-review.md, baseline, approval); `references/codex-delegation.md` 15.5 KB on-demand (channel, intelligence-scale routing, 4 templates; planner preset sol/xhigh; peer implementer carries --model/--effort) |
| T3 six .claude/agents | done | frontmatter model+effort+color+`disallowedTools: Agent`; reviewer RC-IDs/re-review/remediation-history; implementer remediation follow-up/history; planner codex-profile assignment + shared progress core (Owner, Baseline, tally, final-review line) |
| T4 AGENTS.md rewrite | done | 15 KB → 9.8 KB; PcVIP path fixed ($CODEX_HOME); backends/routing → skill pointer; CODEGRAPH + ctx7 marker blocks preserved verbatim (tool-owned) |
| T5 Codex SKILL v2 | done | Quick lane; Second Opinions (adversarial second review → second-review-final.md; second diagnosis → second-diagnosis-<id>.md); explicit Baseline step; artifact tree/ownership updated; description de-arrowed for validator |
| T6 Codex TOMLs | done | debugger: honest high\|medium\|low + Hypotheses Handoff + BLOCKED addendum; reviewer: RECOMMENDATION: SECOND_OPINION + final-review.md in Modes; planner: shared 8-column progress core + Codex extensions + Baseline + second-review criteria line + baseline input |
| T7 tooling | done | patcher: +haiku rescue edit (applied), preset-wording hint; memory notes `codex-plugin-agent-flag-patch` + `claude-codex-agent-system` + MEMORY.md (repairs broken repatch recovery path); `agent-parity-check.mjs` (fence-aware, sentence-level, normalized); repatch-codex skill updated (3 behaviors + parity step) |
| T8 verification | done | see below |

## Verification evidence

- Patcher run: 32 `already` + 1 `applied` (haiku); Syntax OK, Loader OK (6623 chars), Effort OK.
- `quick_validate.py`: **"Skill is valid!"** on both orchestrator skills (after removing `->` from descriptions — validator rejects angle brackets; found and fixed on both sides).
- Parity baseline (`agent-parity-check.mjs`): 29 flagged lines, **all mapped to intentional divergence**: write-permission sentence + Agent-tool parenthetical (Claude-side design), two-engine/provenance notes (Claude-only), routing-matrix ownership + backend/owner fields + External Dispatch (Codex-only), remediation mechanics wording (SendMessage vs followup_task/resume), RECOMMENDATION token (CODEX_SECOND_OPINION vs SECOND_OPINION). Anything NEW that appears in future runs = real drift.
- Sweeps: `PcVIP` 0 hits in .codex; no `sol/max` planning remnants in the Claude orchestrator skill; `final-review.md` present in Claude SKILL (tree/ownership/dispatch/synthesis), reviewer Modes, planner progress template, and across the Codex side; `references/codex-delegation.md` linked from SKILL core (roster, Codex Delegation, plan step, debug step).
- Sizes: fixed per-session context (CLAUDE.md + Claude SKILL core) 53.9 KB → 37.1 KB (−31%); each subagent spawn additionally saves 7.1 KB of CLAUDE.md; Codex templates (15.5 KB) now load only on Codex dispatch. AGENTS.md 15.0 → 9.8 KB (−34%; 4.3 KB of that is tool-owned marker blocks). Codex SKILL grew 40.4 → 45.6 KB by design (Quick + Second Opinions are new capability).
- `node --check` clean on both patch scripts.

## Deferred / user-runnable (live checks not executable from this session)

The auto-mode classifier denies launching Codex runs from here; these are the printed one-liners, cheap to run manually when convenient:
1. `node "C:\Users\Pablo\.claude\plugins\cache\openai-codex\codex\1.0.5\scripts\codex-companion.mjs" task --agent task-implementer-bdd --model gpt-5.6-luna --effort low "Do not read files or run commands. State your allowed report Status values on one line."` → must echo the five Status values (proves role injection + explicit profile routing end-to-end).
2. Same script `task --agent implementation-planner --model gpt-5.6-sol --effort max "…PLANNER_MAX_READY"` → proves max acceptance (patch), noting the planning preset itself is sol/xhigh.
3. Codex-side: one `invoke-specialist.ps1` start→`-Wait` cycle with luna/low echo prompt (fills the schema-v1 runtime-evidence gap noted in analysis.md V5).
4. First real orchestrated feature after this change doubles as the live smoke for Quick lane + SendMessage affinity.
