# Optional engineering orchestration

The `orchestrator` skill is an optional, explicit workflow. Apply it only when the user invokes
`$orchestrator` or clearly asks to use the multi-agent orchestration workflow. Do not activate it
automatically for ordinary engineering work. If the user opts out, work directly.

When the skill is active, the current top-level Codex thread is the parent orchestrator. Never
spawn a separate orchestrator agent. Specialists are already inside that workflow: they must not
load `orchestrator`, coordinate the workflow, or spawn other work owners. They may consult the
read-only `advisor` only as allowed by their own profile.

Use native collaboration for orchestration. A new work unit gets `spawn_agent`; an existing owner
is reactivated with `followup_task`; `send_message` only adds information to an owner that is still
running. Preserve owner affinity for planner amendments, implementer remediation, reviewer
re-review, and artifact repair.

After dispatching one specialist or a parallel wave, the top-level orchestrator enters a strict
wait-only state. Until every agent in that dispatch or wave has returned a terminal result or an
attention request, the main thread must say nothing and do nothing except call `wait_agent` with a
long timeout and repeat the wait as needed. It must not inspect the repository or artifacts, run
commands or tests, start other work, narrate waiting/progress, process partial results, send follow-up
messages, interrupt, cancel, replace, or duplicate any delegated work. When a parallel wait wakes
for the first agent, immediately wait again for the remaining agents; act only after the whole wave
has answered. Break this rule only for new user direction or a genuine safety event.

For frontend/UI work, apply the `frontend` skill plus the relevant framework or design skill during
planning and implementation, and put those requirements in the task brief.

Before changing this orchestration installation, read the README of the canonical source at
`~/agent-system`. These files are generated from it: editing them here is overwritten on the next
install. Workflow state stays plain Markdown under `plans/<slug>/`; there is no workflow runtime or
bundle controller.

For library, framework, SDK, API, CLI, or cloud-service details, use the current documentation
skill/tooling before relying on memory.

# Frontend and UI work

For any work that touches a user-facing surface - a page, component, layout, screen, dashboard, or
visual design - load the `frontend` skill. It is installed in every harness and it sets the visual,
UX and accessibility bar the work must meet: mode (extend an existing design language or redesign),
art direction, tokens and theming including dark mode, dense product surfaces, the state matrix,
motion, and the checks the result has to pass. Load it **both when planning and when implementing**,
never just one.

Load on top of it whatever else this environment offers that matches the stack or the design system
- framework skills, design-system skills, documentation skills. `frontend` is the floor, not the
ceiling.

A Playwright MCP server and a Chrome DevTools MCP server are installed and available to every agent.
Neither is the default: pick whichever fits what you need to see. Use one of them to look at what
you built before calling it done - a diff cannot show contrast, focus order, layout at 375px,
console errors, or layout shift.

# Git delivery

Before repository changes or GitHub work, load the shared `git-github` skill. It applies both
to direct engineering and optional orchestration; it does not activate orchestration. Follow
its local commit ownership, repository contribution rules and completed-result publication
gate. Commit meaningful verified units locally; push or create/update PRs only after explicit
user approval of the concrete finished result. Use its Windows/WSL guidance for `gh.exe`.
