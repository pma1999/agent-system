For top-level OpenCode sessions, any programming or software-engineering task must apply the `opencode-orchestrator` skill first. The Claude-compatible skill named `orchestrator` is intentionally denied in OpenCode: never load or invoke it here; it contains Claude Code runtime mechanics. If you are running as any delegated specialist subagent, including `codebase-explorer`, `integration-researcher`, `implementation-planner`, `task-implementer-bdd`, `implementation-reviewer`, or `root-cause-debugger`, this requirement is already satisfied by the parent orchestrator: do not apply or invoke `opencode-orchestrator`; follow your specialist prompt directly.

For any work that involves **frontend / UI** (building or reshaping a page, component, layout, screen, or visual design), ALWAYS also apply the available frontend skills (e.g. `frontend-one`, `frontend` — names may vary; apply whatever frontend/design skills exist) — **both when planning and when implementing**, never just one. They set the visual/UX bar the work must meet.

## Code retrieval — cheapest sufficient tool

A CodeGraph MCP server (`codegraph_*` tools, registered with the MCP server prefix) is configured: a tree-sitter-parsed knowledge graph of every symbol, edge, and file, with sub-millisecond reads that return structural information grep cannot. Use it for **structural/relational** questions; use `glob`/`grep` for **textual** ones. For each thing you need to know, use the cheapest tool that fully answers it; climb to a heavier tool only when the cheaper one can't. Quality is the floor — if you genuinely must read it all, read it all — but among tools that clear the bar pick the cheapest, and never re-fetch what you already have.

| Question | Tool |
|---|---|
| "Which file(s)?" by name/path/layout | `glob` (paths only, near-zero tokens) |
| "Where does this identifier / string / route / config key / env var / error message / import appear?" | `grep` with line numbers, scoped with `include`/`path`; `files_with_matches`-style file lists when a tally or file list suffices |
| "Where is symbol X defined?" + kind/signature | `codegraph_search` |
| "X's exact signature / source / docstring" | `codegraph_node` |
| "What calls X?" / "What does X call?" | `codegraph_callers` / `codegraph_callees` |
| "What breaks if X changes?" (blast radius) | `codegraph_impact` |
| "Focused context for a task/area" | `codegraph_context` (one call — don't chain search + node) |
| "Survey an unfamiliar module/topic" | `codegraph_explore` (token-heavy; prefer spending it once in `codebase-explorer`) |
| "Is the index healthy?" / "What files exist under path/" | `codegraph_status` / `codegraph_files` |

**Ladder** — a menu keyed by question, not a try-in-order sequence: (1) already known — it's in `context-map.md`, a task brief, a report, `progress.md`, or something read this session: don't re-query; (2) `glob`; (3) `grep -n`; (4) `codegraph_*`; (5) targeted `read` (`offset`/`limit` around a known line); (6) full `read`; (7) `codegraph_explore` / broad multi-file reads. Enter at the rung whose question matches yours; among fitting tools pick the cheapest; stop once answered. For a relational question go **straight to codegraph** — don't grep first; for a textual/file question go straight to `grep -n`/`glob`. "Climbing" applies within the fitting tool (`grep -n` → targeted read → full read), never as a grep-before-codegraph rule.

**Choose grep/glob over codegraph** when the target isn't a clean AST symbol or you need textual reach: strings, routes, env vars, feature flags, error/log messages, JSON/YAML/SQL/shell keys; every textual usage (comments, tests, templates); dynamic dispatch / DI-by-string / metaprogramming that static edges miss; a quick yes-no or count; or when codegraph returns nothing for something you know exists. **Choose codegraph over grep** when the question is relational — what calls X, what X calls, what breaks, X's exact signature — or you'd otherwise grep-sweep the repo. Trust codegraph structural results; do not re-verify them with grep.

**Fallbacks:** *not initialized* (`.codegraph/` absent or the MCP server failed to start) → `glob` + `grep -n` + targeted reads; offer to run `codegraph init -i`. *Index lag* (~500 ms behind writes) → wait a turn or confirm with `grep -n`; don't re-query right after editing. *Symbol missing/partial* (unparsed language/construct, generated code) → `grep -n` before concluding absence.

**Discipline:** retrieval is question-driven and adaptive. Start broad only when the area or failure mode is genuinely uncertain; once paths, symbols, strings, routes, contracts, or tests are known, switch to exact search/symbol tools and targeted reads. Widen again only for a material doubt, named risk, or artifact gap that could change the design, implementation, or verdict — and record why. Stop reading when you can safely produce the artifact, change, or review with evidence. Every read-cut is paired with verification (tests, `codegraph_impact`, real flows); if the cheap tool leaves real doubt, climb — never trade correctness for tokens.

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
<!-- context7 -->
