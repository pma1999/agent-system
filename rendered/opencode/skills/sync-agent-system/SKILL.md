---
name: sync-agent-system
description: Sync, install or publish the personal multi-agent system - the shared orchestration prompts, specialist agents and skills deployed into ~/.claude, ~/.codex and ~/.config/opencode from the canonical repo at ~/agent-system. Use when the user says to sync, update, install or publish the agent system / agents / orchestrator / skills, after editing any of them so other machines get the change, or when something in those folders looks out of date or edited by hand.
---

# Sync Agent System

One canonical repo, `pma1999/agent-system` (branch `main`), cloned at `~/agent-system`, is the
single source of truth for all three harnesses. The live folders (`~/.claude`, `~/.codex`,
`~/.config/opencode`) are **deployment targets**, not repos: what lands there is generated from the
canonical source. Full docs in `~/agent-system/README.md`.

All commands run from the repo:

```bash
cd ~/agent-system
python bin/agentsys.py <comando>
```

On Windows `pwsh -NoProfile -File "$HOME/agent-system/bin/install.ps1"` is a shim for
`build` + `verify` + `install`.

## Update this machine

```bash
git -C ~/agent-system pull --ff-only
python bin/agentsys.py install      # renderiza y despliega; idempotente
python bin/agentsys.py verify
```

`install` backs up every file it replaces under `~/.agent-system-backups/<timestamp>/` and merges
the config templates additively (`settings.json`, `config.toml`, `opencode.jsonc`): missing system
keys are added, existing values are never overwritten.

## Publish changes made here

```bash
python bin/agentsys.py verify
python bin/agentsys.py publish -m "<one-line summary of the change>"
```

`publish` refuses to run when `verify` fails, and stages an explicit file list - it never runs
`git add -A`, so machine state and synced plugin skills cannot leak into the repo. Write a real
summary, not a placeholder.

## Where a change belongs

Never edit the live folders: `install` overwrites them and `verify` reports the drift.

| What changes | Edit |
|---|---|
| A specialist's prompt, for all three harnesses | `source/orchestration/agents/<role>.md` |
| The orchestration operating model | `source/orchestration/skill/SKILL.md` |
| Something true of only one harness | `source/orchestration/skill/sections/<anchor>.<harness>.md` |
| A model, effort, permission or tool name | `harness/<harness>/adapter.toml` |
| A skill shared by the three | `source/skills/<skill>/` |
| A skill of one harness only | `harness/<harness>/files/skills/<skill>/` |
| `CLAUDE.md`, `AGENTS.md`, templates, patches | `harness/<harness>/files/` |

After any edit: `build`, then `verify`, then `install`.

## Handling output

- `verify` prints four blocks. Report which failed, verbatim.
  - *Render determinista* failing means someone edited `rendered/`; re-run `build`.
  - *Identidad de prompts* failing means the three harnesses no longer share one body: the diff it
    prints says exactly where. Fix the canonical source, never one harness.
  - *Deriva* means the live folders do not match; run `install`.
- `install` reporting **rechazados** means those files exist, differ, and were never managed by
  this system. Show the list and ask whether to keep them (copy them aside) or overwrite with
  `--force`. Do not choose silently.
- `adopt` pulls a hand-made change in a live folder back into the canonical source. It refuses for
  generated files and tells you which canonical file to edit instead.
- `status` gives the short version: what is managed, what drifted, whether a legacy checkout is
  still active in a live folder.

## Install on a new machine

```bash
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system && python bin/agentsys.py install
```

Then: open `claude` once so it installs the plugins from `settings.json`; run `/repatch-codex` if
the installer left the Codex plugin patch pending; `codex login` for the Codex side. For OpenCode
inside WSL, link the Windows folders once - see `docs/INSTALACION.md`.

Machine state (credentials, sessions, history, the real `settings.json` / `config.toml` /
`opencode.jsonc` values, plugin caches, plugin skills synced from claude.ai) is never part of the
repo.
