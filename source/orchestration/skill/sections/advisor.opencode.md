**Dispatch format.** The advisor starts fresh and cannot see your transcript by itself - but the
`advisor-context` plugin injects the caller's complete prior transcript automatically (most recent
interactions first; internal reasoning blocks omitted; a truncation notice appears only when a size
cap was hit). Do not re-narrate history; use Evidence for what the transcript cannot show. Write
the brief in the session's working language, keeping these sections:

```text
# Advisor Consultation
## Context
<task, lane, current state, decisions already made - one short paragraph>
## Evidence
<exact artifact and file paths the advisor must read, plus external research and docs results;
omit anything already visible in the injected transcript>
## Question
<one exact decision, not a broad topic>
## Constraints
<what cannot change>
```

A consult is a fresh session - it remembers nothing from earlier consults. The injected transcript
carries previous consult results; a follow-up round can add the previous advice to Evidence if it
was not visible there.
