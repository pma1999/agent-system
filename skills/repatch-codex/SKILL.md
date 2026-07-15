---
name: repatch-codex
description: Re-apply the local Codex plugin compatibility patch (`--agent` injection plus model-dependent `--effort max`) after an update wipes it. Use after Codex plugin updates, on unknown `--agent`/`max` errors, or when asked to restore the local patch.
---

# Repatch Codex Plugin

The installed Codex plugin carries a local compatibility patch that adds `--agent <name>` to the companion `task` command (native injection of `~/.codex/agents/<name>.toml` `developer_instructions` via app-server `developerInstructions`) and accepts the model-dependent `max` reasoning effort used by GPT-5.6-Sol planning. Plugin updates wipe the cache copy; this skill restores both behaviors.

## Steps

1. Run the idempotent patcher:

```bash
node "C:\Users\Pablo\.claude\patches\codex-plugin-agent-patch.mjs"
```

It auto-detects the newest version under `~/.claude/plugins/cache/openai-codex/codex/`, applies only missing edits (`applied` / `already`), then runs a syntax check and a loader check. `--dry-run` previews; `--dir <path>` overrides the target.

2. Read the output:
   - All `applied`/`already` + syntax, loader, and effort checks OK → done. Tell the user the patch is in place.
   - Any `FAILED` core edit → the new plugin version drifted. Do NOT guess-edit: open the memory note `codex-plugin-agent-flag-patch` (in `~/.claude/projects/C--Users-Pablo/memory/`) which describes each edit's intent, adapt the anchors in `codex-plugin-agent-patch.mjs` to the new code, re-run, and update that memory if anchors changed.
   - `WARNING` on docs edits is cosmetic; fix opportunistically.

3. If runtime behavior is in doubt, run the live checks printed by the script:
   - the cheap `--agent task-implementer-bdd --effort low` check must echo `DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT | PACK_GAP`, proving role injection;
   - a read-only `--agent implementation-planner --model gpt-5.6-sol --effort max` handshake must complete without an effort-validation error, proving the planning preset reaches the runtime.

The orchestrator skill's Codex peer-implementer template (`--wait --write --agent task-implementer-bdd`) and optional Codex planning template depend on this patch. The peer implementer intentionally remains model/effort-free.
