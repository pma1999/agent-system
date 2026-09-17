The main Claude Code thread is the parent coordinator. Never create a separate orchestrator
subagent. `CLAUDE.md` routes you here when the user asks to orchestrate; the workflow is explicitly
opt-in and never the default for ordinary engineering work.

Ask the user directly for decisions and approval; you are the session they are talking to. If the
user records a standing approval such as "implement without asking", write it verbatim in
`progress.md` and do not request redundant approval. Product ambiguities still require a decision.

**Depth.** Specialists run as subagents with no Agent tool of their own, so work cannot recurse
further. Their one escape hatch is the native read-only `advisor` tool, available to them and to
you.
