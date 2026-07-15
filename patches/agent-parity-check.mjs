#!/usr/bin/env node
/**
 * Drift detector for the six specialist role twins:
 *   ~/.claude/agents/<role>.md   (body after YAML frontmatter)
 *   ~/.codex/agents/<role>.toml  (developer_instructions ''' block)
 *
 * Splits both bodies into `## `-heading sections, normalizes known
 * intentional token differences (CLAUDE.md<->AGENTS.md, rg<->grep wording),
 * and reports per-section: MATCH, DRIFT <similarity%>, or ONLY-IN-ONE.
 *
 * This is a detector, not a gate: some sections diverge by design
 * (Claude-side two-engine notes, Codex-side External Dispatch/owner fields).
 * Its job is to make *new* drift visible after either side is edited.
 *
 * Usage: node agent-parity-check.mjs [--fail-under <pct>] [--role <name>]
 *   --fail-under N  exit 1 if any common section's similarity < N (default: report only)
 *   --role <name>   check a single role
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const ROLES = [
  "codebase-explorer",
  "integration-researcher",
  "implementation-planner",
  "task-implementer-bdd",
  "implementation-reviewer",
  "root-cause-debugger"
];

// Sections that exist on one side only, by design. Reported as info, never drift.
const EXPECTED_ONE_SIDED = new Set([
  "External Dispatch",         // codex: codex-exec dispatch contract
  "Model Routing",             // codex planner: owns downstream profile routing
  "Planning-Engine Invariance" // claude: two-engine provenance rules
]);

const argv = process.argv.slice(2);
const failUnderIdx = argv.indexOf("--fail-under");
const failUnder = failUnderIdx !== -1 ? Number(argv[failUnderIdx + 1]) : null;
const roleIdx = argv.indexOf("--role");
const onlyRole = roleIdx !== -1 ? argv[roleIdx + 1] : null;

const home = os.homedir();

function extractMdBody(file) {
  const src = fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n");
  const m = src.match(/^---\n[\s\S]*?\n---\n/);
  return m ? src.slice(m[0].length) : src;
}

function extractTomlInstructions(file) {
  const src = fs.readFileSync(file, "utf8").replace(/\r\n/g, "\n");
  const m = src.match(/^developer_instructions\s*=\s*'''\n?([\s\S]*?)'''\s*$/m);
  if (!m) throw new Error(`no developer_instructions ''' block in ${file}`);
  return m[1];
}

/** Canonicalize both sides so intentional cross-CLI wording is not drift. */
function normalize(text) {
  return text
    .replace(/AGENTS\.md/g, "CLAUDE.md")
    .replace(/`rg -n`|`rg`|\brg -n\b|\bgrep\b|\bexact search\b/g, "textsearch")
    .replace(/\(the Agent tool is disabled for this role\)/g, "")
    .replace(/\s+,/g, ",")
    .replace(/[ \t]+/g, " ")
    .replace(/ +\n/g, "\n")
    .trim();
}

/** Split on `## ` headings, fence-aware: headings inside ``` blocks (the brief/report templates) stay in their parent section. */
function splitSections(body) {
  const sections = new Map();
  let title = "(preamble)";
  let buf = [];
  let inFence = false;
  for (const line of body.split("\n")) {
    if (/^\s*```/.test(line)) inFence = !inFence;
    const h = !inFence && line.match(/^## (\S.*)$/);
    if (h) {
      sections.set(title, buf.join("\n"));
      title = h[1].trim();
      buf = [];
    } else {
      buf.push(line);
    }
  }
  sections.set(title, buf.join("\n"));
  return sections;
}

/** Tokenize to sentences/bullets so a one-sentence delta inside a paragraph doesn't zero the whole section. */
function tokens(text) {
  return normalize(text)
    .split("\n")
    .flatMap((l) => l.split(/(?<=[.?])\s+(?=[A-Z`\d])/))
    .map((t) => t.trim())
    .filter(Boolean);
}

function similarity(a, b) {
  const ta = tokens(a);
  const tb = tokens(b);
  if (!ta.length && !tb.length) return 1;
  const bag = new Map();
  for (const t of tb) bag.set(t, (bag.get(t) ?? 0) + 1);
  let common = 0;
  for (const t of ta) {
    const n = bag.get(t);
    if (n) {
      common++;
      bag.set(t, n - 1);
    }
  }
  return (2 * common) / (ta.length + tb.length);
}

function firstDiffLine(a, b) {
  const ta = tokens(a);
  const tb = tokens(b);
  const setB = new Set(tb);
  for (const t of ta) if (!setB.has(t)) return `claude-only: ${t.slice(0, 100)}`;
  const setA = new Set(ta);
  for (const t of tb) if (!setA.has(t)) return `codex-only:  ${t.slice(0, 100)}`;
  return "";
}

let worst = 1;
let hadError = false;

for (const role of ROLES) {
  if (onlyRole && role !== onlyRole) continue;
  const mdPath = path.join(home, ".claude", "agents", `${role}.md`);
  const tomlPath = path.join(home, ".codex", "agents", `${role}.toml`);
  console.log(`\n=== ${role} ===`);
  let md, toml;
  try {
    md = splitSections(extractMdBody(mdPath));
    toml = splitSections(extractTomlInstructions(tomlPath));
  } catch (err) {
    console.log(`  ERROR ${err.message}`);
    hadError = true;
    continue;
  }
  const titles = new Set([...md.keys(), ...toml.keys()]);
  for (const t of titles) {
    const inMd = md.has(t);
    const inToml = toml.has(t);
    if (inMd && inToml) {
      const sim = similarity(md.get(t), toml.get(t));
      worst = Math.min(worst, sim);
      const pct = Math.round(sim * 100);
      if (sim >= 0.999) {
        console.log(`  MATCH        ${t}`);
      } else {
        const hint = firstDiffLine(md.get(t), toml.get(t));
        console.log(`  DRIFT ${String(pct).padStart(3)}%   ${t}${hint ? `\n               ${hint}` : ""}`);
      }
    } else {
      const side = inMd ? "claude-only" : "codex-only ";
      const marker = EXPECTED_ONE_SIDED.has(t) ? "expected" : "check";
      console.log(`  ${side}  ${t}  (${marker})`);
    }
  }
}

console.log(
  `\nNote: 100% match is not the goal — cross-CLI sections legitimately differ. ` +
    `Investigate NEW drift, sections that dropped sharply, and unexpected one-sided sections.`
);
if (hadError) process.exit(2);
if (failUnder !== null && worst * 100 < failUnder) process.exit(1);
