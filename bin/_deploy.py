"""Despliegue: instalar, estado, adoptar y publicar."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from _core import HARNESS, RENDERED, ROOT, SOURCE, Harness

MANIFEST = ".agent-system-manifest.json"

# HOME efectivo. Se puede forzar con --home o AGENTSYS_HOME, lo que importa
# sobre todo bajo WSL: alli `~` es el home de Linux, pero Claude Code y Codex
# corren en Windows y leen sus carpetas del home de Windows.
_HOME_OVERRIDE: Path | None = None


def set_home(p: str | None) -> None:
    global _HOME_OVERRIDE
    if p:
        _HOME_OVERRIDE = Path(p).expanduser().resolve()


def home() -> Path:
    if _HOME_OVERRIDE:
        return _HOME_OVERRIDE
    env = os.environ.get("AGENTSYS_HOME")
    return Path(env).expanduser() if env else Path.home()


def backups() -> Path:
    return home() / ".agent-system-backups"


def under_wsl() -> bool:
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except Exception:  # noqa: BLE001
        return False


def windows_home_from_wsl() -> Path | None:
    """El home de Windows visto desde WSL, si se puede deducir."""
    users = Path("/mnt/c/Users")
    if not users.is_dir():
        return None
    cands = [d for d in users.iterdir()
             if d.is_dir() and (d / ".claude").is_dir() and not d.name.startswith(("Default", "All", "Public"))]
    return cands[0] if len(cands) == 1 else None


def live_dir(h: Harness) -> Path:
    return Path(h.install_dir.replace("~", str(home())))


def rendered_files(h: Harness) -> list[Path]:
    base = RENDERED / h.name
    return sorted(p.relative_to(base) for p in base.rglob("*") if p.is_file())


def read_manifest(live: Path) -> set[str]:
    f = live / MANIFEST
    if not f.exists():
        return set()
    try:
        return set(json.loads(f.read_text(encoding="utf-8")).get("files", []))
    except Exception:  # noqa: BLE001
        return set()


def git_tracked(live: Path) -> set[str]:
    """Ficheros trackeados por un checkout legacy de agent-system en la carpeta viva."""
    if not (live / ".git").exists():
        return set()
    try:
        out = subprocess.run(["git", "-C", str(live), "ls-files"], capture_output=True,
                             text=True, check=True).stdout
    except Exception:  # noqa: BLE001
        return set()
    return {line.strip().replace("/", "\\") if "\\" in str(live) else line.strip()
            for line in out.splitlines() if line.strip()}


def norm(rel: Path) -> str:
    return str(rel).replace("\\", "/")


def install_harness(h: Harness, force: bool, dry: bool, stamp: str) -> tuple[int, list[str]]:
    live = live_dir(h)
    base = RENDERED / h.name
    live.mkdir(parents=True, exist_ok=True)
    owned = read_manifest(live) | {norm(Path(p)) for p in git_tracked(live)}
    written, refused = 0, []
    installed: list[str] = []

    for rel in rendered_files(h):
        src, dst, key = base / rel, live / rel, norm(rel)
        installed.append(key)
        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                continue
            if key not in owned and not force:
                refused.append(key)
                continue
            if not dry:
                bak = backups() / stamp / h.name / rel
                bak.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dst, bak)
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        written += 1

    # ficheros que instalamos antes y ya no existen en rendered/: se retiran
    stale = sorted(read_manifest(live) - set(installed))
    for key in stale:
        p = live / key
        if p.exists() and not dry:
            bak = backups() / stamp / h.name / key
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(bak))
    if not dry:
        (live / MANIFEST).write_text(
            json.dumps({"generated": stamp, "source": str(ROOT), "files": installed}, indent=2)
            + "\n", encoding="utf-8", newline="\n")
    return written, refused


def clean_obsolete(h: Harness, stamp: str, dry: bool) -> list[str]:
    """Retira restos del sistema anterior, SOLO los de la lista exacta del
    adaptador. Nunca se borra: se mueve al backup."""
    live, out = live_dir(h), []
    for rel in h.obsolete:
        p = live / rel
        if not p.exists():
            continue
        out.append(rel)
        if not dry:
            dest = backups() / stamp / h.name / "_obsoleto" / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(p), str(dest))
    return out


def retire_legacy(h: Harness, stamp: str, dry: bool) -> str | None:
    live = live_dir(h)
    g = live / ".git"
    if not g.exists():
        return None
    target = live / f".git.legacy-agent-system-{stamp}"
    if not dry:
        g.rename(target)
    return str(target)


def harness_status(h: Harness) -> dict:
    live = live_dir(h)
    base = RENDERED / h.name
    if not live.exists():
        return {"live": str(live), "installed": False}
    drift = [norm(rel) for rel in rendered_files(h)
             if not (live / rel).exists()
             or (live / rel).read_bytes() != (base / rel).read_bytes()]
    return {"live": str(live), "installed": True, "drift": drift,
            "manifest": len(read_manifest(live)),
            "legacy_git": (live / ".git").exists()}


def source_of(h: Harness, rel: Path) -> Path | None:
    """Fichero del canon que produjo esa ruta, si es copia literal."""
    key = norm(rel)
    cand = h.files_dir / rel
    if cand.exists():
        return cand
    if key.startswith("skills/"):
        parts = key.split("/")
        shared = SOURCE / "skills" / parts[1]
        if shared.exists() and (shared / "/".join(parts[2:])).exists():
            return shared / "/".join(parts[2:])
    return None


def publish_paths() -> list[str]:
    return ["README.md", ".gitignore", ".gitattributes", "docs", "source", "harness",
            "rendered", "bin"]


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def now() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


# --------------------------------------------------- merge aditivo de plantillas
# Regla invariable: se anaden claves del sistema que falten; NUNCA se sobrescribe
# un valor que el usuario ya tiene. Las unicas excepciones son las migraciones
# forzadas declaradas explicitamente abajo.

import re as _re  # noqa: E402
import tomllib as _tomllib  # noqa: E402


def _fill_missing(target: dict, template: dict) -> int:
    changed = 0
    for k, v in template.items():
        if k not in target:
            target[k] = v
            changed += 1
        elif isinstance(v, dict) and isinstance(target[k], dict):
            changed += _fill_missing(target[k], v)
        elif isinstance(v, list) and isinstance(target[k], list):
            for item in v:
                if item not in target[k]:
                    target[k].append(item)
                    changed += 1
    return changed


def missing_paths(target: dict, template: dict, prefix: str = "") -> list[str]:
    """Claves de la plantilla ausentes en el destino, a cualquier profundidad."""
    out: list[str] = []
    for k, v in template.items():
        path = f"{prefix}{k}"
        if k not in target:
            out.append(path)
        elif isinstance(v, dict) and isinstance(target[k], dict):
            out += missing_paths(target[k], v, path + ".")
    return out


def merge_json(target: Path, template: Path, dry: bool) -> int:
    if not template.exists():
        return 0
    tpl = json.loads(template.read_text(encoding="utf-8"))
    cur = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    n = _fill_missing(cur, tpl)
    if n and not dry:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(cur, indent=2) + "\n", encoding="utf-8", newline="\n")
    return n


def _strip_jsonc(text: str) -> str:
    text = _re.sub(r"/\*.*?\*/", "", text, flags=_re.S)
    text = _re.sub(r"(?m)^\s*//.*$", "", text)
    return _re.sub(r"(?<![:\"\w])//[^\"\n]*$", "", text, flags=_re.M)


def merge_jsonc(target: Path, template: Path, dry: bool) -> int:
    """Insercion textual: conserva comentarios y formato del fichero del usuario."""
    if not template.exists():
        return 0
    if not target.exists():
        # Maquina nueva: se copia la plantilla tal cual, con sus comentarios.
        # Parsearla como JSON puro aqui fallaba, porque es JSONC.
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, target)
        return 1
    tpl = json.loads(_strip_jsonc(template.read_text(encoding="utf-8")))
    raw = target.read_text(encoding="utf-8")
    cur = json.loads(_strip_jsonc(raw))
    missing = {k: v for k, v in tpl.items() if k not in cur}
    changed = 0
    if missing:
        block = ",\n".join("  " + json.dumps(k) + ": " + json.dumps(v, indent=2).replace("\n", "\n  ")
                           for k, v in missing.items())
        i = raw.rstrip().rfind("}")
        head = raw[:i].rstrip()
        sep = "," if not head.rstrip().endswith("{") else ""
        raw = head + sep + "\n" + block + "\n}" + raw[i + 1:]
        changed += len(missing)
    # migracion forzada: el orquestador opcional necesita profundidad 2
    m = _re.search(r'"subagent_depth"\s*:\s*(\d+)', raw)
    if m and int(m.group(1)) < 2:
        raw = raw[:m.start(1)] + "2" + raw[m.end(1):]
        changed += 1
    if changed and not dry:
        target.write_text(raw, encoding="utf-8", newline="\n")
    return changed


def jsonc_unplaced(target: Path, template: Path) -> list[str]:
    """Claves anidadas que la insercion textual no puede colocar sin perder los
    comentarios del fichero del usuario. Se reportan para decidirlas a mano."""
    if not target.exists() or not template.exists():
        return []
    tpl = json.loads(_strip_jsonc(template.read_text(encoding="utf-8")))
    cur = json.loads(_strip_jsonc(target.read_text(encoding="utf-8")))
    return [q for q in missing_paths(cur, tpl) if "." in q]


def toml_unplaced(target: Path, template: Path) -> list[str]:
    if not target.exists() or not template.exists():
        return []
    tpl = _tomllib.loads(template.read_text(encoding="utf-8"))
    cur = _tomllib.loads(target.read_text(encoding="utf-8"))
    return [p for p in missing_paths(cur, tpl) if "." in p]


def merge_toml(target: Path, template: Path, dry: bool) -> int:
    """Insercion textual: claves de nivel superior primero, tablas ausentes al final."""
    if not template.exists():
        return 0
    if not target.exists():
        if not dry:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, target)
        return 1
    tpl_raw = template.read_text(encoding="utf-8")
    raw = target.read_text(encoding="utf-8")
    tpl, cur = _tomllib.loads(tpl_raw), _tomllib.loads(raw)
    head, tables = [], []
    for k, v in tpl.items():
        if isinstance(v, dict):
            continue
        if k not in cur:
            head.append(_re.search(rf"(?m)^{_re.escape(k)}\s*=.*$", tpl_raw).group(0))
    for name in _re.findall(r"(?m)^\[([^\]]+)\]", tpl_raw):
        top = name.split(".")[0]
        if top not in cur:
            body = _re.search(rf"(?ms)^\[{_re.escape(name)}\].*?(?=^\[|\Z)", tpl_raw).group(0)
            tables.append(body.rstrip())
    changed = len(head) + len(tables)
    if changed and not dry:
        out = ("\n".join(head) + "\n" if head else "") + raw
        if tables:
            out = out.rstrip() + "\n\n" + "\n\n".join(tables) + "\n"
        target.write_text(out, encoding="utf-8", newline="\n")
    return changed


TEMPLATE_MERGES = {
    "claude":   [("templates/settings.json", "settings.json", merge_json, None)],
    "codex":    [("templates/config.toml", "config.toml", merge_toml, toml_unplaced)],
    "opencode": [("templates/opencode.jsonc", "opencode.jsonc", merge_jsonc, jsonc_unplaced),
                 # config del flujo V2 (`opencode2`), que es el que se usa a diario
                 ("templates/opencode.v2.jsonc", "opencode.v2.jsonc", merge_jsonc, jsonc_unplaced)],
}


def merge_templates(h: Harness, dry: bool) -> list[str]:
    live, out = live_dir(h), []
    for tpl_rel, target_rel, fn, unplaced in TEMPLATE_MERGES.get(h.name, []):
        tpl, target = RENDERED / h.name / tpl_rel, live / target_rel
        if target.exists() and not dry:
            shutil.copy2(target, target.with_suffix(target.suffix + ".bak"))
        n = fn(target, tpl, dry)
        if n:
            out.append(f"{target_rel}: {n} claves del sistema anadidas")
        restantes = unplaced(target, tpl) if unplaced else []
        if restantes:
            out.append(f"{target_rel}: REVISA A MANO, claves anidadas del sistema que faltan "
                       f"y no se pueden insertar sin perder tus comentarios:")
            out += [f"  - {p}" for p in restantes]
    return out
