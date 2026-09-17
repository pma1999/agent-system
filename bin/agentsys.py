#!/usr/bin/env python3
"""agentsys - herramienta unica del sistema multiagentico.

    build     renderiza source/ + harness/ -> rendered/
    verify    comprueba render determinista, identidad de prompts y deriva
    status    resumen legible del estado de este PC
    install   despliega rendered/ en las carpetas vivas
    adopt     trae un cambio hecho en una carpeta viva de vuelta al canon
    publish   commit + push del repo canonico con lista explicita de ficheros

Documentacion: README.md y docs/MANTENIMIENTO.md.
"""
from __future__ import annotations

import argparse
import difflib
import os
import re
import shutil
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _core  # noqa: E402
import _deploy  # noqa: E402
import _schema  # noqa: E402
from _core import (  # noqa: E402
    ANCHOR_RE, BuildError, Harness, RENDERED, ROOT, Role, SOURCE, copy_tree,
    load_harnesses, load_roles, render_body, wrap_agent,
)

SKILL_SRC = SOURCE / "orchestration" / "skill" / "SKILL.md"
NL = chr(10)


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def fail(msg: str) -> None:
    print(f"  FALLO {msg}")


def skill_out_path(h: Harness) -> Path:
    return RENDERED / h.name / h.skill_path.format(skill=h.tokens["ORCH_SKILL"])


def agent_out_path(h: Harness, role: str) -> Path:
    return RENDERED / h.name / h.agent_path.format(role=role)


def render_harness(h: Harness, roles: list[Role]) -> dict[Path, str]:
    """Devuelve {ruta relativa a rendered/<harness>: contenido}."""
    out: dict[Path, str] = {}
    for role in roles:
        if h.name not in role.harnesses:
            continue
        src = SOURCE / "orchestration" / "agents" / f"{role.name}.md"
        if not src.exists():
            raise BuildError(f"falta el cuerpo canonico {src.relative_to(ROOT)}")
        body = render_body(src, h)
        rel = agent_out_path(h, role.name).relative_to(RENDERED / h.name)
        out[rel] = wrap_agent(h, role, body)

    if SKILL_SRC.exists():
        body = render_body(SKILL_SRC, h)
        fm = h.skill_frontmatter
        rel = skill_out_path(h).relative_to(RENDERED / h.name)
        out[rel] = f"---{NL}{fm}{NL}---{NL}{NL}{body.rstrip(NL)}{NL}"
    return out


def write_tree(h: Harness, files: dict[Path, str]) -> None:
    base = RENDERED / h.name
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True)
    for rel, content in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8", newline=NL)
    shared = SOURCE / "skills"
    if shared.exists():
        for d in sorted(shared.iterdir()):
            if d.is_dir():
                copy_tree(d, base / "skills" / d.name)
    if h.files_dir.exists():
        copy_tree(h.files_dir, base)


def cmd_build(args: argparse.Namespace) -> int:
    roles, harnesses = load_roles(), load_harnesses()
    for h in harnesses.values():
        write_tree(h, render_harness(h, roles))
        n = sum(1 for p in (RENDERED / h.name).rglob("*") if p.is_file())
        print(f"  {h.name:<9} {n} ficheros -> rendered/{h.name}/")
    return 0


def drop_anchors(text: str) -> str:
    text = ANCHOR_RE.sub("\x00DROP\x00", text)
    text = re.sub(r"\x00DROP\x00\n\n", "", text)
    return re.sub(r"\x00DROP\x00\n?", "", text)


def canonical_of(src: Path) -> str:
    """Canonico normalizado: anclas fuera y tokens marcados con el centinela."""
    from _core import SENTINEL, TOKEN_RE
    text = drop_anchors(src.read_text(encoding="utf-8"))
    return TOKEN_RE.sub(lambda m: SENTINEL.format(m.group(1)), text)


def strip_sections(src: Path, text: str, h: Harness) -> str:
    """Quita del render neutro los bloques insertados desde sections/."""
    sections_dir = src.parent / "sections"
    for name in ANCHOR_RE.findall(src.read_text(encoding="utf-8")):
        f = sections_dir / f"{name}.{h.name}.md"
        if f.exists():
            block = f.read_text(encoding="utf-8").rstrip(NL)
            text = text.replace(block + NL + NL, "", 1).replace(block, "", 1)
    return text


def unwrap(h: Harness, text: str) -> str:
    """Quita el envoltorio del harness y devuelve el cuerpo del prompt."""
    if h.agent_format == "toml_developer_instructions" and "developer_instructions = '''" in text:
        body = text.split("developer_instructions = '''", 1)[1]
        return body.rsplit("'''", 1)[0]
    if text.startswith("---" + NL):
        return text.split(NL + "---" + NL, 1)[1].lstrip(NL)
    return text


def value_markers(h: Harness) -> dict[str, str]:
    """Un marcador por VALOR distinto, no por nombre de token.

    Dos tokens con el mismo valor en un harness son indistinguibles al hacer la
    vuelta (en Claude, ORCH_SKILL y WORKFLOW valen ambos "orchestrator"), asi que
    se normalizan al mismo marcador en los dos lados de la comparacion.
    """
    out, n = {}, {}
    for name in sorted(h.tokens):
        v = h.tokens[name]
        if not v:
            continue
        if v not in n:
            n[v] = f"⟦v{len(n)}⟧"
        out[name] = n[v]
    return out


def detokenize(h: Harness, text: str) -> str:
    """Sustitucion inversa: cada valor de token vuelve a su marcador.

    Si el valor de un token coincide ademas con prosa del cuerpo canonico, la
    inversa sobre-sustituye y la comparacion falla. Es intencionado: ese valor es
    ambiguo y hay que elegir otro.
    """
    marks = value_markers(h)
    for name in sorted(h.tokens, key=lambda k: -len(h.tokens[k])):
        v = h.tokens[name]
        if v:
            text = text.replace(v, marks[name])
    return text


def marked_canonical(h: Harness, raw: str) -> str:
    marks = value_markers(h)
    from _core import TOKEN_RE
    return TOKEN_RE.sub(lambda m: marks.get(m.group(1), m.group(0)), raw)


def identity_targets(roles: list[Role], harnesses: dict[str, Harness]):
    for r in roles:
        if len(r.harnesses) >= 2:
            src = SOURCE / "orchestration" / "agents" / f"{r.name}.md"
            hs = [harnesses[x] for x in r.harnesses if x in harnesses]
            yield r.name, src, hs
    if SKILL_SRC.exists():
        yield "SKILL", SKILL_SRC, list(harnesses.values())


def cmd_verify(args: argparse.Namespace) -> int:
    roles, harnesses = load_roles(), load_harnesses()
    errors = 0

    print("1. Render determinista")
    n = 0
    for h in harnesses.values():
        for rel, content in render_harness(h, roles).items():
            p = RENDERED / h.name / rel
            if not p.exists():
                fail(f"{h.name}/{rel} no esta renderizado")
                errors += 1
            elif p.read_text(encoding="utf-8") != content:
                fail(f"{h.name}/{rel} difiere del render (editado a mano?)")
                errors += 1
            else:
                n += 1
    if not errors:
        ok(f"rendered/ coincide con source/ + harness/ ({n} ficheros generados)")

    print("2. Identidad de prompts entre harnesses")
    for name, src, hs in identity_targets(roles, harnesses):
        if not src.exists():
            fail(f"{name}: falta el cuerpo canonico")
            errors += 1
            continue
        base = canonical_of(src)
        raw = drop_anchors(src.read_text(encoding="utf-8"))
        bad = []
        for h in hs:
            got = strip_sections(src, render_body(src, h, neutral=True), h)
            if got != base:
                bad.append((h.name, got, base))
                continue
            # vuelta completa desde lo realmente renderizado e instalable
            out = (RENDERED / h.name /
                   (agent_out_path(h, name).relative_to(RENDERED / h.name) if name != "SKILL"
                    else skill_out_path(h).relative_to(RENDERED / h.name)))
            if out.exists():
                back = detokenize(h, strip_sections(src, unwrap(h, out.read_text(encoding="utf-8")), h))
                if back.rstrip(NL) != marked_canonical(h, raw).rstrip(NL):
                    bad.append((h.name + " (vuelta desde rendered/)", back,
                                marked_canonical(h, raw)))
        if bad:
            errors += 1
            fail(f"{name}: el cuerpo no es identico en {', '.join(b[0] for b in bad)}")
            d = difflib.unified_diff(bad[0][2].splitlines(), bad[0][1].splitlines(),
                                     "canonico", bad[0][0], lineterm="", n=1)
            print(NL.join(list(d)[:24]))
        else:
            ok(f"{name}: identico en {', '.join(x.name for x in hs)}")

    print("3. Envoltorio: esquema y roster")
    before = errors
    for h in harnesses.values():
        pattern, checker = _schema.CHECKERS[h.name]
        esperados = {r.name for r in roles if h.name in r.harnesses}
        if h.name == "opencode":
            esperados |= {"orquestador"}          # agente padre, exclusivo de OpenCode
        vistos = set()
        for p in sorted((RENDERED / h.name).glob(pattern)):
            vistos.add(p.stem)
            for msg in checker(p):
                fail(f"{h.name}/{msg}")
                errors += 1
        if vistos != esperados:
            fail(f"{h.name}: roster descuadrado. sobran={sorted(vistos - esperados)} "
                 f"faltan={sorted(esperados - vistos)}")
            errors += 1
        skill = skill_out_path(h)
        if not skill.exists():
            fail(f"{h.name}: falta la skill orquestadora en {skill.name}")
            errors += 1
        else:
            fm = _schema.frontmatter(skill.read_text(encoding="utf-8"))
            if fm.get("name") != h.tokens["ORCH_SKILL"]:
                fail(f"{h.name}: la skill se llama {fm.get('name')!r}, "
                     f"se esperaba {h.tokens['ORCH_SKILL']!r}")
                errors += 1
        for p in sorted((RENDERED / h.name).rglob("*.md")):
            base = p.stem.lower()
            if any(base.startswith(x) for x in _core.FORBIDDEN_ARTIFACT_PREFIXES)                     and "skills" not in p.parts:
                fail(f"{h.name}/{p.name}: nombre de artefacto prohibido")
                errors += 1
    if errors == before:
        ok("esquema por harness, roster y nombres correctos")

    print("4. Deriva respecto a las carpetas vivas")
    for h in harnesses.values():
        live = _deploy.live_dir(h)
        if not live.exists():
            print(f"  --    {h.name}: {live} no existe (sin instalar)")
            continue
        base = RENDERED / h.name
        diffs = []
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(base)
            t = live / rel
            if not t.exists() or t.read_bytes() != p.read_bytes():
                diffs.append(rel)
        if diffs:
            print(f"  DERIVA {h.name}: {len(diffs)} ficheros difieren "
                  f"-- ejecuta `agentsys install`")
            for rel in diffs[:8]:
                print(f"         {rel}")
        else:
            ok(f"{h.name}: instalado y sin deriva")

    print()
    print("verify: FALLO" if errors else "verify: OK")
    return 1 if errors else 0


def cmd_status(args: argparse.Namespace) -> int:
    harnesses = load_harnesses()
    for h in harnesses.values():
        st = _deploy.harness_status(h)
        if not st["installed"]:
            print(f"  {h.name:<9} {st['live']} -- no instalado")
            continue
        drift = st["drift"]
        estado = "sin deriva" if not drift else f"{len(drift)} ficheros con deriva"
        legacy = "  [checkout legacy activo]" if st["legacy_git"] else ""
        print(f"  {h.name:<9} {st['live']}")
        print(f"            {st['manifest']} ficheros gestionados, {estado}{legacy}")
        for rel in drift[:10]:
            print(f"            ~ {rel}")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    roles, harnesses = load_roles(), load_harnesses()
    for h in harnesses.values():          # el render siempre precede a la instalacion
        write_tree(h, render_harness(h, roles))
    stamp = _deploy.now()
    refused_total = 0
    for h in harnesses.values():
        written, refused = _deploy.install_harness(h, args.force, args.dry_run, stamp)
        sufijo = " (simulacion)" if args.dry_run else ""
        print(f"  {h.name:<9} {written} ficheros desplegados en "
              f"{_deploy.live_dir(h)}{sufijo}")
        if refused:
            refused_total += len(refused)
            print(f"            {len(refused)} rechazados: existen, difieren y nunca "
                  f"estuvieron gestionados. Revisalos y repite con --force:")
            for r in refused:
                print(f"            ! {r}")
        for line in _deploy.merge_templates(h, args.dry_run):
            print(f"            {line}")
        if args.retire_legacy:
            moved = _deploy.retire_legacy(h, stamp, args.dry_run)
            if moved:
                print(f"            checkout legacy retirado -> {moved}")
    if not args.dry_run:
        print(f"  copias de seguridad en {_deploy.BACKUPS / stamp}")
    return 1 if refused_total else 0


def cmd_adopt(args: argparse.Namespace) -> int:
    """Trae de vuelta al canon un cambio hecho a mano en una carpeta viva."""
    harnesses = load_harnesses()
    pendientes = 0
    for h in harnesses.values():
        st = _deploy.harness_status(h)
        if not st.get("installed"):
            continue
        for key in st["drift"]:
            rel = Path(key)
            live_file = _deploy.live_dir(h) / rel
            if not live_file.exists():
                continue
            src = _deploy.source_of(h, rel)
            if src is None:
                print(f"  GENERADO {h.name}/{key}")
                print("           no se adopta: es salida del render. Edita el canon en "
                      "source/orchestration/ o harness/<h>/adapter.toml")
                pendientes += 1
                continue
            if args.dry_run:
                print(f"  adoptaria {h.name}/{key} -> {src.relative_to(ROOT)}")
            else:
                shutil.copy2(live_file, src)
                print(f"  adoptado  {h.name}/{key} -> {src.relative_to(ROOT)}")
    if pendientes:
        print()
        print("  Ejecuta `agentsys build` y vuelve a comprobar con `verify`.")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    if cmd_verify(argparse.Namespace()) != 0:
        print("publish cancelado: verify no pasa", file=sys.stderr)
        return 2
    _deploy.git("add", "--", *_deploy.publish_paths())
    st = _deploy.git("status", "--porcelain")
    if not st.stdout.strip():
        print("  nada que publicar")
        return 0
    print(st.stdout.rstrip())
    msg = args.message or "actualiza el sistema multiagentico"
    r = _deploy.git("commit", "-m", msg)
    print(r.stdout.strip() or r.stderr.strip())
    r = _deploy.git("push", "origin", "HEAD")
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


COMMANDS = {"build": cmd_build, "verify": cmd_verify, "status": cmd_status,
            "install": cmd_install, "adopt": cmd_adopt, "publish": cmd_publish}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="agentsys", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in COMMANDS:
        sp = sub.add_parser(name)
        if name in ("install", "adopt"):
            sp.add_argument("--dry-run", action="store_true",
                            help="muestra lo que haria sin tocar nada")
        if name == "install":
            sp.add_argument("--force", action="store_true",
                            help="sobrescribe tambien ficheros que nunca estuvieron gestionados")
            sp.add_argument("--retire-legacy", action="store_true",
                            help="renombra el .git del checkout antiguo de la carpeta viva")
        if name in ("install", "status", "verify", "adopt"):
            sp.add_argument("--home", help="HOME a usar como destino (util desde WSL)")
        if name == "publish":
            sp.add_argument("-m", "--message", help="mensaje del commit")
    args = ap.parse_args(argv)
    _deploy.set_home(getattr(args, "home", None))
    if _deploy.under_wsl() and not getattr(args, "home", None)             and not os.environ.get("AGENTSYS_HOME") and args.cmd in ("install", "status",
                                                                     "verify", "adopt"):
        win = _deploy.windows_home_from_wsl()
        print("AVISO: estas bajo WSL. `~` es el home de Linux, pero Claude Code y Codex")
        print("       corren en Windows y leen sus carpetas del home de Windows.")
        if win:
            print(f"       Si es lo que querias, repite con:  --home {win}")
        print("       Para OpenCode da igual: ~/.config/opencode es un enlace a Windows.")
        print()
    try:
        return COMMANDS[args.cmd](args)
    except BuildError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
