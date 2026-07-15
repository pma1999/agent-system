For top-level Codex sessions, any programming or software-engineering task must apply the `orchestrator` skill first. For non-trivial code changes, this is a standing explicit request to use Codex subagent workflows and the custom agents in `C:\Users\PcVIP\.codex\agents\` when the skill's lane calls for delegation. If you are running as any Codex subagent/delegated specialist, including `codebase-explorer`, `integration-researcher`, `implementation-planner`, `task-implementer-bdd`, `implementation-reviewer`, or `root-cause-debugger`, or if you were explicitly dispatched as a delegated specialist by an external orchestrator (for example through `codex exec` or a rescue forwarder), this requirement is already satisfied by the parent orchestrator: do not apply or invoke `orchestrator`; follow your specialist prompt directly.

For any work that involves **frontend / UI** (building or reshaping a page, component, layout, screen, or visual design), ALWAYS also apply the available frontend skills (especially `frontend-one`, plus any relevant framework/design skill) — **both when planning and when implementing**, never just one. They set the visual/UX bar the work must meet.

The orchestrator only orchestrates. It chooses the lane, gathers requirements, routes artifacts, gives specialists complete inputs, tracks progress, applies quality gates, and synthesizes specialist outputs for the user. It does not pre-write the planner's plan, debugger's diagnosis, implementer's solution, researcher's contract, or reviewer's verdict; those conclusions belong to the delegated specialist unless already settled by the user or an upstream artifact.

When `orchestrator` is used for non-trivial work, prefer artifact handoffs over pasted context: `codebase-explorer` writes `plans/<slug>/context-map.md`, `implementation-planner` writes a plan bundle with `plan.md`, `global-constraints.md`, `task-<id>-brief.md`, and `progress.md`, implementers work from one task brief and write one task report, and reviewers start from briefs/reports/diffs. Do not make downstream agents read the whole plan or accumulated history; if a brief lacks required context, treat it as `PACK_GAP` and repair the artifact.

Token discipline never lowers the quality bar. Agents should avoid repeated discovery, not necessary discovery: explore enough to map the area, research integrations enough to verify the needed contract, plan to an expert maintainable design, implement with meaningful tests, and review from evidence. If a cheap read leaves real doubt, widen deliberately and record why.

When the orchestrator delegates work to a Codex subagent, that work unit has one owner. Write permission follows the deliverable: any delegated specialist that must write files — task reports, diagnosis artifacts, bundle files, code — must run write-capable; specialists must not refuse or skip writing their own artifacts for lack of permissions, and the orchestrator must not accept a "no write permission" complaint as a result — fix the dispatch and re-delegate. The orchestrator must remain suspended until the subagent returns a terminal result, question, gap, or failure. Progress notices, when required by the host, must come from the pending tool call and must not create model turns or status polls. Do not read files, run `rg`, query CodeGraph, run tests, or perform the delegated exploration/planning/implementation/review yourself unless you explicitly switch back to the Direct lane for a genuinely trivial remaining action.

In orchestrated work, each artifact has one owner and one purpose. Keep `progress.md` as a ledger, not a narrative; keep task reports as implementation deltas, not plan summaries; keep reviews as verdict/evidence. Task review is optional and should run only when it gates dependent work, covers a risky/shared contract, or addresses concerns; final review remains the normal quality gate. Agent completion messages should be short and point to artifacts instead of repeating them.

## Dispatch Backends And Agent Reuse

Before every dispatch, choose a backend that can apply the selected agent profile, model, and reasoning effort exactly:

- Prefer `native-collab` when `spawn_agent` exposes and accepts `agent_type`, `model`, and `reasoning_effort`. If it exposes `fork_turns`, set it to `none` because full-history forks inherit the parent profile and cannot take routing overrides. Record the returned canonical target and use `followup_task` for later turns.
- If any required routing field is absent or rejected, use the orchestrator skill's `scripts/invoke-specialist.ps1`. It runs the selected custom agent through persistent `codex exec`, injects that agent TOML's `developer_instructions`, and sets the exact model/effort. Record the returned `job_id`, then apply the single-call passive wait in `skills/orchestrator/references/codex-exec-passive-wait.md`; do not use minute-scale wait/reason/wait loops. Record the returned thread UUID as `codex-exec:<uuid>`. On Windows the hidden Scheduled Task has `ExecutionTimeLimit = 0`, so the specialist lifetime is independent from the waiter. Use the same script with `-SessionId <uuid>` to start a persistent resumed turn and wait on its new job ID.
- A profile's TOML defaults do not prove per-task routing. Record a pair as actual only after the chosen backend accepts it; never claim a prompt-only model choice.
- Report a routing-capability gap only if neither exact native dispatch nor the resumable `codex-exec` backend is available.

Preserve agent affinity when a reviewer requests changes inside a task's existing scope. Record each implementer/reviewer backend, resumable owner, actual profile, and follow-up mechanism in `progress.md`.

- For `native-collab`, use `list_agents` only to confirm the recorded target and `followup_task` to reactivate it.
- For `codex-exec`, resume the recorded UUID with `invoke-specialist.ps1 -SessionId`, record the new job ID, and use the same single-call passive wait. The parent must not regain an inference turn merely to observe unchanged state. Only a terminal specialist result or a genuine host/tool interruption ends the wait; after a genuine interruption, reattach to the same durable job.
- Record every `codex-exec` `job_id`, terminal state, and cleanup state in the current workflow's `progress.md`. A terminal result closes the Codex and PowerShell processes but deliberately retains the inactive Scheduled Task definition and durable job evidence for review, diagnosis, and follow-up. Do not run `-Cleanup` merely because an agent, task review, or final review completed.
- Treat cleanup as the workflow-close gate. Run it only after the user explicitly confirms that the delivered workflow is accepted/finished and no review, remediation, or follow-up is pending. Use only job IDs recorded for that workflow; never use global `-List` output as a deletion scope. Verify each job is terminal, wait for any active recorded job, preserve its final state/session/outcome in the ledger, run `invoke-specialist.ps1 -Cleanup -JobId <job-id>`, and mark it `cleaned` with the returned timestamp. If cleanup fails, retain the job and report its ID instead of broadening deletion.
- Do not use `send_message` for remediation of an idle/completed agent: it delivers information but does not trigger a new turn. Reserve it for a short clarification to an agent that is already running.
- Do not use `interrupt_agent` in the normal fix loop. It is for stopping active work, not requesting the next remediation turn.
- After the original implementer finishes the fix and updates its task report, resume the original reviewer through its recorded backend to re-check the same finding IDs and update the same review artifact.
- Reusing an agent also reuses its existing model/profile. This is correct for in-scope remediation. If the requested fix materially changes scope, risk, contracts, or required capability, repair/replan the execution contract and route a new work unit instead of forcing it through the old agent.
- If the original agent no longer exists, is stale, or cannot resume, dispatch a replacement as a fallback using the brief, report, review, and diff. Record the replacement owner and newly selected routing profile; never silently lose ownership history.

Same-task defects return to the original implementer. Cross-task integration defects, changed requirements, or findings outside that implementer's touch boundary require planner/orchestrator triage before choosing an owner.

## Multi-Agent Model Routing

When evaluating whether a newer Codex release can replace the compatibility dispatch backend, follow `skills/orchestrator/references/native-agent-routing-migration.md`. Use its current-contract check, native smoke test, and coordinated cleanup before changing agent profile defaults, backend selection, or follow-up ownership.

Set both the model and reasoning effort explicitly for every delegated-agent dispatch. `implementation-planner` always uses `gpt-5.6-sol` with `xhigh` reasoning; this is fixed and the planner does not choose its own profile. The `gpt-5.6-terra` / `high` configuration of every other specialist is only a fallback, never the default routing decision.

Every dispatch has a routing owner and an explicit routing decision:

- This applies to every current or future delegated agent — explorer, researcher, debugger, implementer, reviewer, or any unexpected direct transition. The only exception is `implementation-planner`, whose profile is always `gpt-5.6-sol` / `xhigh`.
- When a plan covers the work unit, `implementation-planner` owns its routing. It selects the implementation profile for every task, the reviewer profile for every required task review, and one final-review profile for the whole plan. It records each decision in `plan.md` and the task-local decisions in the corresponding brief.
- When no planner artifact covers the work unit, the orchestrator owns routing at dispatch time. This includes pre-plan discovery/research/diagnosis, `debugger -> implementer`, localized fixes, standalone reviews, recovery work, and unforeseen lanes. Apply the same scale and selection method; never insert a planner solely to choose a model.
- An orchestrator-owned decision must be written into the dispatch prompt as a compact routing record: agent, model, reasoning effort, intelligence score, evidence-based rationale, and escalation triggers. If a bundle or ledger exists, also record planned and actual routing there.
- Dispatch the exact selected profile. Do not silently upgrade, downgrade, replace it, or accept the agent-profile fallback as a decision. If scope, risk, or evidence changes, the owner of that routing decision re-evaluates it: amend the planner artifact when planner-owned; otherwise replace the orchestrator-owned routing record.
- If native collaboration cannot apply the selected role/model/effort, use the resumable `codex-exec` backend above. Report a routing-capability gap only if that backend also fails. Never claim or record the selected profile as actual when the runtime only used a profile default.

| Rank | Model / reasoning effort | Intelligence |
|---:|---|---:|
| 1 | `gpt-5.6-terra` / `max` | 55 |
| 2 | `gpt-5.6-luna` / `max` | 52 |
| 3 | `gpt-5.6-terra` / `xhigh` | 51 |
| 4 | `gpt-5.6-luna` / `xhigh` | 49 |
| 5 | `gpt-5.6-terra` / `high` | 49 |
| 6 | `gpt-5.6-luna` / `high` | 46 |
| 7 | `gpt-5.6-terra` / `medium` | 46 |
| 8 | `gpt-5.6-terra` / `low` | 40 |
| 9 | `gpt-5.6-luna` / `medium` | 38 |
| 10 | `gpt-5.6-luna` / `low` | 33 |

Treat intelligence as a capability floor, not a score to maximize. Assess scope/coupling, ambiguity/novelty, correctness and blast-radius risk, and verification difficulty. Choose the lowest-intelligence approved pair that safely clears the highest load-bearing demand; this is the efficient choice because excess capability is not bought without a quality reason. Scores are ordinal, not additive: do not average dimensions, and move up when several difficult dimensions interact. At equal intelligence, choose by task fit and then by the lower reasoning effort or known lower operational cost; do not invent cost differences.

The routing owner must record the chosen pair, intelligence score, short evidence-based rationale, and concrete escalation triggers. Size every work unit independently: never inherit a model merely because the preceding agent used it. A reviewer may require an equal or stronger profile than its implementer, especially for cross-task integration, security, data, migrations, concurrency, public contracts, or critical UX. If the required floor or task fit cannot be assessed confidently, use `gpt-5.6-terra` with `max` reasoning. Luna is eligible at every listed effort level; never treat it as simple-task-only. For non-planner specialists, do not use an unranked pair such as Terra `ultra` unless the user supplies a new approved scale.

<!-- CODEGRAPH_START -->
## CodeGraph

This project has a CodeGraph MCP server (`codegraph_*` tools) configured. CodeGraph is a tree-sitter-parsed knowledge graph of every symbol, edge, and file. Reads are sub-millisecond and return structural information grep cannot.

### When to prefer codegraph over native search

Use codegraph for **structural** questions — what calls what, what would break, where is X defined, what is X's signature. Use native grep/read only for **literal text** queries (string contents, comments, log messages) or after you already have a specific file open.

| Question | Tool |
|---|---|
| "Where is X defined?" / "Find symbol named X" | `codegraph_search` |
| "What calls function Y?" | `codegraph_callers` |
| "What does Y call?" | `codegraph_callees` |
| "What would break if I changed Z?" | `codegraph_impact` |
| "Show me Y's signature / source / docstring" | `codegraph_node` |
| "Give me focused context for a task/area" | `codegraph_context` |
| "Survey an unfamiliar module/topic" | `codegraph_explore` |
| "What files exist under path/" | `codegraph_files` |
| "Is the index healthy?" | `codegraph_status` |

### Rules of thumb

- **Trust codegraph results.** They come from a full AST parse. Do NOT re-verify them with grep — that's slower, less accurate, and wastes context.
- **Don't grep first** when looking up a symbol by name. `codegraph_search` is faster and returns kind + location + signature in one call.
- **Don't chain `codegraph_search` + `codegraph_node`** when you just want context — `codegraph_context` is one call.
- **`codegraph_explore` is the heavy hitter** for unfamiliar areas — it returns full source from all relevant files in one call, but is token-heavy. If your harness supports parallel subagents (e.g., Claude Code's Task tool), spawn one for explore-class questions to keep main session context clean.
- **Index lag**: the file watcher debounces ~500ms behind writes; don't re-query immediately after editing a file in the same turn.

### If `.codegraph/` doesn't exist

The MCP server returns "not initialized." Ask the user: *"I notice this project doesn't have CodeGraph initialized. Want me to run `codegraph init -i` to build the index?"*
<!-- CODEGRAPH_END -->

## Code retrieval strategy — cheapest sufficient tool

Refines the CodeGraph table above. **Principle: for each thing you need to know, use the cheapest tool that fully answers it; climb to a heavier tool only when the cheaper one can't.** Quality is the floor — if you genuinely must read it all, read it all — but among tools that clear the bar, pick the cheapest, and never re-fetch what you already have. codegraph stays central for *relational* questions; it is one rung of this ladder, not the default for everything.

Retrieval is question-driven and adaptive. Start broad only when the area or failure mode is genuinely uncertain; once paths, symbols, strings, routes, contracts, or tests are known, switch to exact search/symbol tools and targeted reads. Widen again only for a material doubt, named risk, or artifact gap that could change the design, implementation, or verdict. Stop reading when you can safely produce the artifact, change, or review with evidence.

**Retrieval ladder** — a menu keyed by *question*, **not** a strict try-in-order sequence. Enter at the rung whose question matches yours; among the tools that fit, pick the cheapest; stop once it's answered. (Numbers are rough typical cost, not attempt order — see *Match by fit* below.)
1. **Already known** — it's in `context-map.md`, a task brief, a task report, `progress.md`, or something you read this session. Don't re-query it. *(The biggest lever after codebase-explorer.)*
2. **File listing** (specific pattern) — "which file(s)?" by name/path; discover layout & naming. Paths only, near-zero tokens.
3. **`rg -n`** (scoped) — "where does this identifier / string / route / config key / error message / import appear?" Returns `path:line: matched line`. Keep `-n` because it feeds a targeted read; narrow with path/type globs; use file-list/count modes when a tally or file list is all you need. The workhorse for usages and for anything that isn't a clean AST symbol.
4. **`codegraph_*`** (structural/relational) — what text search can't answer cheaply: `codegraph_search` (locate a *defined* symbol + kind/signature in one shot), `codegraph_node` (exact signature/source without opening the file), `codegraph_callers`/`callees` (control/data flow), `codegraph_impact` (blast radius), `codegraph_context` (focused area). Trust these — don't re-verify with grep.
5. **Targeted file read** around a known line/symbol — read just the region `rg`/codegraph pointed at; don't load a whole file for one function.
6. **Full file read** — when you genuinely need the entire file.
7. **`codegraph_explore` / broad multi-file reads** — heaviest. Reserve for genuine "new to this module" surveys, and prefer to spend it **once, in `codebase-explorer`**, then hand the result down through `context-map.md` and task briefs — not repeatedly in later agents.

**Choose `rg` / file listing over codegraph** when the target isn't a clean AST symbol or you need textual reach: strings, routes, env vars, feature flags, error/log messages, JSON/YAML/SQL/shell keys; every textual usage including comments, tests, templates; dynamic dispatch / DI-by-string / metaprogramming that static edges miss; a quick yes-no or count; or when codegraph returns nothing for something you know exists.

**Choose codegraph over `rg`** when the question is relational — what calls X, what X calls, what breaks if X changes, X's exact signature — or you'd otherwise text-search-walk the whole repo. One `codegraph_callers` / `codegraph_impact` beats walking callers one match at a time.

**Match by fit, then by cost — don't walk the rungs blindly.** `rg` is **not** universally cheaper-or-better than codegraph: for a relational question you go **straight to `codegraph_*`** (it's the cheapest *and* best move there — you don't text-search first), and for a textual/file question you go straight to `rg -n` / file listing. The selector is always *which tool fits this exact question*; only when several fit does cost break the tie. "Climbing" applies *within* the fitting tool (for example `rg -n` → targeted read → full file read), not as an `rg`-before-codegraph rule.

**codegraph failure modes → fall back, don't stall:**
- *Not initialized* (`.codegraph/` absent) → file listing + `rg -n` + targeted reads; offer to run `codegraph init -i`.
- *Index lag* (~500 ms behind a just-saved edit) → wait a turn, or use `rg -n` to confirm current state.
- *Symbol missing/partial* (unparsed language/construct, generated code) → use `rg -n` for it before concluding it's absent.

**Cost gradient across the pipeline.** `codebase-explorer` front-loads the one thorough investigation and writes a pointer map. `implementation-planner` turns that map into small task briefs. Implementers start from one brief and report any missing context as `PACK_GAP`; reviewers start from briefs, reports, and diffs. Every later lookup must fill a genuine gap or named risk using the cheapest fitting tool. The bar never drops: every read-cut is paired with verification (BDD/TDD, tests, `codegraph_impact`, Playwright where relevant). If the cheap tool leaves real doubt, climb — never trade correctness for tokens.

<!-- context7 -->
Use the `ctx7` CLI to fetch current documentation whenever the user asks about a library, framework, SDK, API, CLI tool, or cloud service -- even well-known ones like React, Next.js, Prisma, Express, Tailwind, Django, or Spring Boot. This includes API syntax, configuration, version migration, library-specific debugging, setup instructions, and CLI tool usage. Use even when you think you know the answer -- your training data may not reflect recent changes. Prefer this over web search for library docs.

Do not use for: refactoring, writing scripts from scratch, debugging business logic, code review, or general programming concepts.

## Steps

1. Resolve library: `npx ctx7@latest library <name> "<user's question>"` — use the official library name with proper punctuation (e.g., "Next.js" not "nextjs", "Customer.io" not "customerio", "Three.js" not "threejs")
2. Pick the best match (ID format: `/org/project`) by: exact name match, description relevance, code snippet count, source reputation (High/Medium preferred), and benchmark score (higher is better). If results don't look right, try alternate names or queries (e.g., "next.js" not "nextjs", or rephrase the question)
3. Fetch docs: `npx ctx7@latest docs <libraryId> "<user's question>"`
4. Answer using the fetched documentation

You MUST call `library` first to get a valid ID unless the user provides one directly in `/org/project` format. Use the user's full question as the query -- specific and detailed queries return better results than vague single words. Do not run more than 3 commands per question. Do not include sensitive information (API keys, passwords, credentials) in queries.

For version-specific docs, use `/org/project/version` from the `library` output (e.g., `/vercel/next.js/v14.3.0`).

If a command fails with a quota error, inform the user and suggest `npx ctx7@latest login` or setting `CONTEXT7_API_KEY` env var for higher limits. Do not silently fall back to training data.
Run Context7 CLI requests outside Codex's default sandbox. If a Context7 CLI command fails with DNS or network errors such as ENOTFOUND, host resolution failures, or fetch failed, rerun it outside the sandbox instead of retrying inside the sandbox.
<!-- context7 -->
