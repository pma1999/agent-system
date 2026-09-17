- Launch specialists with the Agent tool, using the exact roster name as `subagent_type`.
- Dispatch independent wave members as parallel Agent calls in one message. A wave is a set of
  tasks that are mutually independent in files and contracts. Subagents run in the background and
  notify you on completion; do not poll them.
- The dispatch returns a reusable agent id. Immediately after it returns, record that id in the
  task's `Owner` field in `progress.md`.
- **Affinity:** remediation and re-review resume the recorded owner with `SendMessage`, which
  reactivates that agent with its context intact. `SendMessage` cannot cross sessions: in a resumed
  or fresh session, mark prior owners `stale` in `progress.md` and dispatch replacements from the
  artifacts. Never message a stale owner.
