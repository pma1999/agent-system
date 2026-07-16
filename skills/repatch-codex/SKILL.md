---
name: repatch-codex
description: Re-apply the local Codex plugin compatibility patch (`--agent` injection, model-dependent `--effort max`, haiku rescue model) after an update wipes it. Use after Codex plugin updates, on unknown `--agent`/`max` errors, or when asked to restore the local patch.
---

# Repatch Codex Plugin

The installed Codex plugin carries a local compatibility patch that (1) adds `--agent <name>` to the companion `task` command (native injection of `~/.codex/agents/<name>.toml` `developer_instructions` via app-server `developerInstructions`), (2) accepts the model-dependent `max` reasoning effort (needed for `~/.codex/config.toml`'s Luna/max default and explicit max requests), and (3) sets the mechanical `codex-rescue` forwarder to haiku. Plugin updates wipe the cache copy; this skill restores all three.

## Steps

1. Run the idempotent patcher:

```bash
node "$HOME/.claude/patches/codex-plugin-agent-patch.mjs"
```

It auto-detects the newest version under `~/.claude/plugins/cache/openai-codex/codex/`, applies only missing edits (`applied` / `already`), then runs a syntax check and a loader check. `--dry-run` previews; `--dir <path>` overrides the target.

2. Read the output:
   - All `applied`/`already` + syntax, loader, and effort checks OK → done. Tell the user the patch is in place.
   - Any `FAILED` core edit → the new plugin version drifted. Do NOT guess-edit: open `~/.claude/patches/codex-plugin-agent-flag-patch.md` (tracked mirror of the memory note of the same name), which describes each edit's intent; adapt the anchors in `codex-plugin-agent-patch.mjs` to the new code, re-run, and update that doc if anchors changed.
   - `WARNING` on docs edits is cosmetic; fix opportunistically.

3. If runtime behavior is in doubt, run the live checks printed by the script:
   - the cheap `--agent task-implementer-bdd --effort low` check must echo `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT | PACK_GAP`, proving role injection;
   - a read-only `--agent implementation-planner --model gpt-5.6-sol --effort max` handshake must complete without an effort-validation error, proving `max` acceptance reaches the runtime (the orchestrator's Codex planning preset itself is `sol/xhigh`; `max` matters for config-default runs and explicit user requests).

The Codex dispatch templates in `~/.claude/skills/orchestrator/references/codex-delegation.md` (peer implementer `--agent task-implementer-bdd --model <m> --effort <e>`, planner `--agent implementation-planner`) depend on this patch.

## Optional: role-twin parity check

While doing plugin/system maintenance, also run the role-file drift detector:

```bash
node "$HOME/.claude/patches/agent-parity-check.mjs"
```

It compares each `~/.claude/agents/<role>.md` with its `~/.codex/agents/<role>.toml` twin section by section. Investigate new drift or unexpected one-sided sections; intentional cross-CLI differences are normal and stay.
