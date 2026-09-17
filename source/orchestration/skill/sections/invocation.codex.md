The current top-level Codex thread is the parent coordinator. Never spawn a separate orchestrator
agent. `AGENTS.md` routes you here when the user invokes `$orchestrator` or asks to orchestrate; the
workflow is explicitly opt-in and never the default for ordinary engineering work.

Ask the user directly for decisions and approval; you are the session they are talking to. If the
user records a standing approval such as "implement without asking", write it verbatim in
`progress.md` and do not request redundant approval. Product ambiguities still require a decision.

**Depth.** Specialists may only spawn fresh `advisor` consultations; every other delegation is
forbidden, so work cannot recurse further. Native collaboration requires
`[features] multi_agent = true` in `config.toml`.
