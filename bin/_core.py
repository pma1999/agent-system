"""Núcleo compartido: carga de configuración, render y comprobaciones.

Sin dependencias externas: sólo la biblioteca estándar (tomllib es stdlib
desde Python 3.11).
"""
from __future__ import annotations

import hashlib
import re
import shutil
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source"
HARNESS = ROOT / "harness"
RENDERED = ROOT / "rendered"

TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")
ANCHOR_RE = re.compile(r"^<!-- @section:([a-z0-9-]+) -->[ \t]*$", re.M)
SENTINEL = "⟦{}⟧"

# Nombres de artefacto prohibidos (Claude Code bloquea la escritura de
# subagentes a ficheros cuyo basename empiece por estas palabras).
FORBIDDEN_ARTIFACT_PREFIXES = ("report", "summary", "findings", "analysis")


class BuildError(Exception):
    pass


@dataclass
class Role:
    name: str
    harnesses: list[str]
    description: str


@dataclass
class Harness:
    name: str
    install_dir: str
    agent_format: str
    agent_path: str
    skill_path: str
    tokens: dict[str, str]
    agents: dict[str, dict]
    skill_frontmatter: str
    obsolete: list[str]
    files_dir: Path = field(init=False)

    def __post_init__(self) -> None:
        self.files_dir = HARNESS / self.name / "files"


def load_roles() -> list[Role]:
    data = tomllib.loads((SOURCE / "orchestration" / "roles.toml").read_text(encoding="utf-8"))
    return [Role(r["name"], r["harnesses"], r["description"]) for r in data["role"]]


def load_harnesses() -> dict[str, Harness]:
    out: dict[str, Harness] = {}
    for d in sorted(HARNESS.iterdir()):
        if not (d / "adapter.toml").exists():
            continue
        data = tomllib.loads((d / "adapter.toml").read_text(encoding="utf-8"))
        out[data["harness"]] = Harness(
            name=data["harness"],
            install_dir=data["install_dir"],
            agent_format=data["agent_format"],
            agent_path=data["agent_path"],
            skill_path=data["skill_path"],
            tokens=data.get("tokens", {}),
            agents=data.get("agents", {}),
            skill_frontmatter=data.get("skill", {}).get("frontmatter", ""),
            obsolete=data.get("obsolete", []),
        )
    return out


# --------------------------------------------------------------------- render


def resolve_sections(text: str, harness: str, sections_dir: Path) -> str:
    """Sustituye `<!-- @section:name -->` por sections/name.<harness>.md.

    Si el harness no declara esa sección, la ancla desaparece junto con una
    única línea en blanco que la siga.
    """

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        f = sections_dir / f"{name}.{harness}.md"
        if not f.exists():
            return "\x00DROP\x00"
        return f.read_text(encoding="utf-8").rstrip("\n")

    out = ANCHOR_RE.sub(repl, text)
    out = re.sub(r"\x00DROP\x00\n\n", "", out)
    out = re.sub(r"\x00DROP\x00\n?", "", out)
    return out


def substitute(text: str, tokens: dict[str, str], where: str) -> str:
    missing: set[str] = set()

    def repl(m: re.Match[str]) -> str:
        name = m.group(1)
        if name not in tokens:
            missing.add(name)
            return m.group(0)
        return tokens[name]

    out = TOKEN_RE.sub(repl, text)
    if missing:
        raise BuildError(f"{where}: token sin valor en el adaptador: {', '.join(sorted(missing))}")
    return out


def render_body(src: Path, h: Harness, extra: dict[str, str] | None = None,
                neutral: bool = False) -> str:
    sections_dir = src.parent / "sections"
    text = src.read_text(encoding="utf-8")
    if neutral:
        # Render neutro: las anclas se resuelven igual (para poder aislarlas
        # después) pero los tokens se marcan, no se sustituyen.
        toks = {k: SENTINEL.format(k) for k in set(TOKEN_RE.findall(text)) | set(h.tokens)}
        if extra:
            toks.update({k: SENTINEL.format(k) for k in extra})
    else:
        toks = dict(h.tokens)
        if extra:
            toks.update(extra)
    text = resolve_sections(text, h.name, sections_dir)
    return substitute(text, toks, f"{src.relative_to(ROOT)} [{h.name}]")


def wrap_agent(h: Harness, role: Role, body: str) -> str:
    cfg = h.agents.get(role.name)
    if cfg is None:
        raise BuildError(f"adapter {h.name}: falta [agents.{role.name}]")
    desc = substitute(role.description, h.tokens, f"roles.toml:{role.name} [{h.name}]")
    where = f"adapter {h.name} [agents.{role.name}]"
    for k in ("model", "effort"):
        if not cfg.get(k):
            raise BuildError(f"{where}: falta `{k}`")
    fm = substitute(cfg["frontmatter"],
                    {**h.tokens, "DESCRIPTION": desc,
                     "MODEL": cfg["model"], "EFFORT": cfg["effort"]}, where)
    if h.agent_format == "markdown_frontmatter":
        return f"---\n{fm}\n---\n\n{body.rstrip(chr(10))}\n"
    if h.agent_format == "toml_developer_instructions":
        check_toml_safe(body, f"{role.name} [{h.name}]")
        return f"{fm}\n\ndeveloper_instructions = '''{body.rstrip(chr(10))}\n'''\n"
    raise BuildError(f"formato de agente desconocido: {h.agent_format}")


def check_toml_safe(body: str, where: str) -> None:
    if "'''" in body:
        raise BuildError(f"{where}: el cuerpo contiene ''' y rompería developer_instructions")
    if body.rstrip("\n").endswith("\\"):
        raise BuildError(f"{where}: el cuerpo termina en barra invertida y rompería el TOML")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]


def copy_tree(src: Path, dst: Path) -> int:
    n = 0
    for f in sorted(src.rglob("*")):
        if f.is_dir():
            continue
        rel = f.relative_to(src)
        out = dst / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, out)
        n += 1
    return n
