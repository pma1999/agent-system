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

For frontend/UI work, apply `frontend-one` plus the relevant framework or design skill during
planning and implementation, and put those requirements in the task brief.

Before changing this orchestration installation, read
`~/.agentic/orchestrator/MAINTENANCE.md`. The canonical source contains literal Codex runtime files;
there is no generated workflow runtime or bundle controller.

For library, framework, SDK, API, CLI, or cloud-service details, use the current documentation
skill/tooling before relying on memory.
