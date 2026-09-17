"""Validacion del envoltorio: que cada harness reciba claves y valores que
realmente entiende. Un valor fuera de rango no da error en el runtime: se
ignora en silencio, que es peor.
"""
from __future__ import annotations

import re
import tomllib
from pathlib import Path

CLAUDE_KEYS = {"name", "description", "model", "effort", "tools", "disallowedTools", "color",
               "permissionMode", "maxTurns", "skills", "mcpServers", "hooks", "memory",
               "background", "omitClaudeMd", "isolation", "initialPrompt", "experimental"}
CLAUDE_MODELS = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}
CLAUDE_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}
CODEX_SANDBOX = {"read-only", "workspace-write", "danger-full-access"}
OPENCODE_MODES = {"subagent", "all", "primary"}

TOP_LEVEL = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):[ \t]*(.*)$")


def frontmatter(text: str) -> dict[str, str]:
    """Pares clave: valor de primer nivel. Basta para lo que generamos."""
    if not text.startswith("---\n"):
        return {}
    body = text.split("\n---\n", 1)[0][4:]
    out = {}
    for line in body.splitlines():
        if line[:1] in (" ", "\t", "#", ""):
            continue
        m = TOP_LEVEL.match(line)
        if m:
            out[m.group(1)] = m.group(2).strip().strip('"')
    return out


def check_claude(p: Path) -> list[str]:
    fm, e = frontmatter(p.read_text(encoding="utf-8")), []
    if not fm:
        return [f"{p.name}: frontmatter ilegible"]
    unknown = set(fm) - CLAUDE_KEYS
    if unknown:
        e.append(f"{p.name}: claves que Claude Code ignoraria: {', '.join(sorted(unknown))}")
    if fm.get("name") != p.stem:
        e.append(f"{p.name}: name={fm.get('name')!r} no coincide con el nombre de fichero")
    if not re.fullmatch(r"[a-z][a-z-]*", fm.get("name", "")):
        e.append(f"{p.name}: name debe ser minusculas y guiones")
    m = fm.get("model", "")
    if m not in CLAUDE_MODELS and not m.startswith("claude-"):
        e.append(f"{p.name}: model={m!r} no es alias valido ni id claude-*")
    if fm.get("effort") not in EFFORTS:
        e.append(f"{p.name}: effort={fm.get('effort')!r} fuera de {sorted(EFFORTS)}")
    if fm.get("color") not in CLAUDE_COLORS:
        e.append(f"{p.name}: color={fm.get('color')!r} no es un color con nombre valido")
    if "Agent" not in fm.get("disallowedTools", "") and "Agent" not in fm.get("tools", ""):
        e.append(f"{p.name}: no deniega la tool Agent; el especialista podria delegar")
    if not fm.get("description"):
        e.append(f"{p.name}: description vacia")
    return e


def check_codex(p: Path) -> list[str]:
    try:
        d = tomllib.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return [f"{p.name}: TOML invalido: {exc}"]
    e = []
    for k in ("name", "description", "model", "model_reasoning_effort", "sandbox_mode",
              "developer_instructions"):
        if not d.get(k):
            e.append(f"{p.name}: falta {k}")
    if d.get("name") != p.stem:
        e.append(f"{p.name}: name={d.get('name')!r} no coincide con el nombre de fichero")
    if d.get("model_reasoning_effort") not in EFFORTS:
        e.append(f"{p.name}: model_reasoning_effort={d.get('model_reasoning_effort')!r} fuera de rango")
    if d.get("sandbox_mode") not in CODEX_SANDBOX:
        e.append(f"{p.name}: sandbox_mode={d.get('sandbox_mode')!r} fuera de {sorted(CODEX_SANDBOX)}")
    if p.stem == "advisor" and d.get("sandbox_mode") != "read-only":
        e.append(f"{p.name}: el advisor debe ser read-only")
    return e


def check_opencode(p: Path) -> list[str]:
    fm, e = frontmatter(p.read_text(encoding="utf-8")), []
    if not fm:
        return [f"{p.name}: frontmatter ilegible"]
    if fm.get("mode") not in OPENCODE_MODES:
        e.append(f"{p.name}: mode={fm.get('mode')!r} fuera de {sorted(OPENCODE_MODES)}")
    if not fm.get("model"):
        e.append(f"{p.name}: falta model")
    if not fm.get("description"):
        e.append(f"{p.name}: description vacia")
    return e


CHECKERS = {"claude": ("agents/*.md", check_claude),
            "codex": ("agents/*.toml", check_codex),
            "opencode": ("agents/*.md", check_opencode)}
