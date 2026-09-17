# -*- coding: utf-8 -*-
"""Controles de integridad de una version reescrita frente al original.

    python verifica.py original.txt nueva.txt [--base base.json]

Pasarle `--base` (el JSON de Pangram del original) permite comprobar que los tramos que el
detector marco como humanos siguen intactos, que es la comprobacion mas util: esos tramos
funcionan y tocarlos es riesgo puro.

Lanzalo SIEMPRE antes de gastar creditos. Un analisis con una cifra perdida es un credito tirado.

Salida 0 si todo esta en verde, 1 si hay algo que revisar. La cadencia no hace fallar la
verificacion: es un aviso, porque compite con el destemplado y el destemplado gana.
"""
import argparse
import difflib
import io
import json
import re
import statistics as st
import sys
from collections import Counter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def frases(txt):
    txt = re.sub(r'\s+', ' ', txt)
    return [f.strip() for f in re.split(r'(?<=[.!?])\s+', txt) if len(f.strip()) > 15]


def frases_con_offset(t):
    """Frases del texto crudo con sus posiciones. Corta tambien en salto de linea, para no
    fusionar un parrafo que termina sin punto con el parrafo siguiente."""
    out, ini = [], 0
    for m in re.finditer(r'[.!?]+(?=\s|$)|\n', t):
        fin = m.end()
        frag = t[ini:fin].strip()
        if len(frag) > 15:
            out.append((ini, fin, re.sub(r'\s+', ' ', frag)))
        ini = fin
    resto = t[ini:].strip()
    if len(resto) > 15:
        out.append((ini, len(t), re.sub(r'\s+', ' ', resto)))
    return out


def cifras(t):
    return re.findall(r'\d[\d.,]*\s*%|\b\d[\d.,]*\b', t)


def longitudes(txt):
    t = re.sub(r'\s+', ' ', txt)
    return [len(f.split()) for f in re.split(r'(?<=[.!?])\s+', t) if len(f.strip()) > 3]


def carga_base(p):
    try:
        return json.load(io.open(p, encoding='utf-8'))
    except Exception:
        return None


def perfil_objetivo(d):
    t = d['text']
    hum = ' '.join(t[s['start']:s['end']] for s in d['segments'] if s['label'] == 'Human')
    L = longitudes(hum)
    if len(L) < 5:
        return None
    return {'media': st.mean(L), 'desv': st.pstdev(L), 'n': len(L),
            'cortas': 100.0 * sum(1 for x in L if x <= 8) / len(L),
            'muylargas': 100.0 * sum(1 for x in L if x > 32) / len(L)}


def _contiene(texto, frase):
    """Busca la frase en el texto crudo tolerando cualquier espaciado."""
    partes = [re.escape(w) for w in frase.split()]
    if not partes:
        return True
    return re.search(r'\s+'.join(partes), texto) is not None


def frases_humanas(d):
    """Frases del original cuyo punto medio cae dentro de un fragmento marcado como humano.

    Mapear por punto medio, y no recortar los bordes de cada fragmento, es lo que evita el
    fallo silencioso: los limites de fragmento de Pangram cortan a mitad de palabra, y
    descartar la primera y la ultima frase de cada uno deja sin comprobar los fragmentos de
    una o dos frases, que en prosa densa en citas son la mayoria.
    """
    t = d['text']
    segs = [s for s in d['segments'] if s['label'] == 'Human']
    out = []
    for ini, fin, frag in frases_con_offset(t):
        medio = (ini + fin) // 2
        if any(s['start'] <= medio < s['end'] for s in segs):
            out.append(frag)
    return out


def parecida(f, candidatas, umbral):
    for c in candidatas:
        if difflib.SequenceMatcher(None, f, c).ratio() >= umbral:
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('original')
    ap.add_argument('nueva')
    ap.add_argument('--base', help='JSON de Pangram del original')
    a = ap.parse_args()

    orig = io.open(a.original, encoding='utf-8').read()
    nuevo = io.open(a.nueva, encoding='utf-8').read()
    base = carga_base(a.base) if a.base else None
    ok = True

    print('=' * 78)
    print('VERIFICACION  %s -> %s' % (a.original, a.nueva))
    print('  palabras: %d -> %d  (%+.1f%%)' % (
        len(orig.split()), len(nuevo.split()),
        100.0 * (len(nuevo.split()) - len(orig.split())) / max(len(orig.split()), 1)))
    print('=' * 78)

    print('\n-- 1. Tramos humanos del original --')
    if base is None:
        print('  (sin --base no se puede comprobar. Pasa el JSON de Pangram del original: es la')
        print('   comprobacion mas valiosa de todas.)')
    else:
        fh = frases_humanas(base)
        if not fh:
            print('  El original no tenia ningun fragmento humano.')
        else:
            cand = frases(nuevo)
            # La comparacion tiene que tolerar el espaciado: las frases protegidas vienen
            # normalizadas y el texto crudo puede llevar tabuladores (una tabla) o un salto
            # de linea en medio. Buscarlas literalmente marcaba MODIFICADA cada fila de
            # tabla, que es peor que no comprobar: entrena a ignorar el aviso.
            perdidas = [f for f in fh
                        if not _contiene(nuevo, f) and not parecida(f, cand, 0.95)]
            print('  %d/%d frases protegidas conservadas' % (len(fh) - len(perdidas), len(fh)))
            for f in perdidas:
                print('  MODIFICADA: %s' % f[:110])
                ok = False
            if perdidas:
                print('  Esos tramos ya puntuaban humanos. Si el cambio no fue deliberado, deshazlo.')

    print('\n-- 2. Cifras --')
    co, cn = Counter(cifras(orig)), Counter(cifras(nuevo))
    faltan = sorted((co - cn).elements())
    sobran = sorted((cn - co).elements())
    print('  faltan: %s' % (', '.join(faltan) if faltan else 'ninguna'))
    print('  nuevas: %s' % (', '.join(sobran) if sobran else 'ninguna'))
    if faltan:
        print('  Una cifra que desaparece es contenido perdido. Restaurala. En un texto con')
        print('  citas, un anio que falta puede ser una referencia bibliografica rota.')
        ok = False
    if sobran:
        print('  Comprueba una por una que cada cifra nueva ya estaba en el original en otro')
        print('  sitio (repeticion deliberada) y que no te has inventado ninguna.')

    print('\n-- 3. Rayas y guiones largos --')
    malos = [c for c in ('—', '–') if c in nuevo]
    en_orig = [c for c in ('—', '–') if c in orig]
    if malos and not en_orig:
        print('  ENCONTRADOS: %s  (el original no los usaba: quitalos)' % ' '.join(malos))
        ok = False
    elif malos:
        print('  Presentes, y el original tambien los usaba: es estilo del autor, se respetan.')
    else:
        print('  ninguno')

    print('\n-- 4. Cadencia (aviso, no bloquea) --')
    L = longitudes(nuevo)
    obj = perfil_objetivo(base) if base else None
    print('  nueva    media=%4.1f  desv=%4.1f  <=8: %2.0f%%  >32: %2.0f%%' % (
        st.mean(L), st.pstdev(L),
        100.0 * sum(1 for x in L if x <= 8) / len(L),
        100.0 * sum(1 for x in L if x > 32) / len(L)))
    if obj:
        print('  objetivo media=%4.1f  desv=%4.1f  <=8: %2.0f%%  >32: %2.0f%%   (tramos humanos'
              ' del original, n=%d)' % (obj['media'], obj['desv'], obj['cortas'],
                                        obj['muylargas'], obj['n']))
        d = abs(st.pstdev(L) - obj['desv'])
        if d > 2.0 and obj['n'] >= 12:
            print('  A %.1f del objetivo. Acercala si puedes, pero no deshagas un destemplado' % d)
            print('  para conseguirlo: destemplar mueve el veredicto y la cadencia sola no.')
        elif d > 2.0:
            print('  A %.1f del objetivo, calculado con solo %d frases humanas: margen ancho,' % (
                d, obj['n']))
            print('  no lo persigas.')
    else:
        print('  Sin objetivo del propio autor. No apliques un perfil de otro texto: la')
        print('  direccion correcta cambia con el genero.')

    print('\n-- 5. Frases del original que ya no aparecen --')
    fo, fn = frases(orig), frases(nuevo)
    sm = difflib.SequenceMatcher(None, fo, fn)
    desap = []
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ('delete', 'replace'):
            desap.extend(fo[i1:i2])
    for f in desap:
        print('  - %s' % f[:150])
    print('\n  %d frases. La mayoria estaran reescritas, no perdidas.' % len(desap))
    print('  COMPROBAR CIFRAS NO ES COMPROBAR AFIRMACIONES: recorre esta lista una por una y')
    print('  confirma que el contenido de cada frase sigue vivo en algun sitio. En el caso que')
    print('  origino esta skill, el control de cifras estaba en verde y aun asi una reescritura')
    print('  se habia llevado por delante el criterio central del ensayo, que no tenia numeros.')

    print('\n' + '=' * 78)
    print('RESULTADO: %s' % ('EN VERDE' if ok else 'REVISAR lo marcado antes de medir'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
