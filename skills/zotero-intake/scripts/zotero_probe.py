#!/usr/bin/env python3
"""Sonda de solo lectura contra un Zotero que corre en esta misma maquina.

Sirve para las dos cosas que hay que saber ANTES de dar de alta una fuente:
si el item ya esta en la biblioteca, y con que mayusculas existen ya las etiquetas
que ibas a proponer.

    python zotero_probe.py --check
    python zotero_probe.py --doi 10.1093/oxrep/grz002
    python zotero_probe.py --title "Universal basic income and climate goals"
    python zotero_probe.py --tags welfare

Nunca escribe en Zotero. La busqueda de duplicados usa el JSON-RPC de Better BibTeX
(el unico canal fiable con Zotero abierto). Las etiquetas se leen de una copia
temporal de zotero.sqlite, porque el fichero vivo esta bloqueado por Zotero.

Solo biblioteca estandar. Codigos de salida: 0 correcto, 1 Zotero no disponible.
"""

import argparse
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:23119"
RPC = BASE + "/better-bibtex/json-rpc"
TIMEOUT = 30


def http_get(url, timeout=8):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.status, resp.read()


def rpc(method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "method": method,
                       "params": params or [], "id": 1}).encode("utf-8")
    req = urllib.request.Request(
        RPC, data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(payload["error"])
    return payload.get("result")


def zotero_running():
    try:
        status, body = http_get(BASE + "/connector/ping")
        return status == 200 and b"Zotero is running" in body
    except Exception:
        return False


def bbt_ready():
    try:
        status, body = http_get(BASE + "/better-bibtex/cayw?probe=probe")
        return status == 200 and body.strip() == b"ready"
    except Exception:
        return False


def find_data_dir(explicit=None):
    if explicit:
        return explicit if os.path.isdir(explicit) else None
    candidates = []
    home = os.path.expanduser("~")
    candidates.append(os.path.join(home, "Zotero"))
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(os.path.join(appdata, "Zotero", "Zotero"))
    candidates.append(os.path.join(home, "Library", "Application Support", "Zotero"))
    candidates.append(os.path.join(home, ".zotero", "zotero"))
    for path in candidates:
        if os.path.isfile(os.path.join(path, "zotero.sqlite")):
            return path
    return None


def snapshot_db(data_dir):
    """Copia zotero.sqlite a un temporal. El fichero vivo esta bloqueado."""
    src = os.path.join(data_dir, "zotero.sqlite")
    fd, dst = tempfile.mkstemp(prefix="zotero-probe-", suffix=".sqlite")
    os.close(fd)
    shutil.copy2(src, dst)
    return dst


def normalize(text):
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def cmd_check(args):
    running = zotero_running()
    print("Zotero en marcha:      %s" % ("si" if running else "NO"))
    if not running:
        print("\nAbre Zotero y vuelve a intentarlo. Sin el, trabaja en modo Fichero:")
        print("genera el .ris, validalo y entrega los pasos de importacion.")
        return 1
    ready = bbt_ready()
    print("Better BibTeX listo:   %s" % ("si" if ready else "NO"))
    if ready:
        try:
            for lib in rpc("user.groups") or []:
                print("  biblioteca id=%s  %s" % (lib.get("id"), lib.get("name")))
        except Exception as exc:
            print("  (no se pudieron listar las bibliotecas: %s)" % exc)
    data_dir = find_data_dir(args.data_dir)
    print("Directorio de datos:   %s" % (data_dir or "no encontrado"))
    return 0


DOI_LOOKUP_SQL = """
SELECT i.itemID, i.key, i.libraryID, it.typeName, f.fieldName, idv.value
FROM itemData d
JOIN itemDataValues idv ON d.valueID = idv.valueID
JOIN fields f ON d.fieldID = f.fieldID
JOIN items i ON d.itemID = i.itemID
JOIN itemTypes it ON i.itemTypeID = it.itemTypeID
WHERE f.fieldName IN ('DOI', 'extra')
  AND lower(idv.value) LIKE ?
  AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
"""

TITLE_SQL = """
SELECT idv.value
FROM itemData d
JOIN itemDataValues idv ON d.valueID = idv.valueID
JOIN fields f ON d.fieldID = f.fieldID
WHERE d.itemID = ? AND f.fieldName = 'title'
"""


def lookup_doi(data_dir, doi):
    """Busca un DOI en el campo DOI y en Extra. El JSON-RPC de Better BibTeX no
    indexa el DOI, asi que aqui hace falta la base de datos."""
    snap = snapshot_db(data_dir)
    try:
        con = sqlite3.connect(snap)
        rows = con.execute(DOI_LOOKUP_SQL, ("%" + doi.lower() + "%",)).fetchall()
        hits = []
        for item_id, key, library_id, type_name, field, _value in rows:
            title_row = con.execute(TITLE_SQL, (item_id,)).fetchone()
            hits.append({
                "key": key,
                "libraryID": library_id,
                "type": type_name,
                "title": title_row[0] if title_row else "(sin titulo)",
                "found_in": field,
            })
        con.close()
        return hits
    finally:
        try:
            os.unlink(snap)
        except OSError:
            pass


def citekey_for(title):
    """Recupera la clave Better BibTeX de un item ya conocido, por titulo."""
    if not bbt_ready():
        return None
    try:
        for r in rpc("item.search", [title]) or []:
            if normalize(r.get("title")) == normalize(title):
                return r.get("citation-key")
    except Exception:
        pass
    return None


def cmd_search(args):
    if args.doi:
        data_dir = find_data_dir(args.data_dir)
        if not data_dir:
            print("No se encontro el directorio de datos de Zotero. "
                  "Pasalo con --data-dir.")
            return 1
        doi = args.doi.strip()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if doi.lower().startswith(prefix):
                doi = doi[len(prefix):]
        try:
            hits = lookup_doi(data_dir, doi)
        except (OSError, sqlite3.Error) as exc:
            print("No se pudo consultar la base: %s" % exc)
            return 1

        if not hits:
            print("Sin duplicados: el DOI %s no esta en la biblioteca." % doi)
            print("Comprueba tambien por titulo, por si entro sin DOI:")
            print('  python zotero_probe.py --title "<titulo exacto>"')
            return 0

        print("YA EXISTE (DOI) — %d coincidencia(s):" % len(hits))
        for hit in hits:
            key = citekey_for(hit["title"])
            print("  titulo: %s" % hit["title"])
            print("  tipo  : %s" % hit["type"])
            print("  donde : biblioteca %s, item %s%s"
                  % (hit["libraryID"], hit["key"],
                     "" if hit["found_in"] == "DOI" else " (DOI en el campo Extra)"))
            if key:
                print("  clave : %s" % key)
            print()
        print("No lo vuelvas a dar de alta: revisa el item existente y completalo "
              "si le faltan campos o el PDF.")
        return 0

    if not bbt_ready():
        print("Better BibTeX no responde; no se puede buscar por titulo.")
        return 1
    try:
        results = rpc("item.search", [args.title]) or []
    except Exception as exc:
        print("La busqueda fallo: %s" % exc)
        return 1

    wanted = normalize(args.title)
    hits = []
    for r in results:
        title = normalize(r.get("title"))
        if not title:
            continue
        if title == wanted or wanted in title or title in wanted:
            hits.append(r)

    if not hits:
        print("Sin duplicados por titulo equivalente.")
        if results:
            print("(%d resultado(s) proximos en la busqueda libre; revisa si alguno "
                  "es la misma obra en otra version)" % len(results))
            for r in results[:5]:
                print("  ~ %s  %s" % (r.get("citation-key"), (r.get("title") or "")[:70]))
        return 0

    print("YA EXISTE (titulo equivalente) — %d coincidencia(s):" % len(hits))
    for r in hits:
        authors = r.get("author") or []
        first = ""
        if authors:
            first = authors[0].get("family") or authors[0].get("literal") or ""
        print("  clave : %s" % r.get("citation-key"))
        print("  tipo  : %s" % r.get("type"))
        print("  titulo: %s" % (r.get("title") or ""))
        print("  autor : %s" % first)
        print("  id    : %s" % r.get("id"))
        print()
    print("No lo vuelvas a dar de alta: revisa el item existente y completalo si "
          "le faltan campos o el PDF.")
    return 0


def cmd_tags(args):
    data_dir = find_data_dir(args.data_dir)
    if not data_dir:
        print("No se encontro el directorio de datos de Zotero. "
              "Pasalo con --data-dir.")
        return 1
    try:
        snap = snapshot_db(data_dir)
    except OSError as exc:
        print("No se pudo copiar zotero.sqlite: %s" % exc)
        return 1
    try:
        con = sqlite3.connect(snap)
        rows = con.execute(
            "SELECT t.name, COUNT(*) AS n "
            "FROM tags t JOIN itemTags it ON t.tagID = it.tagID "
            "GROUP BY t.tagID ORDER BY n DESC").fetchall()
        con.close()
    except sqlite3.Error as exc:
        print("No se pudo leer la copia de la base: %s" % exc)
        return 1
    finally:
        try:
            os.unlink(snap)
        except OSError:
            pass

    needle = normalize(args.tags)
    groups = {}
    for name, count in rows:
        key = normalize(name)
        if needle and needle not in key:
            continue
        groups.setdefault(key, []).append((name, count))

    if not groups:
        print("Ninguna etiqueta contiene %r." % args.tags)
        print("Es una etiqueta nueva: elige tu la forma y se consistente con ella.")
        return 0

    print("Variantes existentes que contienen %r:\n" % args.tags)
    for key in sorted(groups, key=lambda k: -sum(c for _, c in groups[k])):
        variants = sorted(groups[key], key=lambda v: -v[1])
        best, best_n = variants[0]
        print("  USA: %-45s (%d usos)" % ('"%s"' % best, best_n))
        for name, count in variants[1:]:
            print("       tambien existe %-38s (%d)" % ('"%s"' % name, count))
        print()
    print("Reutiliza la forma mayoritaria tal cual. Una variante nueva de mayusculas "
          "fragmenta la busqueda por etiqueta.")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Sonda de solo lectura contra Zotero (duplicados y etiquetas).")
    ap.add_argument("--check", action="store_true",
                    help="comprobar que Zotero y Better BibTeX responden")
    ap.add_argument("--doi", help="buscar un duplicado por DOI exacto")
    ap.add_argument("--title", help="buscar un duplicado por titulo")
    ap.add_argument("--tags", help="ver con que mayusculas existe ya una etiqueta")
    ap.add_argument("--data-dir", help="directorio de datos de Zotero, si no se detecta")
    args = ap.parse_args()

    if args.check:
        return cmd_check(args)
    if args.doi or args.title:
        if not zotero_running():
            print("Zotero no esta abierto; no se puede comprobar duplicados.")
            return 1
        return cmd_search(args)
    if args.tags is not None:
        return cmd_tags(args)

    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
