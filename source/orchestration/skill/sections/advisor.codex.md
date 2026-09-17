**Dispatch format.** Spawn the consult with `spawn_agent`, `agent_type="advisor"` and
`fork_turns="all"`, then `wait_agent`. The fork carries your retained thread, so do not re-narrate
history; use Evidence for what the thread cannot show. Write the brief in the session's working
language, keeping these sections:

```text
# Advisor Consultation
## Context
<task, lane, current state, decisions already made - one short paragraph>
## Evidence
<exact artifact and file paths the advisor must read, plus external research and docs results;
omit anything already visible in the inherited thread>
## Question
<one exact decision, not a broad topic>
## Constraints
<what cannot change>
```

Each consult is a new advisor and remembers nothing from earlier consults; never resume one as a
work owner. The inherited thread carries previous consult results; a follow-up round can add the
previous advice to Evidence if it was not visible there.
