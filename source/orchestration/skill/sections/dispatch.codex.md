- A new work unit gets `spawn_agent` with `agent_type` set to the exact roster name and
  `fork_turns="none"`. An existing owner is reactivated with `followup_task`. `send_message` only
  adds information to an owner that is still running; it never reactivates an idle one. Reserve
  `interrupt_agent` for user redirection, an unsafe action, or a genuinely stuck owner.
- Dispatch independent wave members as parallel `spawn_agent` calls. A wave is a set of tasks that
  are mutually independent in files and contracts.
- Record each owner's agent id in the task's `Owner` field in `progress.md` immediately.
- **Affinity:** remediation, re-review, planner amendments, and artifact repair go back to the
  recorded owner with `followup_task`. In a fresh session, mark prior owners `stale` and dispatch
  replacements from artifacts; never assume an old id is reactivatable.
- **Parent wait-only state.** After dispatching one specialist or a parallel wave, say nothing and
  do nothing except call `wait_agent` with a long timeout, repeating the wait as needed, until
  every agent in that dispatch or wave has returned a terminal result or an attention request. Do
  not inspect the repository or artifacts, run commands or tests, start other work, narrate
  waiting or progress, process partial results, send follow-up messages, or interrupt, cancel,
  replace, or duplicate delegated work. When a parallel wait wakes for the first agent, wait again
  immediately for the rest; act only once the whole wave has answered. Break this rule only for new
  user direction or a genuine safety event.
