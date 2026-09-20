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


def git_dirty(live: Path) -> set[str]:
    """Ficheros trackeados y MODIFICADOS en un checkout legacy.

    Estar en git es lo que hace que un fichero cuente como "nuestro" y se pueda
    sobrescribir. Pero si ademas esta modificado, es trabajo que ese PC nunca
    publico: deja de contar como nuestro y se reporta en vez de pisarse.
    """
    if not (live / ".git").exists():
        return set()
    try:
        out = subprocess.run(["git", "-C", str(live), "status", "--porcelain",
                              "--untracked-files=no"],
                             capture_output=True, text=True, check=True).stdout
    except Exception:  # noqa: BLE001
        return set()
    return {line[3:].strip().strip('"') for line in out.splitlines() if line.strip()}


def norm(rel: Path) -> str:
    return str(rel).replace("\\", "/")


def install_harness(h: Harness, force, dry: bool, stamp: str) -> tuple[int, list[str]]:
    live = live_dir(h)
    base = RENDERED / h.name
    live.mkdir(parents=True, exist_ok=True)
    sucios = {norm(Path(x)) for x in git_dirty(live)}
    owned = (read_manifest(live) | {norm(Path(x)) for x in git_tracked(live)}) - sucios
    written, refused = 0, []
    installed: list[str] = []

    for rel in rendered_files(h):
        src, dst, key = base / rel, live / rel, norm(rel)
        installed.append(key)
        if dst.exists():
            if dst.read_bytes() == src.read_bytes():
                continue
            # `force` es True (todo) o una lista de rutas concretas. Lo segundo
            # existe porque lo natural al revisar los rechazados es aprobar unos
            # si y otros no; un flag global obligaria a pisarlos todos.
            forzado = force is True or (isinstance(force, (list, set, tuple)) and key in force)
            if key not in owned and not forzado:
                motivo = ("cambio local sin publicar" if key in sucios
                          else "nunca estuvo gestionado")
                refused.append((key, motivo))
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
        # Un directorio que se queda vacio al retirar su contenido se retira
        # tambien: una carpeta `skills/<x>/` sin SKILL.md no es una skill, pero
        # si es una fuente de confusion. Solo se sube mientras quede vacio y sin
        # salir de la carpeta viva.
        if not dry:
            d = p.parent
            while d != live and d.is_dir() and not any(d.iterdir()):
                d.rmdir()
                d = d.parent
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


def _find_object_span(raw: str, key: str, start: int, end: int) -> tuple[int, int] | None:
    """Rango (pos tras `{`, pos del `}`) del objeto `key` dentro de raw[start:end]."""
    m = _re.search(r'"' + _re.escape(key) + r'"\s*:\s*\{', raw[start:end])
    if not m:
        return None
    open_at = start + m.end()
    depth, i, n = 1, open_at, len(raw)
    in_str = esc = False
    while i < n and depth:
        c = raw[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if not depth:
                return open_at, i
        i += 1
    return None


def _insert_nested(raw: str, path: list[str], value, indent: str = "  ") -> str | None:
    """Inserta textualmente `value` en raw bajo la ruta `path`, conservando
    comentarios y formato. Devuelve None si el padre no existe como objeto."""
    start, end = 0, len(raw)
    for parent in path[:-1]:
        span = _find_object_span(raw, parent, start, end)
        if span is None:
            return None
        start, end = span
    pad = indent * (len(path) + 1)
    body = json.dumps(value, indent=2).replace(chr(10), chr(10) + pad)
    entry = chr(10) + pad + json.dumps(path[-1]) + ": " + body + ","
    return raw[:start] + entry + raw[start:]


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
    # claves anidadas ausentes: insercion textual dentro del bloque padre, que
    # conserva los comentarios del usuario. Solo se anaden las que faltan; nunca
    # se toca un valor existente.
    for q in missing_paths(json.loads(_strip_jsonc(raw)), tpl):
        if "." not in q:
            continue
        parts = q.split(".")
        node = tpl
        for k in parts:
            node = node[k]
        out = _insert_nested(raw, parts, node)
        if out is not None:
            raw = out
            changed += 1

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
        # Una subtabla se inserta si falta su ruta COMPLETA, aunque su tabla
        # padre ya exista: `[mcp_servers.codegraph]` presente no debe impedir
        # anadir `[mcp_servers.playwright]`. TOML admite la subtabla al final.
        node, absent = cur, False
        for part in [x.strip().strip('"') for x in name.split(".")]:
            if not isinstance(node, dict) or part not in node:
                absent = True
                break
            node = node[part]
        if absent:
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
    "claude":   [("templates/settings.json", "settings.json", merge_json, None),
                 # Claude guarda los servidores MCP de usuario en ~/.claude.json,
                 # no en ~/.claude/settings.json. Es el unico sitio donde puede
                 # declararse Playwright/Chrome DevTools para todos los agentes.
                 ("templates/mcp-servers.json", "~/.claude.json", merge_json, None)],
    "codex":    [("templates/config.toml", "config.toml", merge_toml, toml_unplaced)],
    "opencode": [("templates/opencode.jsonc", "opencode.jsonc", merge_jsonc, jsonc_unplaced),
                 # config del flujo V2 (`opencode2`), que es el que se usa a diario
                 ("templates/opencode.v2.jsonc", "opencode.v2.jsonc", merge_jsonc, jsonc_unplaced)],
}


def migrate_browser_paths(target: Path, dry: bool) -> int:
    """Actualiza los argumentos de los MCP oficiales @latest sin reformatear.

    Migracion explicita: el usuario quiere guardar evidencias entre proyectos.
    Las versiones fijadas y los comandos personalizados conservan su politica.
    """
    if not target.exists():
        return 0
    raw = target.read_text(encoding="utf-8")
    flags = {
        "@playwright/mcp@latest": "--allow-unrestricted-file-access",
        "chrome-devtools-mcp@latest": "--allow-unrestricted-paths",
    }
    changed = 0

    def update(match):
        nonlocal changed
        body = match.group(2)
        try:
            args = json.loads(_strip_jsonc("[" + body + "]"))
        except (ValueError, TypeError):
            return match.group(0)
        if not isinstance(args, list):
            return match.group(0)
        for package, flag in flags.items():
            if package not in args or any(
                isinstance(arg, str) and
                (arg == flag or arg.startswith(flag + "="))
                for arg in args
            ):
                continue
            # Inserta justo despues del paquete, antes de posibles comentarios.
            package_match = _re.search(_re.escape(json.dumps(package)), body)
            if package_match is None:
                continue
            at = package_match.end()
            body = body[:at] + ", " + json.dumps(flag) + body[at:]
            changed += 1
        return match.group(1) + body + "]"

    result = _re.sub(
        r'((?:"(?:args|command)"\s*:|\bargs\s*=)\s*\[)'
        r'((?:[^"\]]|"(?:\\.|[^"\\])*")*)\]',
        update, raw,
    )
    if changed and not dry:
        # Valida antes de escribir y conserva una copia de esta migracion.
        if target.suffix == ".toml":
            _tomllib.loads(result)
        else:
            json.loads(_strip_jsonc(result))
        backup = backups() / now() / "browser-paths" / target.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
        target.write_text(result, encoding="utf-8", newline="\n")
    return changed


def merge_templates(h: Harness, dry: bool) -> list[str]:
    live, out = live_dir(h), []
    for tpl_rel, target_rel, fn, unplaced in TEMPLATE_MERGES.get(h.name, []):
        tpl = RENDERED / h.name / tpl_rel
        # Un destino que empieza por `~/` vive fuera de install_dir. Se usa para
        # ficheros que el harness escribe solo para si (los MCP de Claude viven
        # en ~/.claude.json, no en ~/.claude/settings.json) y sigue las mismas
        # reglas: fusion aditiva, copia .bak, nunca se pisa un valor existente.
        target = (home() / target_rel[2:]) if target_rel.startswith("~/") else live / target_rel
        if target.exists() and not dry:
            shutil.copy2(target, target.with_suffix(target.suffix + ".bak"))
        n = fn(target, tpl, dry)
        if n:
            out.append(f"{target_rel}: {n} claves del sistema anadidas")
        migrated = migrate_browser_paths(target, dry)
        if migrated:
            out.append(f"{target_rel}: {migrated} permisos de rutas MCP actualizados")
        restantes = unplaced(target, tpl) if unplaced else []
        if restantes:
            out.append(f"{target_rel}: REVISA A MANO, claves anidadas del sistema que faltan "
                       f"y no se pueden insertar sin perder tus comentarios:")
            out += [f"  - {p}" for p in restantes]
    return out
