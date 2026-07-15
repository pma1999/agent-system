For top-level Claude sessions, any programming or software-engineering task must apply the `orchestrator` skill first. If you are running as any delegated specialist subagent, including `codebase-explorer`, `integration-researcher`, `implementation-planner`, `task-implementer-bdd`, `implementation-reviewer`, `root-cause-debugger`, or `codex:codex-rescue`, this requirement is already satisfied by the parent orchestrator: do not apply or invoke `orchestrator`; follow your specialist prompt directly.

For any work that involves **frontend / UI** (building or reshaping a page, component, layout, screen, or visual design), ALWAYS also apply the available frontend skills (e.g. `frontend`, `frontend-design` — names may vary; apply whatever frontend/design skills exist) — **both when planning and when implementing**, never just one. They set the visual/UX bar the work must meet.

The orchestrator only orchestrates. It chooses the lane, gathers requirements, routes artifacts, gives specialists complete inputs, tracks progress, applies quality gates, and synthesizes specialist outputs for the user. It does not pre-write the planner's plan, debugger's diagnosis, implementer's solution, researcher's contract, or reviewer's verdict; those conclusions belong to the delegated specialist unless already settled by the user or an upstream artifact.

When `orchestrator` is used for non-trivial work, prefer artifact handoffs over pasted context: `codebase-explorer` writes `plans/<slug>/context-map.md`, `implementation-planner` writes a plan bundle with `plan.md`, `global-constraints.md`, `task-<id>-brief.md`, and `progress.md`, implementers work from one task brief and write one task report, and reviewers start from briefs/reports/diffs. Do not make downstream agents read the whole plan or accumulated history; if a brief lacks required context, treat it as `PACK_GAP` and repair the artifact.

Token discipline never lowers the quality bar. Agents should avoid repeated discovery, not necessary discovery: explore enough to map the area, research integrations enough to verify the needed contract, plan to an expert maintainable design, implement with meaningful tests, and review from evidence. If a cheap read leaves real doubt, widen deliberately and record why.

In orchestrator workflows, choose models explicitly from Sonnet or Haiku only for Claude subagents. Use Sonnet by default for planning, exploration, integration research, implementation, debugging, and review. Use Haiku only for truly mechanical, isolated work with complete briefs and no material judgment call. Codex delegation is separate: leave Codex `--model`/`--effort` unset so `~/.codex/config.toml` governs for implementation, review, and diagnosis. The only standing exception is explicitly user-requested Codex planning, whose per-run model/effort selection follows the orchestrator skill's Codex Planning section and never propagates to implementer dispatches.

In orchestrated work, Codex is reached only through the `codex:codex-rescue` subagent per the orchestrator skill's Codex Delegation section, for exactly four uses: explicitly user-requested plan-bundle authoring, equal-rank peer implementation of task briefs (targeting a ~50/50 effort split with `task-implementer-bdd` per Implementer Routing), criteria-gated adversarial second-opinion review, and automatic second diagnosis when the debugger is BLOCKED or below high confidence. Planning is never routed to Codex proactively: without an explicit user request, `implementation-planner` on Sonnet remains the default. Read-only review/diagnosis output is preserved verbatim; planners and implementers instead own their normal workflow artifacts. A failed Codex run is never hidden, planner fallback follows the skill's explicit retry/fallback contract, and Codex-suggested fixes are never auto-applied outside the fix loop.

In orchestrated work, each artifact has one owner and one purpose. Keep `progress.md` as a ledger, not a narrative; record planning engine/model/effort/fallback there as compact provenance, never as implementation routing input. Keep task reports as implementation deltas, not plan summaries; keep reviews as verdict/evidence. Task review is optional and should run only when it gates dependent work, covers a risky/shared contract, or addresses concerns; final review remains the normal quality gate. Agent completion messages should be short and point to artifacts instead of repeating them.

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
2. **`Glob`** (specific pattern) — "which file(s)?" by name/path; discover layout & naming. Paths only, near-zero tokens (e.g. `**/*Repository.ts`, `**/User*.tsx`).
3. **`Grep -n`** (scoped) — "where does this identifier / string / route / config key / error message / import appear?" Returns `path:line: matched line`. Keep `-n` (it feeds a targeted Read); narrow with `glob`/`path`/`type`; use `output_mode: count`/`files_with_matches` when a tally or file list is all you need. The workhorse for usages and for anything that isn't a clean AST symbol.
4. **`codegraph_*`** (structural/relational) — what grep can't answer cheaply: `codegraph_search` (locate a *defined* symbol + kind/signature in one shot), `codegraph_node` (exact signature/source without opening the file), `codegraph_callers`/`callees` (control/data flow), `codegraph_impact` (blast radius), `codegraph_context` (focused area). Trust these — don't re-verify with grep.
5. **Targeted `Read`** (`offset`/`limit` around a known line) — read just the region grep/codegraph pointed at; don't load a whole file for one function.
6. **Full `Read`** — when you genuinely need the entire file.
7. **`codegraph_explore` / broad multi-file reads** — heaviest. Reserve for genuine "new to this module" surveys, and prefer to spend it **once, in `codebase-explorer`**, then hand the result down through `context-map.md` and task briefs — not repeatedly in later agents.

**Choose grep/glob over codegraph** when the target isn't a clean AST symbol or you need textual reach: strings, routes, env vars, feature flags, error/log messages, JSON·YAML·SQL·shell keys; *every textual usage* (incl. comments, tests, templates); dynamic dispatch / DI-by-string / metaprogramming that static edges miss; a quick yes-no or count; or when codegraph returns nothing for something you know exists (tree-sitter may not parse that language/construct).

**Choose codegraph over grep** when the question is relational — what calls X, what X calls, what breaks if X changes, X's exact signature — or you'd otherwise grep-sweep the whole repo. One `codegraph_callers` / `codegraph_impact` beats walking callers grep-by-grep.

**Match by fit, then by cost — don't walk the rungs blindly.** grep is **not** universally cheaper-or-better than codegraph: for a relational question you go **straight to `codegraph_*`** (it's the cheapest *and* best move there — you don't grep first), and for a textual/file question you go straight to `Grep -n` / `Glob`. The selector is always *which tool fits this exact question*; only when several fit does cost break the tie. "Climbing" applies *within* the fitting tool (e.g. `Grep -n` → targeted `Read` → full `Read`), not as a grep-before-codegraph rule.

**codegraph failure modes → fall back, don't stall:**
- *Not initialized* (`.codegraph/` absent) → glob + grep -n + Read; offer to run `codegraph init -i`.
- *Index lag* (~500 ms behind a just-saved edit) → wait a turn, or grep -n to confirm current state.
- *Symbol missing/partial* (unparsed language/construct, generated code) → grep -n for it before concluding it's absent.

**Cost gradient across the pipeline.** `codebase-explorer` front-loads the one thorough investigation and writes a pointer map. `implementation-planner` turns that map into small task briefs. Implementers start from one brief and report any missing context as `PACK_GAP`; reviewers start from briefs, reports, and diffs. Every later lookup must fill a genuine gap or named risk using the cheapest fitting tool. The bar never drops: every read-cut is paired with verification (BDD/TDD, tests, `codegraph_impact`, Playwright where relevant). If the cheap tool leaves real doubt, climb — never trade correctness for tokens.
