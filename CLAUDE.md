For top-level Claude sessions, any programming or software-engineering task must apply the `orchestrator` skill first. If you are running as any delegated specialist subagent, including `codebase-explorer`, `integration-researcher`, `implementation-planner`, `task-implementer-bdd`, `implementation-reviewer`, `root-cause-debugger`, or `codex:codex-rescue`, this requirement is already satisfied by the parent orchestrator: do not apply or invoke `orchestrator`; follow your specialist prompt directly.

For any work that involves **frontend / UI** (building or reshaping a page, component, layout, screen, or visual design), ALWAYS also apply the available frontend skills (e.g. `frontend`, `frontend-design` — names may vary; apply whatever frontend/design skills exist) — **both when planning and when implementing**, never just one. They set the visual/UX bar the work must meet.

## Code retrieval — cheapest sufficient tool

A CodeGraph MCP server (`codegraph_*` tools) is configured: a tree-sitter-parsed knowledge graph of every symbol, edge, and file, with sub-millisecond reads that return structural information grep cannot. Use it for **structural/relational** questions; use Glob/Grep for **textual** ones. For each thing you need to know, use the cheapest tool that fully answers it; climb to a heavier tool only when the cheaper one can't. Quality is the floor — if you genuinely must read it all, read it all — but among tools that clear the bar pick the cheapest, and never re-fetch what you already have.

| Question | Tool |
|---|---|
| "Which file(s)?" by name/path/layout | `Glob` (paths only, near-zero tokens) |
| "Where does this identifier / string / route / config key / env var / error message / import appear?" | `Grep -n`, scoped with `glob`/`path`/`type`; `count`/`files_with_matches` when a tally or file list suffices |
| "Where is symbol X defined?" + kind/signature | `codegraph_search` |
| "X's exact signature / source / docstring" | `codegraph_node` |
| "What calls X?" / "What does X call?" | `codegraph_callers` / `codegraph_callees` |
| "What breaks if X changes?" (blast radius) | `codegraph_impact` |
| "Focused context for a task/area" | `codegraph_context` (one call — don't chain search + node) |
| "Survey an unfamiliar module/topic" | `codegraph_explore` (token-heavy; prefer spending it once in `codebase-explorer`) |
| "Is the index healthy?" / "What files exist under path/" | `codegraph_status` / `codegraph_files` |

**Ladder** — a menu keyed by question, not a try-in-order sequence: (1) already known — it's in `context-map.md`, a task brief, a report, `progress.md`, or something read this session: don't re-query; (2) `Glob`; (3) `Grep -n`; (4) `codegraph_*`; (5) targeted `Read` (`offset`/`limit` around a known line); (6) full `Read`; (7) `codegraph_explore` / broad multi-file reads. Enter at the rung whose question matches yours; among fitting tools pick the cheapest; stop once answered. For a relational question go **straight to codegraph** — don't grep first; for a textual/file question go straight to `Grep -n`/`Glob`. "Climbing" applies within the fitting tool (`Grep -n` → targeted Read → full Read), never as a grep-before-codegraph rule.

**Choose Grep/Glob over codegraph** when the target isn't a clean AST symbol or you need textual reach: strings, routes, env vars, feature flags, error/log messages, JSON/YAML/SQL/shell keys; every textual usage (comments, tests, templates); dynamic dispatch / DI-by-string / metaprogramming that static edges miss; a quick yes-no or count; or when codegraph returns nothing for something you know exists. **Choose codegraph over Grep** when the question is relational — what calls X, what X calls, what breaks, X's exact signature — or you'd otherwise grep-sweep the repo. Trust codegraph structural results; do not re-verify them with grep.

**Fallbacks:** *not initialized* (`.codegraph/` absent) → Glob + `Grep -n` + targeted reads; offer to run `codegraph init -i`. *Index lag* (~500 ms behind writes) → wait a turn or confirm with `Grep -n`; don't re-query right after editing. *Symbol missing/partial* (unparsed language/construct, generated code) → `Grep -n` before concluding absence.

**Discipline:** retrieval is question-driven and adaptive. Start broad only when the area or failure mode is genuinely uncertain; once paths, symbols, strings, routes, contracts, or tests are known, switch to exact search/symbol tools and targeted reads. Widen again only for a material doubt, named risk, or artifact gap that could change the design, implementation, or verdict — and record why. Stop reading when you can safely produce the artifact, change, or review with evidence. Every read-cut is paired with verification (tests, `codegraph_impact`, real flows); if the cheap tool leaves real doubt, climb — never trade correctness for tokens.
