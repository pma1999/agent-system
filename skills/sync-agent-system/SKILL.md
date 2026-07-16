---
name: sync-agent-system
description: Sync the personal multi-agent system config across machines — the ~/.claude and ~/.codex git repos. Pull the latest version onto this machine, or commit & push local changes. Use when the user says to sync, update, install, or publish the agent system / agents / orchestrator config, or after editing agents/skills so other PCs get the change.
---

# Sync Agent System

`~/.claude` and `~/.codex` are git checkouts of one private repo, `pma1999/agent-system` — branch `master` mirrors `~/.claude`, branch `codex` mirrors `~/.codex`. One script manages both; full docs in `~/.claude/README.md`.

## Update this machine (default)

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1"
```

Fast-forward pulls both repos, additively merges `templates/settings.json` → `settings.json` and `templates/config.toml` → `config.toml` (fills missing system keys, never overwrites), and re-applies the Codex plugin patch. Idempotent — safe to run anytime.

## Publish local changes ("push")

When the user asks to publish/push (e.g. after editing agents or skills here):

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1" -Push -Message "<short summary of the change>"
```

Commits and pushes both repos. Write a real one-line summary, not a placeholder.

## Handling script output

- Report per-repo results plainly (updated X→Y / already up to date / committed+pushed / no changes).
- `fetch/push falló` → git auth or missing remote: suggest `gh auth login` and confirm the private repos exist.
- `divergido` → do NOT force anything; show the printed `git pull --rebase` command and let the user decide.
- `pull omitido` (uncommitted tracked changes) → ask whether to publish them (`-Push`) or discard, don't choose silently.
- If it says the codex plugin isn't installed yet, tell the user to launch Claude Code once, then run `/repatch-codex`.

Machine state (credentials, sessions, real `settings.json`/`config.toml` values, plugin caches, memory) is never synced; only the agent system files are.
