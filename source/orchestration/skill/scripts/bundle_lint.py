#!/usr/bin/env python3
"""bundle_lint - deterministic validation of an orchestration plan bundle.

Read-only. Never edits the bundle, never drives the workflow: it reads the
Markdown artifacts, contrasts them with the actual repository, prints findings
and returns an exit code. It is "run the tests" for a plan bundle, not a
workflow controller.

    python bundle_lint.py plans/<slug> --phase pre-approval
    python bundle_lint.py plans/<slug> --phase pre-synthesis
    python bundle_lint.py plans/<slug>            # both phases

Exit codes
    0  no blockers (warnings may still be printed)
    1  at least one blocker
    2  the bundle path is unusable

Findings carry stable IDs (BL-01, BL-02, ...) so a repair round can name them.
Severity is deliberately conservative: only facts that are unambiguously wrong
are blockers. A noisy linter gets ignored, and an ignored gate is worse than no
gate.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------- constants

REQUIRED_BRIEF_SECTIONS = [
    "Goal",
    "Acceptance Criteria",
    "Scope",
    "Interfaces",
    "Context Pack",
    "Tests",
    "Report Path",
]

TERMINAL_STATUSES = {
    "DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_CONTEXT", "PACK_GAP",
    "PASS", "FAIL", "PASS WITH REQUIRED CHANGES",
}

FORBIDDEN_ARTIFACT_PREFIXES = ("report", "summary", "findings", "analysis")

# A path-looking token: has a separator or a known code extension.
PATH_RE = re.compile(r"[\w./\\@~-]*[\w]/[\w./\\@-]+|[\w./\\-]+\.[A-Za-z0-9]{1,6}")

CODEISH_SUFFIXES = {
    ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".py", ".go", ".rs", ".rb",
    ".java", ".kt", ".swift", ".cs", ".php", ".c", ".h", ".cc", ".cpp", ".hpp",
    ".vue", ".svelte", ".astro", ".css", ".scss", ".less", ".html", ".json",
    ".yaml", ".yml", ".toml", ".sql", ".prisma", ".graphql", ".md", ".sh",
    ".ps1", ".tf", ".proto", ".ini", ".cfg", ".env", ".lock", ".xml",
}

# Words that look like paths but are prose, versions or placeholders.
PATH_NOISE = re.compile(
    r"^(?:\.{1,2}|https?:|www\.|e\.g\.|i\.e\.|etc\.|vs\.|\d+(?:\.\d+)+|<.*>|N/?A)$",
    re.I,
)

NEW_FILE_MARKERS = re.compile(
    r"^\s*(?:new|nuevo|nueva)(?:\s+(?:file|fichero|archivo|test|tests?)\b|\s+`)|"
    r"\(\s*(?:new|nuevo|nueva)\b|"
    r"\b(?:new|nuevo|nueva)\s+(?:file|fichero|archivo|test|tests?)\b|"
    r"\((?:to create|create|created|a crear)\)|\bnew file\b|"
    r"\bfichero nuevo\b|\bdoes not exist yet\b|\bno existe a[uú]n\b",
    re.I,
)

RUNNERS_WITH_SCRIPTS = ("npm", "pnpm", "yarn", "bun")

# Review finding identifiers and their small, intentionally explicit status
# vocabulary.  Reviews are Markdown, not a machine-readable format: statuses
# may be on a wrapped continuation line, in a remediation round, or in a
# final per-ID summary.  The parser below understands those documented shapes
# without treating arbitrary prose such as "RC-01 quedó abierto" as the
# current state of the finding.
RC_ID_RE = re.compile(r"`?(RC-\d{2,})`?", re.I)
RC_STATUS_WORD_RE = re.compile(
    r"\b(unresolved|resolved|superseded|accepted|open|"
    r"resuelt(?:o|a|os|as)|superad(?:o|a|os|as)|"
    r"aceptad(?:o|a|os|as)|abiert(?:o|a|os|as))\b",
    re.I,
)
RC_STATUS_LABEL_RE = re.compile(r"\bstatus\s*:\s*(.*)", re.I)
RC_RESULT_LABEL_RE = re.compile(r"\b(?:result|resultado)\s*:\s*(.*)", re.I)
RC_ITEM_START_RE = re.compile(
    r"^\s*[-*]\s+(?:[*_`]+)?(RC-\d{2,})(?:[*_`]+)?\b", re.I
)
MARKDOWN_LIST_START_RE = re.compile(r"^\s*[-*]\s+", re.I)
ROUND_START_RE = re.compile(r"^\s*###\s+", re.I)

LINE_RANGE_RE = re.compile(
    r"(?P<suffix>\.[A-Za-z0-9]{1,8}):\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*$"
)
MODULE_EXTENSIONS = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".json", ".py")
COMMON_REPO_DIRS = {
    "app", "assets", "bin", "components", "config", "data", "docs", "fixtures", "harness",
    "lib", "migrations", "packages", "pages", "prisma", "public", "rendered", "routes",
    "scripts", "source", "src", "styles", "tests", "test", "types",
}

# Directories never searched by the suffix fallback or the bundle inventory:
# version control, dependencies, build outputs and caches.  On slow mounts
# (WSL DrvFs under /mnt/c) an unfiltered recursive walk hangs the lint.
SKIP_DIRS = frozenset({
    ".git", "node_modules", ".venv", "venv", "__pycache__",
    "target", "dist", "build", ".next", ".codegraph", "coverage",
})

# Safety budgets for the suffix fallback below.  Hitting either means the
# tree is too big (or the mount too slow) to prove absence: the lookup
# degrades to "not disproven" and run() records a WARN instead of hanging.
# The walk is name-only and never reads file contents, so these budgets (not
# a file-size cutoff, which could hide a real file and forge a BLOCKER) are
# what bounds the I/O.
_MAX_SUFFIX_WALK_ENTRIES = 200_000
_MAX_SUFFIX_WALK_SECONDS = 10.0

# Per-run cache: (repo root, path suffix) -> exists.  A bundle names the
# same missing path in several briefs/sections; without this each lookup
# pays a full walk.  Keyed by absolute repo so two worktrees never share
# verdicts.
_PATH_SUFFIX_CACHE: dict[tuple[str, str], bool] = {}
# Suffixes whose walk exhausted a budget this run (existence unproven).
_SUFFIX_WALK_DEGRADED: set[tuple[str, str]] = set()


def clear_path_cache() -> None:
    """Reset the suffix cache (tests; a fresh process starts empty anyway)."""
    _PATH_SUFFIX_CACHE.clear()
    _SUFFIX_WALK_DEGRADED.clear()


# ---------------------------------------------------------------- model

@dataclass
class Finding:
    severity: str          # "blocker" | "warn" | "info"
    artifact: str
    message: str
    hint: str = ""
    ident: str = ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)

    def add(self, severity: str, artifact: str, message: str, hint: str = "") -> None:
        self.findings.append(Finding(severity, artifact, message, hint))

    def blocker(self, artifact: str, message: str, hint: str = "") -> None:
        self.add("blocker", artifact, message, hint)

    def warn(self, artifact: str, message: str, hint: str = "") -> None:
        self.add("warn", artifact, message, hint)

    def info(self, artifact: str, message: str, hint: str = "") -> None:
        self.add("info", artifact, message, hint)

    def note(self, what: str) -> None:
        self.checked.append(what)

    def number(self) -> None:
        for i, f in enumerate(self.findings, 1):
            f.ident = f"BL-{i:02d}"

    @property
    def blockers(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "blocker"]


# ---------------------------------------------------------------- markdown helpers

def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        try:
            return p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""


def strip_code_fences(text: str) -> str:
    """Fenced blocks are examples and schemas, not claims about the repo."""
    return re.sub(r"(?ms)^```.*?^```\s*$", "", text)


def sections(text: str) -> dict[str, str]:
    """Map `## Heading` -> body, for level-2 headings."""
    out: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            if current is not None:
                out[current] = "\n".join(buf)
            current = m.group(1).strip()
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        out[current] = "\n".join(buf)
    return out


def normalize_rc_status(raw: str) -> str | None:
    """Map the review vocabulary to the four states the gate understands."""
    m = RC_STATUS_WORD_RE.search(raw)
    if not m:
        return None
    word = m.group(1).lower()
    if word in {"unresolved", "open", "abierto", "abierta", "abiertos", "abiertas"}:
        return "open"
    if word.startswith("resuelt") or word == "resolved":
        return "resolved"
    if word.startswith("superad") or word == "superseded":
        return "superseded"
    if word.startswith("aceptad") or word == "accepted":
        return "accepted"
    return None


def labeled_rc_status(line: str) -> str | None:
    """Read a `Status:` or `Result:` value from one Markdown line."""
    for pattern in (RC_STATUS_LABEL_RE, RC_RESULT_LABEL_RE):
        m = pattern.search(line)
        if m:
            return normalize_rc_status(m.group(1))
    return None


def direct_rc_status(line: str) -> str | None:
    """Read compact summaries such as ``RC-01: resolved``."""
    if not RC_ID_RE.search(line):
        return None
    # A direct ID summary has the state immediately after the separator.  It
    # deliberately does not match `RC-01 quedó abierto` in narrative prose.
    if not re.search(r"RC-\d{2,}\s*(?:[:|—-])", line, re.I):
        return None
    tail = re.split(r"RC-\d{2,}\s*(?:[:|—-])", line, maxsplit=1, flags=re.I)[-1]
    return normalize_rc_status(tail)


def rc_item_blocks(body: str) -> list[tuple[list[str], str]]:
    """Return required-change list items, including wrapped continuation lines."""
    lines = body.splitlines()
    starts = [i for i, line in enumerate(lines) if RC_ITEM_START_RE.match(line)]
    out: list[tuple[list[str], str]] = []
    for start in starts:
        end = len(lines)
        for i in range(start + 1, len(lines)):
            if MARKDOWN_LIST_START_RE.match(lines[i]):
                end = i
                break
        ids = RC_ID_RE.findall(lines[start])
        if ids:
            out.append((ids, "\n".join(lines[start:end])))
    return out


def remediation_rounds(body: str) -> list[str]:
    """Split `Remediation History` into ordered rounds for latest-state wins."""
    lines = body.splitlines()
    starts = [i for i, line in enumerate(lines) if ROUND_START_RE.match(line)]
    if not starts:
        return [body] if body.strip() else []
    out: list[str] = []
    for pos, start in enumerate(starts):
        end = starts[pos + 1] if pos + 1 < len(starts) else len(lines)
        out.append("\n".join(lines[start:end]))
    return out


def review_rc_statuses(text: str) -> tuple[set[str], dict[str, str]]:
    """Collect current RC states without confusing history with the verdict.

    The review template puts the current state at the end of each item in
    `## Required Changes`.  Older artifacts and re-reviews also put it in a
    `Result:` line under `## Remediation History`, sometimes several lines
    after `IDs checked:`.  We parse the latter first and let an explicit
    current Required Changes status win over historical prose.  This keeps a
    preserved Round 0 `open` sentence from reopening a finding resolved in a
    later round, while still blocking a finding whose current item is
    explicitly open.
    """
    clean = strip_code_fences(text)
    all_ids = set(RC_ID_RE.findall(clean))
    statuses: dict[str, str] = {}

    # Remediation rounds are ordered; a later result replaces an earlier one.
    history = sections(clean).get("Remediation History", "")
    for round_text in remediation_rounds(history):
        lines = round_text.splitlines()
        ids: set[str] = set()
        for line in lines:
            if re.search(r"\bids?\b|\bidentificadores?\b", line, re.I):
                ids.update(RC_ID_RE.findall(line))
        if not ids and lines:
            ids.update(RC_ID_RE.findall(lines[0]))

        state: str | None = None
        for line in lines:
            result = labeled_rc_status(line)
            if result:
                state = result
                continue
            # Round-0 artifacts sometimes say `IDs: RC-01 abierto` rather
            # than using a Result label.  Restrict this fallback to ID lines.
            if re.search(r"\bids?\b|\bidentificadores?\b", line, re.I):
                state = normalize_rc_status(line.split(":", 1)[-1]) or state
        if state:
            for rc in ids:
                statuses[rc] = state

    # Compact per-ID summaries and explicit labels anywhere in the review are
    # useful fallback evidence.  Required Changes below remains authoritative.
    for line in clean.splitlines():
        ids = RC_ID_RE.findall(line)
        if not ids:
            continue
        state = labeled_rc_status(line) or direct_rc_status(line)
        if state:
            for rc in ids:
                statuses[rc] = state

    # Current findings are list items.  Their wrapped body may contain the
    # status several lines after the RC identifier.
    for ids, item in rc_item_blocks(sections(clean).get("Required Changes", "")):
        state = None
        for line in item.splitlines():
            state = labeled_rc_status(line) or state
        if state:
            for rc in ids:
                statuses[rc] = state

    return all_ids, statuses


def backticked(text: str) -> list[str]:
    return re.findall(r"`([^`\n]+)`", text)


def table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|") or set(s) <= set("|- :"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if cells and not all(c.lower() in ("file", "symbol / contract", "read-hint", "why",
                                           "symbol/contract", "change", "task", "status")
                             for c in cells):
            rows.append(cells)
    return rows


def normalize_path_token(token: str) -> str:
    """Remove Markdown punctuation and an optional `:line[-line]` suffix."""
    token = token.strip()
    token = LINE_RANGE_RE.sub(r"\g<suffix>", token)
    return token.strip("`*_,;:()[]{}\"' ")


def looks_like_path(token: str) -> bool:
    raw = token.strip()
    # Inline calls such as `vi.mock("../lib/db")` are code examples, not
    # paths asserted by the brief.  Keep real relative module paths, which do
    # not contain call parentheses, eligible for extension resolution below.
    if "(" in raw or ")" in raw:
        return False
    token = normalize_path_token(raw)
    if not token or PATH_NOISE.match(token):
        return False
    # Un token con espacios es prosa o una cabecera de tabla ("Symbol / contract"),
    # no una ruta. Se prefiere no mirar a inventar un hallazgo falso.
    if any(c.isspace() for c in token):
        return False
    if any(ch in token for ch in "<>*?|"):
        return False
    if token.startswith(("http://", "https://", "npm ", "-")):
        return False
    slash_token = token.replace("\\", "/")
    p = Path(token)
    if p.suffix.lower() in CODEISH_SUFFIXES:
        return True
    if "/" not in slash_token or slash_token.endswith(".") or len(token) <= 3:
        return False
    if slash_token.startswith(("./", "../", "/", "~/")):
        return True
    if re.match(r"^[A-Za-z]:/", slash_token):
        return True
    return slash_token.split("/", 1)[0].lower() in COMMON_REPO_DIRS


def candidate_paths(text: str) -> list[str]:
    """Paths asserted by the artifact: backticked tokens and table cells."""
    out: list[str] = []
    for tok in backticked(text):
        for part in re.split(r"\s+|,|;", tok):
            if looks_like_path(part):
                out.append(normalize_path_token(part))
    for line in text.splitlines():
        if line.strip().startswith("|"):
            for cell in line.strip("|").split("|"):
                cell = cell.strip()
                if cell and "`" not in cell and looks_like_path(cell):
                    out.append(normalize_path_token(cell))
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return uniq


def _any_suffix_exists(repo: Path, wanted: set[tuple[str, str]]) -> bool:
    """One bounded walk answering every suffix variant of a single lookup.

    Returns True when a match proves presence *or* when a safety budget
    fires first (absence unproven: never a blocker, run() warns).  Results
    are cached per (repo, suffix) so repeated briefs never re-walk.
    Skips SKIP_DIRS and never follows symlinks.
    """
    uncached = sorted(w for w in wanted if w not in _PATH_SUFFIX_CACHE)
    if not uncached:
        return any(_PATH_SUFFIX_CACHE[w] for w in wanted)
    names = {name for name, _ in uncached}
    suffixes: dict[str, list[str]] = {}
    for name, suffix in uncached:
        suffixes.setdefault(name, []).append(suffix)

    deadline = time.monotonic() + _MAX_SUFFIX_WALK_SECONDS
    seen = 0
    truncated = False
    stack = [repo]
    while stack:
        if time.monotonic() > deadline:
            truncated = True
            break
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                items = []
                for entry in it:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                    except OSError:
                        continue
                    items.append((entry.name, entry.path, is_dir))
        except OSError:
            continue
        for entry_name, entry_path, is_dir in items:
            seen += 1
            if seen > _MAX_SUFFIX_WALK_ENTRIES:
                truncated = True
                break
            if is_dir:
                if entry_name in SKIP_DIRS:
                    continue
                stack.append(Path(entry_path))
            elif entry_name in names:
                try:
                    rel = Path(entry_path).relative_to(repo).as_posix()
                except ValueError:
                    continue
                for suffix in suffixes[entry_name]:
                    if rel.endswith(suffix):
                        _PATH_SUFFIX_CACHE[(entry_name, suffix)] = True
                        return True
        if truncated:
            break

    if truncated:
        # Absence unproven: treat as present (no false blocker) but leave a
        # marker so run() degrades to WARN instead of silently passing.
        for key in uncached:
            _PATH_SUFFIX_CACHE[key] = True
            _SUFFIX_WALK_DEGRADED.add(key)
        return True
    for key in uncached:
        _PATH_SUFFIX_CACHE[key] = False
    return False


def path_exists(repo: Path, rel: str) -> bool:
    rel = normalize_path_token(rel).replace("\\", "/").lstrip("./")
    if not rel:
        return False
    target = repo / rel
    variants = [target]
    if target.suffix == "":
        variants.extend(Path(f"{target}{ext}") for ext in MODULE_EXTENSIONS)
        variants.extend(target / f"index{ext}" for ext in MODULE_EXTENSIONS)
    if any(candidate.exists() for candidate in variants):
        return True
    # A brief may address a file by a suffix of its real path.  One bounded
    # walk covers every variant: the old unfiltered `repo.rglob(name)` hung
    # on slow mounts by strolling through .git/node_modules/.venv.
    wanted = set()
    for variant in variants:
        name = variant.name
        if not name:
            continue
        try:
            suffix = variant.relative_to(repo).as_posix()
        except ValueError:
            continue
        wanted.add((name, suffix))
    if not wanted:
        return False
    try:
        return _any_suffix_exists(repo, wanted)
    except OSError:
        return False


# ---------------------------------------------------------------- checks

def check_brief(repo: Path, bundle: Path, brief: Path, rep: Report) -> dict:
    name = brief.name
    raw = read(brief)
    text = strip_code_fences(raw)
    secs = sections(text)
    info: dict = {"name": name, "touch": set(), "produces": [], "consumes": [], "ui": False}

    missing = [s for s in REQUIRED_BRIEF_SECTIONS if s not in secs]
    if missing:
        rep.blocker(name, f"faltan secciones obligatorias del esquema de brief: {', '.join(missing)}",
                    "el implementador no puede ejecutar desde un brief incompleto")

    info["ui"] = "UI Contract" in secs
    if info["ui"]:
        ui = secs["UI Contract"]
        if not re.search(r"\bstates?\b|estados", ui, re.I):
            rep.warn(name, "UI Contract sin matriz de estados declarada")
        if not re.search(r"\bskill", ui, re.I):
            rep.warn(name, "UI Contract no nombra las skills de diseño que el implementador debe cargar")
        if not re.search(r"\d{3,4}\s*px|breakpoint", ui, re.I):
            rep.warn(name, "UI Contract sin breakpoints concretos; la evidencia visual no será comparable")

    # Paths asserted in the sections that point at repository reality.
    for sec in ("Context Pack", "Scope", "Existing Patterns To Reuse", "Tests"):
        body = secs.get(sec, "")
        if not body:
            continue
        for line in body.splitlines():
            if NEW_FILE_MARKERS.search(line):
                continue
            for cand in candidate_paths(line):
                if cand.startswith("plans/"):
                    continue
                if not path_exists(repo, cand):
                    rep.blocker(name, f"{sec}: la ruta `{cand}` no existe en el worktree",
                                "márcala como (new) si el brief la crea, o corrige el puntero")

    # Scope -> touch set
    scope = secs.get("Scope", "")
    touch_block = scope.split("Do not touch", 1)[0]
    for cand in candidate_paths(touch_block):
        info["touch"].add(cand.replace("\\", "/").lstrip("./"))
    if "Scope" in secs and not info["touch"]:
        rep.warn(name, "Scope sin `Touch:` reconocible; la disjunción de olas no se puede comprobar")

    # Interfaces
    iface = secs.get("Interfaces", "")
    cur = None
    for line in iface.splitlines():
        low = line.strip().lower()
        if low.startswith("consumes"):
            cur = "consumes"
            continue
        if low.startswith("produces"):
            cur = "produces"
            continue
        if cur and line.strip().startswith(("-", "*")):
            syms = backticked(line)
            info[cur].extend(s.strip() for s in syms if s.strip())

    # Tests
    tests = secs.get("Tests", "")
    if tests.strip() and not backticked(tests):
        rep.blocker(name, "la sección Tests no nombra ningún comando ni fichero concreto",
                    "«add tests» no es verificación; hace falta comando, escenario y señal red/green")
    for line in tests.splitlines():
        if NEW_FILE_MARKERS.search(line):
            continue
        for cmd in backticked(line):
            problem = unresolvable_command(repo, cmd)
            if problem:
                rep.blocker(name, f"Tests: {problem}",
                            "el implementador no puede producir la señal RED/GREEN pedida")
    if tests and not re.search(r"\bred\b|\bgreen\b|rojo|verde|fail|pass", tests, re.I):
        rep.warn(name, "Tests sin señal roja/verde esperada declarada")

    # Report path
    rp = secs.get("Report Path", "")
    for cand in backticked(rp):
        if not cand.startswith("plans/"):
            rep.warn(name, f"Report Path `{cand}` fuera del bundle")
        base = Path(cand).stem.lower()
        if base.startswith(FORBIDDEN_ARTIFACT_PREFIXES):
            rep.blocker(name, f"Report Path `{cand}` usa un nombre de artefacto prohibido",
                        "algunos runtimes bloquean escrituras de subagente a esos nombres")
    return info


def unresolvable_command(repo: Path, cmd: str) -> str:
    """Only reports what can be *proven* wrong. Silence means 'not disproven'."""
    cmd = cmd.strip()
    if not cmd or cmd.startswith(("#", "<")):
        return ""
    parts = cmd.split()
    head = parts[0]

    # `npm run <script>` / pnpm / yarn / bun
    if head in RUNNERS_WITH_SCRIPTS and len(parts) >= 3 and parts[1] == "run":
        script = parts[2]
        pkg = repo / "package.json"
        if pkg.exists():
            try:
                scripts = json.loads(read(pkg)).get("scripts", {})
            except (ValueError, TypeError):
                return ""
            if script not in scripts:
                near = ", ".join(sorted(scripts)[:8]) or "ninguno"
                return (f"`{cmd}` no existe: package.json no define el script "
                        f"`{script}` (hay: {near})")
        return ""

    # `make <target>`
    if head == "make" and len(parts) >= 2 and not parts[1].startswith("-"):
        mk = repo / "Makefile"
        if mk.exists() and not re.search(rf"(?m)^{re.escape(parts[1])}\s*:", read(mk)):
            return f"`{cmd}` no existe: el Makefile no define el target `{parts[1]}`"
        return ""

    # A file argument that must exist (pytest path, vitest path, ...)
    for arg in parts[1:]:
        if arg.startswith("-"):
            continue
        base = arg.split("::")[0].split(":")[0]
        if looks_like_path(base) and Path(base).suffix.lower() in CODEISH_SUFFIXES:
            if not path_exists(repo, base) and not NEW_FILE_MARKERS.search(cmd):
                return f"`{cmd}` apunta a `{base}`, que no existe en el worktree"
    return ""


def check_wave_disjointness(briefs: list[dict], plan_text: str, rep: Report) -> None:
    waves = parse_waves(plan_text)
    for i, a in enumerate(briefs):
        for b in briefs[i + 1:]:
            shared = a["touch"] & b["touch"]
            if not shared:
                continue
            same = same_wave(a["name"], b["name"], waves)
            msg = (f"{a['name']} y {b['name']} declaran el mismo Touch: "
                   f"{', '.join(sorted(shared))}")
            if same is True:
                rep.blocker("plan.md", msg + " y están en la misma ola",
                            "tareas con ficheros compartidos van en olas secuenciales")
            elif same is None:
                rep.warn("plan.md", msg + "; no se pudo leer su ola en plan.md",
                         "confirma que no se despachan en paralelo")


def parse_waves(plan_text: str) -> dict[str, str]:
    """task id -> wave label, from any line that names a wave and task ids."""
    out: dict[str, str] = {}
    current = None
    for line in plan_text.splitlines():
        m = re.search(r"\b(?:wave|ola)\s*([0-9A-Za-z]+)", line, re.I)
        if m:
            current = m.group(1).lower()
        for tid in re.findall(r"\btask[-\s]?([0-9]{1,3}[a-z]?)\b", line, re.I):
            if current:
                out.setdefault(tid.lower(), current)
        if m and not re.search(r"task", line, re.I):
            continue
    return out


def task_id(filename: str) -> str:
    m = re.search(r"task-([0-9]{1,3}[a-z]?)-", filename, re.I)
    return m.group(1).lower() if m else ""


def same_wave(fa: str, fb: str, waves: dict[str, str]):
    a, b = waves.get(task_id(fa)), waves.get(task_id(fb))
    if a is None or b is None:
        return None
    return a == b


def check_interface_reciprocity(briefs: list[dict], rep: Report) -> None:
    produced = {}
    for b in briefs:
        for sym in b["produces"]:
            produced.setdefault(sym, b["name"])
    consumed = {}
    for b in briefs:
        for sym in b["consumes"]:
            consumed.setdefault(sym, b["name"])
    for sym, owner in consumed.items():
        if sym in produced:
            continue
        rep.info(owner, f"consume `{sym}`, que ninguna otra tarea declara producir",
                 "correcto si ya existe en el repo; revisa si falta una tarea")


def check_progress(bundle: Path, rep: Report, pre_synthesis: bool) -> None:
    p = bundle / "progress.md"
    if not p.exists():
        rep.warn("progress.md", "el bundle no tiene ledger de coordinación")
        return
    text = read(p)
    if not re.search(r"(?mi)^\s*Baseline\s*:", text):
        rep.blocker("progress.md", "no registra `Baseline:`",
                    "sin baseline el reviewer no puede separar tu delta del trabajo previo")
    if not re.search(r"(?mi)^\s*(Pre-existing changes|Cambios preexistentes)\s*:", text):
        rep.warn("progress.md", "no registra los cambios preexistentes del worktree")
    if not pre_synthesis:
        return
    for row in table_rows(text):
        if len(row) < 3:
            continue
        label = row[0]
        if not re.search(r"task|tarea|[0-9]", label, re.I):
            continue
        cells = " ".join(row).upper()
        if any(s in cells for s in TERMINAL_STATUSES):
            continue
        if re.search(r"PENDING|IN.?PROGRESS|RUNNING|-\s*$", " ".join(row), re.I):
            rep.blocker("progress.md", f"la fila `{label}` no tiene estado terminal",
                        "no se sintetiza con trabajo sin cerrar")
    # Dueño perdido: una fila cerrada cuya columna Owner quedó vacía. Se localiza
    # la columna por su cabecera, no por posición, porque el ledger la coloca
    # donde quiera.
    header, idx = None, None
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip().lower() for c in line.strip().strip("|").split("|")]
        if "owner" in cells and header is None:
            header, idx = cells, cells.index("owner")
            continue
        if idx is None or set(line.strip()) <= set("|- :"):
            continue
        row = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(row) <= idx:
            continue
        closed = any(s in " ".join(row).upper() for s in TERMINAL_STATUSES)
        if closed and row[idx] in ("", "-"):
            rep.warn("progress.md", f"la fila `{row[0]}` está cerrada y no registra dueño",
                     "regístralo o márcalo stale explícitamente antes de sintetizar")


def check_reports_and_reviews(bundle: Path, rep: Report) -> None:
    for brief in sorted(bundle.glob("task-*-brief.md")):
        tid = task_id(brief.name)
        report = bundle / f"task-{tid}-report.md"
        if not report.exists():
            rep.blocker(brief.name, f"no existe `{report.name}` para esta tarea",
                        "todo brief despachado deja report, incluso en BLOCKED")
            continue
        text = read(report)
        secs = sections(text)
        status = (secs.get("Status", "") or "").strip().splitlines()
        first = status[0].strip() if status else ""
        if not any(s in first.upper() for s in TERMINAL_STATUSES):
            rep.blocker(report.name, f"`## Status` no declara un estado terminal (leído: {first!r})")
        brief_txt = strip_code_fences(read(brief))
        if "UI Contract" in sections(brief_txt):
            ve = secs.get("Visual Evidence", "")
            if not ve.strip():
                rep.blocker(report.name, "la tarea tiene UI Contract y el report no trae "
                                         "`## Visual Evidence`",
                            "capturas por breakpoint/estado, o UNVERIFIED con la razón")
            elif "UNVERIFIED" not in ve.upper():
                shots = [c for c in candidate_paths(ve)
                         if Path(c).suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
                if not shots:
                    rep.blocker(report.name, "`## Visual Evidence` no referencia ninguna captura "
                                             "ni se declara UNVERIFIED")
                else:
                    missing = [s for s in shots if not (bundle.parent.parent / s).exists()
                               and not (bundle / s).exists()
                               and not Path(s).exists()]
                    if missing:
                        rep.warn(report.name,
                                 f"capturas referenciadas que no se encuentran: {', '.join(missing[:4])}")

    for review in sorted(bundle.glob("*review*.md")):
        text = read(review)
        ids, statuses = review_rc_statuses(text)
        if not ids:
            continue
        for rc in sorted(ids):
            state = statuses.get(rc)
            if state in {"resolved", "superseded", "accepted"}:
                continue
            if state == "open":
                rep.blocker(review.name, f"`{rc}` sigue abierto",
                            "arréglalo, acéptalo con razón registrada, o decláralo abierto al usuario")
            else:
                rep.warn(review.name, f"`{rc}` no declara Status resolved/open/superseded")


def _bundle_files(bundle: Path) -> list[Path]:
    """Files under *bundle* in sorted order, skipping SKIP_DIRS.

    Replaces an unfiltered `bundle.rglob("*")`: a bundle never owns
    node_modules/.git, but a stray one used to drag the lint through
    thousands of vendored files on slow mounts.  Never follows symlinks,
    mirroring rglob's default.
    """
    found: list[Path] = []
    stack = [bundle]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as it:
                items = []
                for entry in it:
                    try:
                        is_dir = entry.is_dir(follow_symlinks=False)
                    except OSError:
                        continue
                    items.append((entry.name, entry.path, is_dir))
        except OSError:
            continue
        for entry_name, entry_path, is_dir in sorted(items):
            if is_dir:
                if entry_name in SKIP_DIRS:
                    continue
                stack.append(Path(entry_path))
            else:
                found.append(Path(entry_path))
    return sorted(found)


def check_naming_and_leftovers(bundle: Path, rep: Report) -> None:
    known = re.compile(
        r"^(context-map|plan|global-constraints|progress|final-review|brief|"
        r"integration-.+|task-\d{1,3}[a-z]?-(brief|report|review)|"
        r"debug-diagnosis|second-diagnosis-.+|advisor-.+)$", re.I)
    for p in _bundle_files(bundle):
        if not p.is_file():
            continue
        rel = p.relative_to(bundle).as_posix()
        if p.suffix.lower() != ".md":
            if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".txt", ".json", ".html"):
                continue
            rep.info(rel, "fichero no-Markdown en el bundle; ¿sonda temporal sin retirar?")
            continue
        if p.stem.lower().startswith(FORBIDDEN_ARTIFACT_PREFIXES):
            rep.blocker(rel, "nombre de artefacto prohibido",
                        "prefíjalo con su rol, p. ej. task-01-report.md")
        if "/" not in rel and not known.match(p.stem):
            rep.info(rel, "artefacto fuera de la convención de nombres del bundle")


# ---------------------------------------------------------------- driver

def run(bundle: Path, repo: Path, phase: str) -> Report:
    rep = Report()
    _SUFFIX_WALK_DEGRADED.clear()
    plan_text = strip_code_fences(read(bundle / "plan.md")) if (bundle / "plan.md").exists() else ""

    briefs = sorted(bundle.glob("task-*-brief.md")) + sorted(bundle.glob("brief.md"))
    pre_approval = phase in ("pre-approval", "all")
    pre_synthesis = phase in ("pre-synthesis", "all")

    if pre_approval:
        if not briefs:
            rep.warn("bundle", "no hay ningún task brief en el bundle")
        parsed = [check_brief(repo, bundle, b, rep) for b in briefs]
        rep.note(f"{len(briefs)} brief(s): secciones, rutas, comandos de test, nombres")
        if len(parsed) > 1:
            check_wave_disjointness(parsed, plan_text, rep)
            check_interface_reciprocity(parsed, rep)
            rep.note("disjunción de Touch entre tareas y reciprocidad de interfaces")
        if plan_text:
            if not re.search(r"(?i)\bwave|\bola", plan_text):
                rep.warn("plan.md", "no declara olas; el paralelismo no es auditable")
            if any(p["ui"] for p in parsed) and not re.search(
                    r"(?i)\b(extend|redesign|greenfield)\b", plan_text):
                rep.blocker("plan.md", "hay tareas de UI y plan.md no declara el modo "
                                       "Extend / Redesign / Greenfield")
        elif briefs:
            rep.warn("plan.md", "no existe; el bundle no tiene diseño registrado (¿lane Quick?)")

    if pre_synthesis:
        check_reports_and_reviews(bundle, rep)
        rep.note("reports por brief, estado terminal, evidencia visual y hallazgos RC")

    check_progress(bundle, rep, pre_synthesis)
    check_naming_and_leftovers(bundle, rep)
    if _SUFFIX_WALK_DEGRADED:
        rep.warn("bundle",
                 f"búsqueda por sufijo truncada en {len(_SUFFIX_WALK_DEGRADED)} "
                 "ruta(s): árbol grande o montaje lento; la ausencia no se pudo demostrar",
                 "usa rutas exactas en el brief en vez de sufijos")
    rep.note("ledger, convención de nombres y restos temporales")
    rep.number()
    return rep


def emit(rep: Report, bundle: Path, phase: str, as_json: bool) -> int:
    if as_json:
        print(json.dumps({
            "bundle": str(bundle),
            "phase": phase,
            "checked": rep.checked,
            "findings": [f.__dict__ for f in rep.findings],
            "blockers": len(rep.blockers),
        }, indent=2, ensure_ascii=False))
        return 1 if rep.blockers else 0

    icons = {"blocker": "BLOCKER", "warn": "WARN   ", "info": "INFO   "}
    print(f"bundle-lint  {bundle}  [{phase}]")
    for what in rep.checked:
        print(f"  checked: {what}")
    if not rep.findings:
        print("\n  sin hallazgos: el bundle es coherente con el repositorio.")
        return 0
    print()
    for f in rep.findings:
        print(f"  {icons[f.severity]} {f.ident}  {f.artifact}: {f.message}")
        if f.hint:
            print(f"                  -> {f.hint}")
    n = len(rep.blockers)
    print()
    print(f"  {n} blocker(s), "
          f"{sum(1 for f in rep.findings if f.severity == 'warn')} warning(s), "
          f"{sum(1 for f in rep.findings if f.severity == 'info')} info")
    return 1 if n else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="bundle_lint",
        description="Valida un plan bundle contra la realidad del repositorio. Solo lee.")
    ap.add_argument("bundle", help="ruta del bundle, p. ej. plans/mi-feature")
    ap.add_argument("--phase", choices=["pre-approval", "pre-synthesis", "all"], default="all")
    ap.add_argument("--repo", default=None,
                    help="raíz del repositorio (por defecto: el padre de plans/)")
    ap.add_argument("--json", action="store_true", help="salida JSON")
    a = ap.parse_args(argv)

    bundle = Path(a.bundle).resolve()
    if not bundle.is_dir():
        print(f"bundle-lint: {bundle} no es un directorio", file=sys.stderr)
        return 2
    if a.repo:
        repo = Path(a.repo).resolve()
    else:
        repo = bundle.parent.parent if bundle.parent.name == "plans" else Path.cwd()
    if not repo.is_dir():
        print(f"bundle-lint: raíz de repo inválida: {repo}", file=sys.stderr)
        return 2

    return emit(run(bundle, repo, a.phase), bundle, a.phase, a.json)


if __name__ == "__main__":
    sys.exit(main())
