# Codex plugin patch — edit intents (recovery doc)

Tracked mirror of the auto-memory note `codex-plugin-agent-flag-patch`, so patch recovery works on every machine this system is installed on. If you update one, update the other (this file is authoritative on machines without that memory note).

The installed Codex plugin (`~/.claude/plugins/cache/openai-codex/codex/<version>/`) carries a local patch applied by `~/.claude/patches/codex-plugin-agent-patch.mjs` (idempotent; auto-picks the newest version dir). Plugin updates wipe it; `/repatch-codex` restores it. If the patcher reports a FAILED core edit, the plugin code drifted — re-derive the anchor from the *intent* below, update the patcher's `find`/`replace`, and re-run.

**Purpose 1 — `--agent <name>` on the companion `task` command.** Resolves `$CODEX_HOME/agents/<name>.toml`, extracts `developer_instructions`, and injects it natively as the app-server thread's `developerInstructions` (start AND resume). Core edits by intent:

1. `scripts/lib/codex.mjs` — add helper `loadAgentDeveloperInstructions(agentName)` (+ `extractDeveloperInstructions`): validates the agent name (`^[A-Za-z0-9][A-Za-z0-9._-]*$`), resolves `$CODEX_HOME/agents/<name>.toml` (env `CODEX_HOME` fallback `~/.codex`), extracts the TOML `developer_instructions` string (''' / """ / quoted forms), throws on missing file/empty value. Anchored before the `/** @returns {UserInput[]} */` helper block.
2. `scripts/lib/codex.mjs` — `buildThreadParams` and `buildResumeParams` conditionally include `params.developerInstructions` when `options.developerInstructions` is set (the app-server accepts it on thread start and resume).
3. `scripts/lib/codex.mjs` — `runAppServerTurn`: both branches (resume via `resumeThread`, start via `startThread`) pass `developerInstructions: options.developerInstructions ?? null` through.
4. `scripts/codex-companion.mjs` — import the loader alongside the other lib imports (anchor: `interruptAppServerTurn,`).
5. `scripts/codex-companion.mjs` — `handleTask`: accept `agent` in `valueOptions`; resolve `const agent = options.agent...; const developerInstructions = agent ? loadAgentDeveloperInstructions(agent) : null;` right after effort normalization; thread `agent` + `developerInstructions` through `buildTaskRequest`, the background enqueue call, and the foreground `executeTaskRun` call.
6. `scripts/codex-companion.mjs` — `buildTaskRequest` carries `agent` and `developerInstructions` fields (null defaults).
7. `scripts/codex-companion.mjs` — `executeTaskRun` computes `developerInstructions = request.developerInstructions ?? (request.agent ? loadAgentDeveloperInstructions(request.agent) : null)` (background workers re-resolve from the persisted request) and passes it into `runAppServerTurn`.

**Purpose 2 — accept `max` reasoning effort.** `VALID_REASONING_EFFORTS` gains `"max"`; the error string gains `, max`. Needed because `~/.codex/config.toml` defaults to Luna/max and users may explicitly request max. Model compatibility stays runtime-validated. (The orchestrator's Codex *planning preset* is `sol/xhigh` — the max edit is not for planning.)

**Purpose 3 — rescue agent on haiku.** `agents/codex-rescue.md` frontmatter `model: sonnet` → `model: haiku` (non-core edit "docs: rescue agent haiku model"): the rescue subagent is a mechanical forwarder (launch job → `status --wait` loop → `result`), so haiku suffices. If a future plugin version changes the forwarder into something judgment-bearing, drop this edit.

Doc edits (non-core, cosmetic): rescue agent/skill/command docs describing `--agent`, `max`, the background+wait launch protocol, and result forwarding. WARNING-level failures there are safe to fix opportunistically.

Verification after patching: syntax check both files (`node --check`), loader check (imports lib and loads `task-implementer-bdd` instructions), effort check (regex on `VALID_REASONING_EFFORTS`), plus the two optional live checks the patcher prints (role-injection echo; sol/max handshake proving max acceptance). The orchestrator templates in `~/.claude/skills/orchestrator/references/codex-delegation.md` depend on this patch.
