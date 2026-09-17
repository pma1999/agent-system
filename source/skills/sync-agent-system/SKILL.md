---
name: sync-agent-system
description: Operate the personal multi-agent system - the orchestration prompts, specialist agents and skills that live in one canonical repo (~/agent-system) and deploy into ~/.claude, ~/.codex and ~/.config/opencode. Use it to pull and apply the latest version onto this machine, publish local changes so other machines get them, check whether this machine is in sync or has drifted, switch the model or effort of a role, migrate a machine that still uses the retired three-branch layout, or set the system up on a new one. Trigger on anything like "sync the agent system", "fetch the latest", "publish what you changed", "is this machine up to date", "install this on the new laptop", "switch opencode to <model>", or after editing any agent, skill or orchestration prompt so the change reaches the other machines - even when the user does not name the repo or the tooling.
---

# Operating the agent system

**You run this, end to end.** The user asks for an outcome ("fetch the latest", "publish that",
"is this machine current?") and you execute the commands, read the output, and report what actually
happened. Do not print a command list and hand it back - the point of this skill is that they
don't have to.

The one thing you never do alone is decide what happens to *their* files. Those decision points are
marked below; when you hit one, stop and ask with the evidence in front of them.

## The shape of the system

`~/agent-system` (branch `main`) is the single source of truth. `~/.claude`, `~/.codex` and
`~/.config/opencode` are **deployment targets**: what lands there is generated. Editing them
directly is pointless - the next `install` overwrites it and `verify` reports it as drift.

Everything goes through one tool:

```bash
cd ~/agent-system && python bin/agentsys.py <comando>
```

`build` renders, `verify` checks, `install` deploys, `publish` pushes, `status` summarises,
`adopt` rescues a hand-edit, `models` switches models.

**Under WSL, pass `--home /mnt/c/Users/<usuario>`** to `install`, `verify`, `status` and `adopt`.
`~` is the Linux home there, but Claude Code and Codex read the Windows one. The tool detects WSL
and prints the exact flag to use - if you see that warning, you forgot it.

## Start by orienting

Unless the request is obviously a one-liner, run `status` first. It costs nothing and it tells you
which of the four jobs below you are actually in:

- *no instalado* -> this machine has never had it: **set up** or **migrate**.
- *N ficheros con deriva* -> someone edited a live folder, or an `install` is pending.
- *[checkout legacy activo]* -> still on the retired three-branch layout: **migrate**.

## Job 1 - Bring this machine up to date

```bash
cd ~/agent-system
git pull --ff-only
python bin/agentsys.py install
python bin/agentsys.py verify
```

If `~/agent-system` does not exist, clone it first
(`git clone https://github.com/pma1999/agent-system.git ~/agent-system`) - that is the normal
bootstrap, not an error.

If `git pull --ff-only` refuses because the branches diverged, **do not force anything**. Show them
what is on each side and ask.

## Job 2 - Publish what was changed here

```bash
cd ~/agent-system
python bin/agentsys.py verify
python bin/agentsys.py publish -m "<resumen>"
```

`publish` refuses to run when `verify` fails, and stages an explicit file list - never `git add -A`
- so machine state and third-party plugin skills cannot leak into the repo.

**Write the message yourself, from the actual diff.** Read `git diff --stat` and `git diff` before
composing it, and say what changed and why in one line. A placeholder like "update" makes the
history useless for the person on the other machine, who is usually the same person six weeks
later.

Publishing is outward-facing. If the user said "publish", that is your authorisation. If they only
said "I changed X", make the change and *offer* to publish.

## Job 3 - Change something in the system

Never edit the live folders. Find the right file first:

| What changes | Where it lives |
|---|---|
| A specialist's prompt, for all three harnesses | `source/orchestration/agents/<role>.md` |
| The orchestration operating model | `source/orchestration/skill/SKILL.md` |
| Something true of only one harness | `source/orchestration/skill/sections/<anchor>.<harness>.md` |
| A role's model or effort | `agentsys models` (never the adapter by hand) |
| Permissions, colours, tool names, sandbox | `harness/<h>/adapter.toml` |
| A skill shared by the three | `source/skills/<skill>/` |
| A skill of one harness only | `harness/<h>/files/skills/<skill>/` |
| `CLAUDE.md`, `AGENTS.md`, templates, patches | `harness/<h>/files/` |

Then always: `build` -> `verify` -> `install`. And offer to publish.

The rule that keeps the three harnesses identical: if the text would read the same in all three,
it belongs in the canonical body. If you find yourself wanting a per-harness `if` inside that body,
it is a token or a section instead. `verify` proves this on every run, so a mistake here shows up
immediately rather than six months later.

### Switching models

```bash
python bin/agentsys.py models list                                  # * marca el perfil vigente
python bin/agentsys.py models apply <perfil> --harness <h>
python bin/agentsys.py models set --harness <h> --model <m> [--effort <e>] [--role <r>]
python bin/agentsys.py models save <nombre> --harness <h>
```

Both `apply` and `set` rewrite the canonical adapter and re-render, so `install` still has to run
afterwards. OpenCode has many profiles because it changes often; Claude and Codex start with one.

On OpenCode only, `--scope` picks what gets touched: `ours` (default) is the orchestrator roster,
`omo` is the active preset of `oh-my-opencode-slim.json`, `both` is the two. OMO is a *different*
agent system and its config is local to each machine, so never widen the scope without being asked.

## Job 4 - Migrate a machine from the old three-branch layout

A machine where `status` shows `[checkout legacy activo]`, or where `~/.claude` is still a git
checkout of `master`. Its `~/.claude/install.ps1` is the retired installer; running it reinstalls
the old system from frozen branches.

```bash
git clone https://github.com/pma1999/agent-system.git ~/agent-system
cd ~/agent-system
python bin/agentsys.py install --dry-run
```

**Stop here and put the dry run in front of the user.** It touches nothing, and the *rechazados*
are the whole point of running it:

- `cambio local sin publicar` - work this machine never pushed. Show them the diff
  (`git -C ~/.claude diff -- <fichero>`) and ask. This is the only thing the migration can lose
  sight of.
- `nunca estuvo gestionado` - a file of theirs the system did not put there. Same rule.

Once they have decided:

```bash
python bin/agentsys.py install                          # respeta todos los rechazados
python bin/agentsys.py install --force ruta/aprobada    # solo los que autorizaron
python bin/agentsys.py install --retire-legacy
python bin/agentsys.py verify
```

`--retire-legacy` renames each live folder's `.git` to `.git.legacy-agent-system-<fecha>`; nothing
is deleted and renaming it back reverts it. Machine state survives: the config templates merge
additively and never overwrite an existing value.

Afterwards tell them the manual bits: open `claude` once so it installs the plugins from
`settings.json`, run `/repatch-codex` if the Codex plugin patch was left pending, and `codex login`
for the Codex side.

## Reading the output

`verify` prints four blocks. Report which one failed, verbatim - each means something different:

- **Render determinista** - someone edited `rendered/` by hand. Re-run `build`; if the edit was
  intentional, move it to the canonical source first.
- **Identidad de prompts** - the three harnesses no longer share one body. The diff it prints says
  exactly where. Fix it in `source/orchestration/`, never in one harness.
- **Envoltorio: esquema y roster** - a model alias, effort, colour or roster entry a harness would
  silently ignore. These fail quietly at runtime, which is why the check exists.
- **Deriva** - the live folders do not match `rendered/`. Run `install`.

`install` reporting **rechazados** or **REVISA A MANO** is not a failure - it is the tool refusing
to guess. Both need the user.

## When to stop and ask

Everything else you handle yourself. These four are theirs:

1. **Rechazados.** Their file, differing from what we would write. Show the list with reasons, and
   the diff for anything marked `cambio local sin publicar`. Never reach for `--force` on your own.
   When they approve some but not others, pass the approved paths: `--force AGENTS.md`. Bare
   `--force` overwrites every rejected file, so use it only when they said yes to all of them.
2. **`REVISA A MANO`.** System keys missing inside a config block they already had. The merge will
   not insert them without destroying their comments. Give them the exact paths. The one that
   matters most is `permission.skill.orchestrator: "deny"` on OpenCode - without it the Claude
   `orchestrator` skill, visible there through the `~/.claude/skills` symlink, gets advertised in
   the wrong runtime.
3. **Divergencia en git.** Show both sides; never force-push or hard-reset.
4. **Anything that would discard their work.** Backups exist - every replaced file is under
   `~/.agent-system-backups/<fecha>/` - but a backup is a recovery path, not permission.

## What is not in the repo

Credentials, sessions, history, transcripts, plugin caches, the real `settings.json` /
`config.toml` / `opencode.jsonc` / `opencode.v2.jsonc` values, and the plugin skills synced from
claude.ai under `skills/synced/`. If someone asks why a machine-specific setting did not travel:
that is deliberate, and the templates are how a new machine gets the *system* keys without losing
its own.

Full reference: `~/agent-system/README.md`, and `docs/INSTALACION.md` for migration and WSL.
