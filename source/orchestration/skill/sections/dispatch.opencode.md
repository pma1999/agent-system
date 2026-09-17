- Launch specialists with `task`, using the exact roster name as `subagent_type`.
- Dispatch independent wave members as parallel task calls in one message. A wave is a set of
  tasks that are mutually independent in files and contracts. Use a single blocking call when no
  useful work can proceed without its result. Do not poll background agents.
- The task result includes a reusable `task_id`. Immediately after it returns, record that ID in
  the task's `Owner` field in `progress.md`.
- **Affinity:** remediation and re-review resume the recorded owner with `task_id`. In a fresh
  OpenCode session, mark prior owners `stale` and dispatch replacements from artifacts; never
  assume an old ID is resumable.
