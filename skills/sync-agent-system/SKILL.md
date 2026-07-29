---
name: sync-agent-system
description: Sync the personal multi-agent system config across machines — the ~/.claude, ~/.codex and ~/.config/opencode git repos. Pull the latest version onto this machine, or commit & push local changes. Use when the user says to sync, update, install, or publish the agent system / agents / orchestrator / opencode config, or after editing agents/skills so other PCs get the change.
---

# Sync Agent System

`~/.claude`, `~/.codex` and `~/.config/opencode` are git checkouts of one private repo, `pma1999/agent-system` — branch `master` mirrors `~/.claude`, branch `codex` mirrors `~/.codex`, branch `opencode` mirrors `~/.config/opencode`. One script manages all three; full docs in `~/.claude/README.md`.

## Update this machine (default)

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1"
```

Fast-forward pulls the three repos, additively merges `templates/settings.json` → `settings.json`, `templates/config.toml` → `config.toml` and `templates/opencode.jsonc` → `opencode.jsonc` (fills missing system keys, never overwrites), and re-applies the Codex plugin patch. Idempotent — safe to run anytime.

## Publish local changes ("push")

When the user asks to publish/push (e.g. after editing agents or skills here):

```powershell
pwsh -NoProfile -File "$HOME/.claude/install.ps1" -Push -Message "<short summary of the change>"
```

Commits and pushes the three repos. Write a real one-line summary, not a placeholder.

## Running from WSL (OpenCode)

`pwsh` is not installed in WSL; call the Windows PowerShell 7 via interop with **Windows** paths (adjust the Windows user name):

```bash
pwsh.exe -NoProfile -File 'C:\Users\PcVIP\.claude\install.ps1'
pwsh.exe -NoProfile -File 'C:\Users\PcVIP\.claude\install.ps1' -Push -Message "<short summary>"
```

On a new WSL installation, bridge both OpenCode config and the synchronized Claude-compatible skills once (back up a pre-existing target before replacing it):

```bash
ln -s /mnt/c/Users/PcVIP/.config/opencode ~/.config/opencode
mkdir -p ~/.claude
ln -s /mnt/c/Users/PcVIP/.claude/skills ~/.claude/skills
npx -y @playwright/mcp@latest install-browser chromium
sudo npx -y playwright@latest install-deps chrome-for-testing
```

The skills link makes `sync-agent-system`, frontend skills, docs skills and the rest of `~/.claude/skills` globally visible to OpenCode from any WSL project. OpenCode config denies the Claude `orchestrator` skill, so the wrong runtime skill is neither advertised nor invocable. Do not copy that runtime-specific skill into the OpenCode branch. The final two commands install the browser and Linux dependencies once per WSL distro; `sudo` may require the user's password.

## Handling script output

- Report per-repo results plainly (updated X→Y / already up to date / committed+pushed / no changes).
- `fetch/push falló` → git auth or missing remote: suggest `gh auth login` and confirm the private repos exist.
- `divergido` → do NOT force anything; show the printed `git pull --rebase` command and let the user decide.
- `pull omitido` (uncommitted tracked changes) → ask whether to publish them (`-Push`) or discard, don't choose silently.
- If it says the codex plugin isn't installed yet, tell the user to launch Claude Code once, then run `/repatch-codex`.

Machine state (credentials, sessions, real `settings.json`/`config.toml`/`opencode.jsonc` values, plugin caches, memory, opencode `node_modules`) is never synced; only the agent system files are.
