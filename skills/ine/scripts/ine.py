#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ine.py — Cliente CLI de la API pública del INE (WSTempus / INEbase).

Base URL: https://servicios.ine.es/wstempus/{js|csv|csv_sc|px|xlsx}/{ES|EN}/{FUNCION}/{input}[?params]

Sin autenticación. Licencia CC BY 4.0 (citar fuente: INE www.ine.es).

Uso general:  python ine.py <subcomando> [args] [--flags]
Ayuda:        python ine.py --help | python ine.py <subcomando> --help

Subcomandos:
  ops                 Lista las operaciones estadísticas (catálogo Tempus3)
  search <kw>         Busca operaciones por palabra clave en el nombre
  op <id>             Detalle de una operación (Id, Codigo o IOE<n>)
  tables <op>         Tablas de una operación
  table-data <id>     Datos de una tabla (Tempus3, pc-axis o tpx)
  series <cod>        Metadatos de una serie (información, unidad, periodicidad...)
  series-data <cod>   Datos de una serie (requiere --nult o --date)
  series-table <id>   Series que componen una tabla
  series-op <op>      Series de una operación (paginado, 500/pág)
  values-serie <cod>  Variables y valores que definen una serie
  variables <op>      Variables usadas en una operación
  values <var>        Valores de una variable (--op para acotar a operación)
  groups <tabla>      Grupos/combos de selección de una tabla
  group-values <t> <g> Valores de un grupo de tabla (para filtrar con --tv)
  meta-op <op>        Datos filtrados por metadatos de una operación (--g)
  series-meta-op <op> Series filtradas por metadatos de una operación (--g)
  periodicities       Periodicidades disponibles
  publications [op]   Publicaciones (de una operación si se indica)
  pub-dates <pub>     Fechas de publicación de una publicación
  children <var> <v>  Valores hijo de un valor (jerarquías, p.ej. CCAA->provincias)

Flags comunes:
  --lang EN           Idioma de la respuesta (ES por defecto)
  --det 0|1|2         Nivel de detalle de la respuesta
  --tip A|M|AM        A=amigable (nombres/fechas ISO), M=metadatos, AM=ambos
  --page N            Página (500 elementos por página)
  --url               Imprime la URL construida y sale (sin llamar)
  --json              Vuelca la respuesta JSON cruda a stdout
  --out PATH          Guarda la salida en un archivo

Datos de tabla:
  --nult N            Últimos N periodos (no observaciones)
  --date INI[:FIN]    Rango de fechas (AAAA-MM-DD o AAAAMMDD; FIN opcional)
  --tv "var:val"      Filtro por variable:valor (repetible; "var:" = todos)
  --format FORMATO    js|csv|csv_sc|px|xlsx (exportación completa; ver notas)
  --rows N            Limita las filas mostradas en pantalla (no afecta a --out)
  --tidy              Imprime una fila por observación (CSV a stdout)

Notas verificadas (jul-ago 2026):
  * DATOS_SERIE exige --nult o --date (si no: 404).
  * csv/csv_sc/px/xlsx exportan la TABLA COMPLETA (ignoran nult/date; tv da 400).
  * El CSV real viene en UTF-8 (BOM) aunque la cabecera diga ISO-8859-15.
  * csv/px/xlsx solo existen para tablas Tempus3 y tpx (prefijo /tpx/ automático);
    las tablas pc-axis solo tienen JSON.
  * SERIES_OPERACION puede pesar varios MB: usa --page y --search.
"""
import argparse
import json
import os
import sys
import urllib.parse

import requests

BASE = "https://servicios.ine.es/wstempus"
UA = {"User-Agent": "Mozilla/5.0 (compatible; ine-skill/1.0; +https://www.ine.es)"}
TIMEOUT = int(os.environ.get("INE_TIMEOUT", "120"))


def out(text=""):
    """Print con codificación UTF-8 segura (Windows console)."""
    print(text)


def raw_json(data):
    return json.dumps(data, ensure_ascii=False, indent=1)


def fmt_fecha(f):
    """Normaliza fechas: epoch ms (int) → AAAA-MM-DD; ISO/string → primeros 10 chars."""
    if f is None:
        return ""
    if isinstance(f, (int, float)):
        import datetime
        return datetime.datetime.fromtimestamp(f / 1000).strftime("%Y-%m-%d")
    s = str(f)
    return s[:10] if len(s) >= 10 else s


def periodo_label(d):
    """Mejor etiqueta de periodo para una observación (prefiere códigos tipo M06)."""
    p = d.get("Periodo") or {}
    return (d.get("T3_Periodo") or p.get("Codigo") or d.get("CodigoPeriodo")
            or p.get("Nombre") or d.get("NombrePeriodo") or "")


def get(path, params=None, fmt="js", lang="ES"):
    url = f"{BASE}/{fmt}/{lang}/{path}"
    r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
    return url, r


def norm_date(s, end=False):
    """Acepta AAAA, AAAA-MM, AAAA-MM-DD, AAAAMMDD → aaaammdd."""
    s = s.strip()
    if not s:
        return s
    digits = s.replace("-", "").replace("/", "").replace(".", "")
    if len(digits) == 4:
        return digits + ("1231" if end else "0101")
    if len(digits) == 6:
        return digits + ("30" if end else "01")
    if len(digits) == 8:
        return digits
    raise ValueError(f"Fecha no válida: {s!r} (usa AAAA, AAAA-MM, AAAA-MM-DD o AAAAMMDD)")


def norm_date_param(value):
    """'2025', '2025-01-01:2025-12-31', '2025-01-01:' → aaaammdd:aaaammdd"""
    if ":" in value:
        ini, fin = value.split(":", 1)
        return norm_date(ini) + ":" + (norm_date(fin, end=True) if fin else "")
    return norm_date(value) + ":"


# ---------------------------------------------------------------- operaciones
def cmd_ops(args):
    p = {"page": getattr(args, "page", 1)}
    if getattr(args, "geo", None) is not None:
        p["geo"] = args.geo
    if getattr(args, "det", None) is not None:
        p["det"] = args.det
    url, r = get("OPERACIONES_DISPONIBLES", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    ops = r.json()
    kw = getattr(args, "search", None) or getattr(args, "kw", None)
    if kw:
        kw = kw.lower()
        ops = [o for o in ops if kw in (o.get("Nombre") or "").lower()
               or kw in (o.get("Codigo") or "").lower()
               or kw in (o.get("Cod_IOE") or "").lower()]
    if args.json:
        return out(raw_json(ops))
    if not ops:
        return out("(sin resultados)")
    out(f"{len(ops)} operacion(es):")
    for o in ops:
        out(f"  {o.get('Id'):>4} | {o.get('Codigo') or '—':<10} | IOE{o.get('Cod_IOE') or '—':<6} | {(o.get('Nombre') or '').strip()}")


def cmd_op(args):
    url, r = get(f"OPERACION/{urllib.parse.quote(str(args.id))}", {"det": args.det} if args.det is not None else None, lang=args.lang)
    if args.url:
        return out(url)
    if r.status_code == 404:
        return out(f"Operación no encontrada: {args.id} (prueba `python ine.py search <palabra>`)")
    r.raise_for_status()
    o = r.json()
    if args.json:
        return out(raw_json(o))
    out(f"Id: {o['Id']} | Código: {o.get('Codigo')} | IOE: {o.get('Cod_IOE')}")
    out(f"Nombre: {o['Nombre']}")
    out(f"URL INEbase: https://www.ine.es{o.get('Url','')}" if o.get("Url") else "")


# ------------------------------------------------------------------ tablas
def cmd_tables(args):
    p = {}
    for k in ("det", "tip", "geo"):
        v = getattr(args, k)
        if v is not None:
            p[k] = v
    if "tip" not in p:
        p["tip"] = "A"  # modo amigable: nombres T3_* y fechas ISO en vez de IDs/epoch
    url, r = get(f"TABLAS_OPERACION/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    tabs = r.json()
    if args.search:
        kw = args.search.lower()
        tabs = [t for t in tabs if kw in (t.get("Nombre") or "").lower()]
    if args.json:
        return out(raw_json(tabs))
    if not tabs:
        return out("(sin tablas)")
    out(f"{len(tabs)} tabla(s):")
    for t in tabs:
        fin = t.get("FechaRef_fin")
        if fin == "null" or fin is None:
            fin = "—"
        per = t.get("T3_Periodicidad") or (t.get("Periodicidad") or [{}])[0].get("Nombre") if isinstance(t.get("Periodicidad"), list) else (t.get("T3_Periodicidad") or "")
        out(f"  Id {t['Id']:>6} | {(t.get('Nombre') or '').strip()[:66]} | per: {per} | ini: {t.get('Anyo_Periodo_ini')} | act: {fmt_fecha(t.get('Ultima_Modificacion'))}")


def _tv_list(args):
    tvs = []
    for tv in args.tv or []:
        if ":" not in tv:
            raise SystemExit(f"--tv debe tener formato 'id_variable:id_valor' (recibido: {tv!r})")
        tvs.append(tv)
    return tvs


def _print_series_data(data, rows=None, tidy=False):
    """data: lista de {COD,Nombre,Data:[...]} (Tempus3) o {Nombre,Data} (pc-axis/tpx).
    --rows limita el número total de observaciones mostradas (contador global)."""
    n = 0
    if tidy:
        hdr = ["COD", "Nombre", "Periodo", "Anyo", "TipoDato", "Valor"]
        out(",".join(hdr))
        for s in data:
            cod = s.get("COD", "")
            nombre = (s.get("Nombre") or "").strip()
            for d in s.get("Data", []):
                if rows is not None and n >= rows:
                    return
                out(f"{cod},{nombre},{periodo_label(d)},{d.get('Anyo', '')},{d.get('T3_TipoDato', '')},{d.get('Valor', '')}")
                n += 1
        return
    total = sum(len(s.get("Data", [])) for s in data)
    for s in data:
        nombre = (s.get("Nombre") or "").strip()
        out(f"• {s.get('COD', '')} {nombre}".rstrip())
        for d in s.get("Data", []):
            if rows is not None and n >= rows:
                out(f"    … ({total - n} observaciones más; usa --rows o --out para verlas todas)")
                return
            per = periodo_label(d)
            anyo = d.get("Anyo", "")
            tdt = d.get("T3_TipoDato", "")
            val = d.get("Valor", "")
            fecha = fmt_fecha(d.get("Fecha"))
            if fecha:
                out(f"    {per:<6} {anyo:<5} {tdt:<14} {val}   ({fecha})")
            else:
                out(f"    {per:<6} {anyo:<5} {tdt:<14} {val}")
            n += 1


def cmd_table_data(args):
    tvs = _tv_list(args)
    p = {}
    if args.nult is not None:
        p["nult"] = args.nult
    if args.date:
        p["date"] = norm_date_param(args.date)
    if args.tip and args.tip != "raw":
        p["tip"] = args.tip
    elif args.tip is None:
        p["tip"] = "A"  # modo amigable por defecto (nombres T3_*, fechas ISO)
    if args.det is not None:
        p["det"] = args.det
    for tv in tvs:
        p.setdefault("tv", []).append(tv)

    fmt = args.format or "js"
    if fmt != "js":
        # Exportación completa: probar ruta normal y, si falla, con prefijo /tpx/
        path = f"DATOS_TABLA/{args.id}"
        url, r = get(path, p if fmt == "js" else None, fmt=fmt, lang=args.lang)
        if r.status_code in (204, 404) and not str(args.id).startswith("t"):
            url2, r2 = get(f"DATOS_TABLA/tpx/{args.id}", None, fmt=fmt, lang=args.lang)
            if r2.status_code == 200:
                url, r = url2, r2
        if args.url:
            return out(url)
        if r.status_code in (204, 404):
            return out(f"El formato {fmt} no está disponible para esta tabla (pc-axis solo tiene JSON; tpx necesita --format con prefijo).")
        r.raise_for_status()
        ext = {"csv": "csv", "csv_sc": "csv", "px": "px", "xlsx": "xlsx"}[fmt]
        fn = args.out or f"ine_export_{args.id}.{ext}"
        with open(fn, "wb") as f:
            f.write(r.content)
        # El CSV real es UTF-8 (BOM) pese a cabecera ISO-8859-15
        enc = "utf-8-sig" if fmt in ("csv", "csv_sc") else None
        info = ""
        if enc:
            txt = r.content.decode(enc, errors="replace")
            info = f" | {len(txt.splitlines())} líneas | cabecera: {txt.splitlines()[0][:80] if txt.splitlines() else ''}"
        out(f"Exportada tabla completa a {fn} ({len(r.content):,} bytes){info}")
        out("Nota: csv/xlsx/px exportan TODA la tabla (ignoran --nult/--date; --tv no aplica).")
        return

    url, r = get(f"DATOS_TABLA/{args.id}", p, lang=args.lang)
    if args.url:
        return out(url)
    if r.status_code == 404:
        return out(f"Tabla no encontrada: {args.id}. ¿Es Tempus3 (t=...), pc-axis (path+file) o tpx (tpx=...)? "
                   "Prueba `python ine.py tables <operación>` para listar tablas.")
    r.raise_for_status()
    data = r.json()
    if args.json:
        return out(raw_json(data))
    if args.out:
        fn = args.out
        if fn.endswith(".csv"):
            import io, csv as _csv
            buf = io.StringIO()
            w = _csv.writer(buf)
            w.writerow(["COD", "Nombre", "Periodo", "Anyo", "TipoDato", "Valor"])
            for s in data:
                for d in s.get("Data", []):
                    w.writerow([s.get("COD", ""), (s.get("Nombre") or "").strip(),
                                d.get("T3_Periodo") or d.get("NombrePeriodo", ""),
                                d.get("Anyo", ""), d.get("T3_TipoDato", ""), d.get("Valor", "")])
            with open(fn, "w", encoding="utf-8-sig", newline="") as f:
                f.write(buf.getvalue())
            out(f"Guardadas {sum(len(s.get('Data', [])) for s in data)} observaciones en {fn}")
            return
        with open(fn, "w", encoding="utf-8") as f:
            f.write(raw_json(data))
        out(f"Guardada respuesta JSON en {fn}")
        return
    if not data:
        return out("(sin datos)")
    out(f"{len(data)} serie(s):")
    _print_series_data(data, rows=args.rows, tidy=args.tidy)


# ------------------------------------------------------------------- series
def cmd_series(args):
    p = {"det": args.det if args.det is not None else 2}  # det=2: objetos anidados (operación, unidad...)
    if args.tip:
        p["tip"] = args.tip
    elif args.tip is None:
        p["tip"] = "A"
    url, r = get(f"SERIE/{urllib.parse.quote(str(args.cod))}", p, lang=args.lang)
    if args.url:
        return out(url)
    if r.status_code == 404:
        return out(f"Serie no encontrada: {args.cod}")
    r.raise_for_status()
    s = r.json()
    if args.json:
        return out(raw_json(s))
    out(f"Código: {s.get('COD')} | {s.get('Nombre','').strip()}")
    op = s.get("Operacion") or {}
    per = s.get("Periodicidad") or {}
    uni = s.get("Unidad") or {}
    cla = s.get("Clasificacion") or {}
    pub = s.get("Publicacion") or {}
    out(f"  Operación: {op.get('Nombre')} ({op.get('Codigo')})")
    out(f"  Periodicidad: {per.get('Nombre')} | Unidad: {uni.get('Nombre')} | Decimales: {s.get('Decimales')}")
    out(f"  Clasificación: {cla.get('Nombre')} | Publicación: {pub.get('Nombre')}")
    pfa = pub.get("PubFechaAct") or {}
    if pfa:
        out(f"  Última actualización: {pfa.get('Nombre')} ({fmt_fecha(pfa.get('Fecha'))})")


def cmd_series_data(args):
    if args.nult is None and not args.date:
        raise SystemExit("DATOS_SERIE exige --nult N o --date INI[:FIN] (si no, el INE responde 404)")
    p = {}
    if args.nult is not None:
        p["nult"] = args.nult
    if args.date:
        p["date"] = norm_date_param(args.date)
    if args.tip and args.tip != "raw":
        p["tip"] = args.tip
    elif args.tip is None:
        p["tip"] = "A"
    if args.det is not None:
        p["det"] = args.det
    url, r = get(f"DATOS_SERIE/{urllib.parse.quote(str(args.cod))}", p, lang=args.lang)
    if args.url:
        return out(url)
    if r.status_code == 404:
        return out(f"Serie no encontrada: {args.cod} (¿es Tempus3? Solo las series Tempus3 tienen datos por serie)")
    r.raise_for_status()
    s = r.json()  # ¡dict, no lista!
    if args.json:
        return out(raw_json(s))
    if args.out:
        if args.tidy:
            import io, csv as _csv
            buf = io.StringIO()
            w = _csv.writer(buf)
            w.writerow(["COD", "Nombre", "Periodo", "Anyo", "TipoDato", "Valor"])
            for d in s.get("Data", []):
                w.writerow([s.get("COD", ""), (s.get("Nombre") or "").strip(),
                            periodo_label(d), d.get("Anyo", ""), d.get("T3_TipoDato", ""), d.get("Valor", "")])
            with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
                f.write(buf.getvalue())
            out(f"Guardadas {len(s.get('Data', []))} observaciones en {args.out}")
        else:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(raw_json(s))
            out(f"Guardada respuesta en {args.out}")
        return
    _print_series_data([s], rows=args.rows, tidy=args.tidy)


def cmd_series_table(args):
    p = {}
    if args.tip:
        p["tip"] = args.tip
    if args.det is not None:
        p["det"] = args.det
    for tv in _tv_list(args):
        p.setdefault("tv", []).append(tv)
    url, r = get(f"SERIES_TABLA/{args.id}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    series = r.json()
    if args.search:
        kw = args.search.lower()
        series = [s for s in series if kw in (s.get("Nombre") or "").lower() or kw in (s.get("COD") or "").lower()]
    if args.json:
        return out(raw_json(series))
    out(f"{len(series)} serie(s):")
    for s in series[: args.max or len(series)]:
        out(f"  {s.get('COD',''):<12} {(s.get('Nombre') or '').strip()[:70]}")
    if args.max and len(series) > args.max:
        out(f"  … y {len(series) - args.max} más (usa --max para ampliar)")


def cmd_series_op(args):
    p = {"page": args.page}
    if args.det is not None:
        p["det"] = args.det
    if args.tip:
        p["tip"] = args.tip
    url, r = get(f"SERIES_OPERACION/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    series = r.json()
    scanned = 1
    # SERIES_OPERACION pagina (500/pág). Si se busca, escanea hasta 3 páginas y
    # fusiona coincidencias: los códigos con Id alto (series de la base vigente)
    # suelen estar en páginas posteriores a las series históricas.
    if getattr(args, "search", None) and args.page == 1 and not args.json:
        kw = args.search.lower()
        def matches(page):
            return [s for s in page if kw in (s.get("Nombre") or "").lower() or kw in (s.get("COD") or "").lower()]
        series = matches(series)
        while scanned < 3:
            nxt = requests.get(f"{BASE}/js/{args.lang}/SERIES_OPERACION/{urllib.parse.quote(str(args.op))}",
                               params={"page": scanned + 1}, headers=UA, timeout=TIMEOUT)
            if nxt.status_code != 200:
                break
            page = nxt.json()
            scanned += 1
            if not page:
                break
            series += matches(page)
    elif args.search:
        kw = args.search.lower()
        series = [s for s in series if kw in (s.get("Nombre") or "").lower() or kw in (s.get("COD") or "").lower()]
    if args.json:
        return out(raw_json(series))
    if scanned > 1:
        out(f"(búsqueda ampliada: escaneadas {scanned} páginas de SERIES_OPERACION; "
            "para buscar en TODA la operación usa `series-meta-op` con filtros --g)")
    out(f"{len(series)} serie(s) (página {args.page}):")
    for s in series[: args.max or len(series)]:
        out(f"  {s.get('COD',''):<12} {(s.get('Nombre') or '').strip()[:70]}")
    if args.max and len(series) > args.max:
        out(f"  … y {len(series) - args.max} más (usa --max para ampliar)")


def cmd_values_serie(args):
    p = {"det": args.det if args.det is not None else 1}  # det=1: incluye objeto Variable
    url, r = get(f"VALORES_SERIE/{urllib.parse.quote(str(args.cod))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    vals = r.json()
    if args.json:
        return out(raw_json(vals))
    for v in vals:
        var = v.get("Variable") or {}
        nombre_var = var.get("Nombre") or v.get("T3_Variable") or "?"
        out(f"  {nombre_var}: {v.get('Nombre')} (id {v.get('Id')}, código {v.get('Codigo')})")


# ----------------------------------------------------- variables y valores
def cmd_variables(args):
    p = {"page": args.page} if args.page else None
    url, r = get(f"VARIABLES_OPERACION/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    vars_ = r.json()
    if args.json:
        return out(raw_json(vars_))
    for v in vars_:
        out(f"  Id {v['Id']:>4} | {(v.get('Nombre') or '').strip()} | código: {v.get('Codigo') or '—'}")


def cmd_values(args):
    p = {}
    if args.det is not None:
        p["det"] = args.det
    if args.clasif is not None:
        p["clasif"] = args.clasif
    if args.op:
        url, r = get(f"VALORES_VARIABLEOPERACION/{args.var}/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    else:
        url, r = get(f"VALORES_VARIABLE/{args.var}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    vals = r.json()
    if args.json:
        return out(raw_json(vals))
    for v in vals:
        out(f"  Id {v['Id']:>7} | {(v.get('Nombre') or '').strip()} | código: {v.get('Codigo') or '—'}")


def cmd_children(args):
    p = {"det": args.det if args.det is not None else 2}  # det=2: incluye JerarquiaPadres
    url, r = get(f"VALORES_HIJOS/{args.var}/{args.val}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    vals = r.json()
    if args.json:
        return out(raw_json(vals))
    for v in vals:
        padres = " ← " + ", ".join(p.get("Nombre", "") for p in (v.get("JerarquiaPadres") or []))
        out(f"  Id {v['Id']:>7} | {(v.get('Nombre') or '').strip()} | código: {v.get('Codigo') or '—'}{padres}")


# ------------------------------------------------------- grupos y filtros g
def cmd_groups(args):
    url, r = get(f"GRUPOS_TABLA/{args.id}", lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    gs = r.json()
    if args.json:
        return out(raw_json(gs))
    for g in gs:
        out(f"  Id {g['Id']:>7} | {g.get('Nombre')}")


def cmd_group_values(args):
    p = {"det": args.det} if args.det is not None else None
    url, r = get(f"VALORES_GRUPOSTABLA/{args.id}/{args.group}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    vals = r.json()
    if args.json:
        return out(raw_json(vals))
    for v in vals:
        out(f"  Id {v['Id']:>7} | {(v.get('Nombre') or '').strip()} | código: {v.get('Codigo') or '—'}")


def _g_params(args):
    if not args.g:
        raise SystemExit("Este subcomando exige al menos un --g 'id_var:id_valor' (o 'id_var:' para todos los valores)")
    return {f"g{i + 1}": g for i, g in enumerate(args.g)}


def cmd_meta_op(args):
    p = _g_params(args)
    if args.p is not None:
        p["p"] = args.p
    if args.nult is not None:
        p["nult"] = args.nult
    if args.tip:
        p["tip"] = args.tip
    if args.det is not None:
        p["det"] = args.det
    url, r = get(f"DATOS_METADATAOPERACION/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    data = r.json()
    if args.json:
        return out(raw_json(data))
    if not data:
        return out("(sin datos para ese filtro)")
    out(f"{len(data)} serie(s):")
    _print_series_data(data, rows=args.rows, tidy=args.tidy)


def cmd_series_meta_op(args):
    p = _g_params(args)
    if args.p is not None:
        p["p"] = args.p
    if args.det is not None:
        p["det"] = args.det
    if args.tip:
        p["tip"] = args.tip
    url, r = get(f"SERIE_METADATAOPERACION/{urllib.parse.quote(str(args.op))}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    series = r.json()
    if args.json:
        return out(raw_json(series))
    for s in series:
        out(f"  {s.get('COD',''):<12} {(s.get('Nombre') or '').strip()[:70]}")


# ------------------------------------------------------ catálogos y demás
def cmd_periodicities(args):
    url, r = get("PERIODICIDADES", lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    ps = r.json()
    if args.json:
        return out(raw_json(ps))
    for p in ps:
        out(f"  Id {p['Id']:>2} | {p.get('Nombre')} | {p.get('Codigo')}")


def cmd_publications(args):
    p = {}
    if args.det is not None:
        p["det"] = args.det
    if args.tip:
        p["tip"] = args.tip
    path = f"PUBLICACIONES_OPERACION/{urllib.parse.quote(str(args.op))}" if args.op else "PUBLICACIONES"
    url, r = get(path, p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    pubs = r.json()
    if args.json:
        return out(raw_json(pubs))
    for pb in pubs:
        out(f"  Id {pb['Id']:>4} | {pb.get('Nombre')}")


def cmd_pub_dates(args):
    p = {"tip": args.tip if args.tip else "A"}  # tip=A: Fecha en formato ISO
    url, r = get(f"PUBLICACIONFECHA_PUBLICACION/{args.pub}", p, lang=args.lang)
    if args.url:
        return out(url)
    r.raise_for_status()
    pubs = r.json()
    if args.json:
        return out(raw_json(pubs))
    for pb in pubs:
        out(f"  {fmt_fecha(pb.get('Fecha'))} | {pb.get('Nombre')} | año: {pb.get('Anyo')}")


# ------------------------------------------------------------------- main
def build_parser():
    pr = argparse.ArgumentParser(prog="ine.py", description="Cliente CLI de la API pública del INE (WSTempus)")
    pr.add_argument("--lang", choices=["ES", "EN"], default="ES")
    sub = pr.add_subparsers(dest="cmd", required=True)

    def common(p, det=True, tip=False, page=False):
        if det:
            p.add_argument("--det", type=int, choices=[0, 1, 2])
        if tip:
            p.add_argument("--tip", choices=["A", "M", "AM", "raw"], help="A=amigable (defecto), M=metadatos, AM=ambos, raw=sin tip")
        if page:
            p.add_argument("--page", type=int, default=1)

    p = sub.add_parser("ops", help="operaciones disponibles")
    p.add_argument("--geo", type=int, choices=[0, 1])
    p.add_argument("--search")
    common(p, page=True)
    p.set_defaults(func=cmd_ops)

    p = sub.add_parser("search", help="buscar operaciones")
    p.add_argument("kw")
    p.add_argument("--geo", type=int, choices=[0, 1])
    p.add_argument("--page", type=int, default=1)
    p.set_defaults(func=cmd_ops)

    p = sub.add_parser("op", help="detalle de operación")
    p.add_argument("id")
    common(p)
    p.set_defaults(func=cmd_op)

    p = sub.add_parser("tables", help="tablas de una operación")
    p.add_argument("op")
    p.add_argument("--geo", type=int, choices=[0, 1])
    p.add_argument("--search")
    common(p, tip=True)
    p.set_defaults(func=cmd_tables)

    p = sub.add_parser("table-data", help="datos de una tabla")
    p.add_argument("id")
    p.add_argument("--nult", type=int)
    p.add_argument("--date")
    p.add_argument("--tv", action="append")
    p.add_argument("--format", choices=["js", "csv", "csv_sc", "px", "xlsx"], default="js")
    p.add_argument("--rows", type=int, help="filas mostradas en pantalla")
    p.add_argument("--tidy", action="store_true", help="una fila por observación")
    p.add_argument("--out", help="guardar a archivo")
    common(p, tip=True)
    p.set_defaults(func=cmd_table_data)

    p = sub.add_parser("series", help="metadatos de una serie")
    p.add_argument("cod")
    common(p, tip=True)
    p.set_defaults(func=cmd_series)

    p = sub.add_parser("series-data", help="datos de una serie")
    p.add_argument("cod")
    p.add_argument("--nult", type=int)
    p.add_argument("--date")
    p.add_argument("--rows", type=int)
    p.add_argument("--tidy", action="store_true")
    p.add_argument("--out")
    common(p, tip=True)
    p.set_defaults(func=cmd_series_data)

    p = sub.add_parser("series-table", help="series de una tabla")
    p.add_argument("id")
    p.add_argument("--tv", action="append")
    p.add_argument("--search")
    p.add_argument("--max", type=int)
    common(p, tip=True)
    p.set_defaults(func=cmd_series_table)

    p = sub.add_parser("series-op", help="series de una operación")
    p.add_argument("op")
    p.add_argument("--search")
    p.add_argument("--max", type=int)
    common(p, tip=True, page=True)
    p.set_defaults(func=cmd_series_op)

    p = sub.add_parser("values-serie", help="variables/valores de una serie")
    p.add_argument("cod")
    common(p)
    p.set_defaults(func=cmd_values_serie)

    p = sub.add_parser("variables", help="variables de una operación")
    p.add_argument("op")
    common(p, page=True, det=False)
    p.set_defaults(func=cmd_variables)

    p = sub.add_parser("values", help="valores de una variable")
    p.add_argument("var", type=int)
    p.add_argument("--op", help="acotar a una operación")
    p.add_argument("--clasif", type=int)
    common(p)
    p.set_defaults(func=cmd_values)

    p = sub.add_parser("groups", help="grupos de una tabla")
    p.add_argument("id")
    p.set_defaults(func=cmd_groups)

    p = sub.add_parser("group-values", help="valores de un grupo de tabla")
    p.add_argument("id")
    p.add_argument("group", type=int)
    common(p)
    p.set_defaults(func=cmd_group_values)

    p = sub.add_parser("meta-op", help="datos filtrados por metadatos")
    p.add_argument("op")
    p.add_argument("--g", action="append", help="filtro id_var:id_valor (repetible)")
    p.add_argument("--p", type=int, choices=[1, 3, 6, 12])
    p.add_argument("--nult", type=int)
    p.add_argument("--rows", type=int)
    p.add_argument("--tidy", action="store_true")
    common(p, tip=True)
    p.set_defaults(func=cmd_meta_op)

    p = sub.add_parser("series-meta-op", help="series filtradas por metadatos")
    p.add_argument("op")
    p.add_argument("--g", action="append")
    p.add_argument("--p", type=int, choices=[1, 3, 6, 12])
    common(p, tip=True)
    p.set_defaults(func=cmd_series_meta_op)

    p = sub.add_parser("periodicities", help="periodicidades")
    p.set_defaults(func=cmd_periodicities)

    p = sub.add_parser("publications", help="publicaciones")
    p.add_argument("op", nargs="?")
    common(p, tip=True)
    p.set_defaults(func=cmd_publications)

    p = sub.add_parser("pub-dates", help="fechas de publicación")
    p.add_argument("pub", type=int)
    p.add_argument("--tip", choices=["A", "M", "AM", "raw"])
    p.set_defaults(func=cmd_pub_dates)

    p = sub.add_parser("children", help="valores hijo (jerarquías)")
    p.add_argument("var", type=int)
    p.add_argument("val", type=int)
    common(p)
    p.set_defaults(func=cmd_children)

    # --url y --json funcionan también después del subcomando
    for _sp in sub.choices.values():
        _sp.add_argument("--url", action="store_true", help="solo imprimir la URL construida")
        _sp.add_argument("--json", action="store_true", help="volcar la respuesta JSON cruda")
    return pr


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args()
    try:
        args.func(args)
    except requests.exceptions.ConnectionError as e:
        print(f"Error de conexión con servicios.ine.es: {e}", file=sys.stderr)
        sys.exit(2)
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
