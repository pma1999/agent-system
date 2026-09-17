"""Perfiles de modelos por harness.

Un perfil es un fichero pequeno en `harness/<h>/model-profiles/<nombre>.toml`
que fija, por rol, el modelo y el effort. Aplicarlo reescribe esas dos claves en
`harness/<h>/adapter.toml`; nunca toca los cuerpos de prompt ni el envoltorio.

OpenCode cambia de modelo con mucha mas frecuencia que los otros dos, asi que
tiene mas perfiles; el mecanismo es el mismo para los tres.

`oh-my-opencode-slim.json` es config de OTRO sistema de agentes (OMO, el flujo
por defecto de OpenCode) y es estado local de cada maquina. Por eso el alcance
por defecto es `ours` y hay que pedir `omo` o `both` explicitamente.
"""
from __future__ import annotations

import json
import re
import tomllib
from datetime import date
from pathlib import Path

from _core import HARNESS, Harness

OMO_FILE = Path.home() / ".config" / "opencode" / "oh-my-opencode-slim.json"


def profiles_dir(harness: str) -> Path:
    return HARNESS / harness / "model-profiles"


def list_profiles(harness: str) -> list[Path]:
    d = profiles_dir(harness)
    return sorted(d.glob("*.toml")) if d.is_dir() else []


def load_profile(harness: str, name: str) -> dict:
    p = profiles_dir(harness) / f"{name}.toml"
    if not p.exists():
        disponibles = ", ".join(x.stem for x in list_profiles(harness)) or "ninguno"
        raise SystemExit(f"error: no existe el perfil '{name}' para {harness}.\n"
                         f"       disponibles: {disponibles}")
    return tomllib.loads(p.read_text(encoding="utf-8"))


def current(h: Harness) -> dict[str, tuple[str, str]]:
    return {r: (c["model"], c["effort"]) for r, c in h.agents.items()}


def write_adapter(harness: str, changes: dict[str, tuple[str, str]]) -> list[str]:
    """Reescribe `model`/`effort` de cada rol en el adaptador. Devuelve el log."""
    p = HARNESS / harness / "adapter.toml"
    raw = p.read_text(encoding="utf-8")
    known = set(tomllib.loads(raw).get("agents", {}))
    log: list[str] = []
    for role, (model, effort) in changes.items():
        if role not in known:
            log.append(f"  -- {role}: no existe en {harness}, se ignora")
            continue
        block = re.search(rf'(?ms)^\[agents\.{re.escape(role)}\]\n(.*?)(?=^\[|\Z)', raw)
        head = block.group(0)
        new = re.sub(r'(?m)^model = ".*"$', f'model = "{model}"', head)
        new = re.sub(r'(?m)^effort = ".*"$', f'effort = "{effort}"', new)
        if new != head:
            raw = raw.replace(head, new, 1)
            log.append(f"  -> {role}: {model} ({effort})")
        else:
            log.append(f"  =  {role}: ya estaba en {model} ({effort})")
    p.write_text(raw, encoding="utf-8", newline="")
    return log


def save_profile(harness: str, name: str, h: Harness, description: str | None) -> Path:
    d = profiles_dir(harness)
    d.mkdir(parents=True, exist_ok=True)
    desc = description or f"Guardado el {date.today().isoformat()}"
    lines = [f"# Perfil de modelos para {harness}.", f'description = "{desc}"', ""]
    for role, (model, effort) in current(h).items():
        lines += [f"[roles.{role}]", f'model = "{model}"', f'effort = "{effort}"', ""]
    p = d / f"{name}.toml"
    p.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="")
    return p


# --------------------------------------------------------------------- OMO

def omo_apply(model: str, effort: str, preset: str | None) -> list[str]:
    """Fija modelo/variante en un preset de oh-my-opencode-slim.json.

    Es config local de esta maquina y de otro sistema de agentes: no viaja en el
    repo y no la toca nadie salvo que se pida `--scope omo` o `both`.
    """
    if not OMO_FILE.exists():
        return [f"  -- {OMO_FILE.name} no existe en esta maquina; OMO sin tocar"]
    d = json.loads(OMO_FILE.read_text(encoding="utf-8"))
    target = preset or d.get("preset")
    if not target:
        return ["  -- oh-my-opencode-slim.json no declara preset activo; OMO sin tocar"]
    if target not in d.get("presets", {}):
        disp = ", ".join(d.get("presets", {})) or "ninguno"
        return [f"  -- el preset '{target}' no existe (hay: {disp}); OMO sin tocar"]
    agentes = d["presets"][target]
    tocados = []
    for nombre, cfg in agentes.items():
        if isinstance(cfg, dict) and "model" in cfg:
            cfg["model"] = model
            if effort:
                cfg["variant"] = effort
            tocados.append(nombre)
    OMO_FILE.write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8", newline="\n")
    return [f"  -> OMO preset '{target}': {len(tocados)} agentes a {model} ({effort})",
            f"     ({', '.join(tocados)})",
            "     nota: es config local de esta maquina, no viaja en el repo"]
