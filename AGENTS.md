For top-level Codex sessions, any programming or software-engineering task must apply the `orchestrator` skill first. For non-trivial code changes, this is a standing explicit request to use Codex subagent workflows and the custom agents in `$CODEX_HOME\agents\` (i.e. `~/.codex/agents/`) when the skill's lane calls for delegation. If you are running as any Codex subagent/delegated specialist, including `codebase-explorer`, `integration-researcher`, `implementation-planner`, `task-implementer-bdd`, `implementation-reviewer`, or `root-cause-debugger`, or if you were explicitly dispatched as a delegated specialist by an external orchestrator (for example through `codex exec` or a rescue forwarder), this requirement is already satisfied by the parent orchestrator: do not apply or invoke `orchestrator`; follow your specialist prompt directly.

For any work that involves **frontend / UI** (building or reshaping a page, component, layout, screen, or visual design), ALWAYS also apply the available frontend skills (especially `frontend-one`, plus any relevant framework/design skill) — **both when planning and when implementing**, never just one. They set the visual/UX bar the work must meet.

When work is delegated to a Codex subagent, that work unit has one owner. Write permission follows the deliverable: any delegated specialist that must write files — task reports, diagnosis artifacts, bundle files, code — runs write-capable; specialists must not refuse or skip writing their own artifacts for lack of permissions, and the orchestrator must not accept a "no write permission" complaint as a result — fix the dispatch and re-delegate. While a delegated agent runs, the orchestrator remains suspended until it returns a terminal result, question, gap, or failure: no reading files, no `rg`/CodeGraph/tests, no pre-solving the delegated work, unless it explicitly switches back to the Direct lane for a genuinely trivial remaining action. Progress notices, when the host requires them, come from the pending tool call and never create model turns or status polls.

Dispatch backends (`native-collab` vs resumable `codex-exec`), passive waiting, agent affinity and reuse, durable-job retention and the workflow-close cleanup gate, and per-work-unit model routing on the approved intelligence scale are all defined in `skills/orchestrator/SKILL.md` and its references. The orchestrator applies them at dispatch time; specialists receive their role, model, and reasoning effort in the dispatch itself and never choose their own.

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

## Code retrieval — cheapest sufficient tool

Complements the CodeGraph table above with the textual side and the overall method. For each thing you need to know, use the cheapest tool that fully answers it; climb to a heavier tool only when the cheaper one can't. Quality is the floor — if you genuinely must read it all, read it all — but among tools that clear the bar pick the cheapest, and never re-fetch what you already have.

**Ladder** — a menu keyed by question, not a try-in-order sequence: (1) already known — it's in `context-map.md`, a task brief, a report, `progress.md`, or something read this session: don't re-query; (2) file listing (specific pattern) — "which file(s)?", paths only; (3) `rg -n` (scoped) — "where does this identifier / string / route / config key / env var / error message / import appear?"; keep `-n` so it feeds a targeted read, narrow with path/type globs, use file-list/count modes when a tally suffices; (4) `codegraph_*` per the table above; (5) targeted read around a known line/symbol; (6) full file read; (7) `codegraph_explore` / broad multi-file reads — reserve for genuine "new to this module" surveys, and prefer spending that once in `codebase-explorer`, handed down through `context-map.md` and task briefs. Enter at the rung whose question matches yours; among fitting tools pick the cheapest; stop once answered. For a relational question go **straight to codegraph** — don't text-search first; for a textual/file question go straight to `rg -n` / file listing. "Climbing" applies within the fitting tool (`rg -n` → targeted read → full read), never as an rg-before-codegraph rule.

**Choose `rg`/file listing over codegraph** when the target isn't a clean AST symbol or you need textual reach: strings, routes, env vars, feature flags, error/log messages, JSON/YAML/SQL/shell keys; every textual usage (comments, tests, templates); dynamic dispatch / DI-by-string / metaprogramming that static edges miss; a quick yes-no or count; or when codegraph returns nothing for something you know exists (then `rg -n` before concluding absence).

**Discipline:** retrieval is question-driven and adaptive. Start broad only when the area or failure mode is genuinely uncertain; once paths, symbols, strings, routes, contracts, or tests are known, switch to exact search/symbol tools and targeted reads. Widen again only for a material doubt, named risk, or artifact gap that could change the design, implementation, or verdict — and record why. Stop reading when you can safely produce the artifact, change, or review with evidence. Every read-cut is paired with verification (BDD/TDD, tests, `codegraph_impact`, Playwright where relevant); if the cheap tool leaves real doubt, climb — never trade correctness for tokens.

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
