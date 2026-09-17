# -*- coding: utf-8 -*-
"""Mide una unidad donde va a vivir: contexto real izquierdo + candidata + contexto real derecho."""
import re, argparse

def sent_left(txt, n):
    sub = ' '.join(txt.split()[-n:])
    m = re.search(r'[.!?]\s+([A-ZÁÉÍÓÚÑ¿¡"“])', sub)
    return sub[m.start(1):] if m else sub

def sent_right(txt, n):
    sub = ' '.join(txt.split()[:n])
    m = list(re.finditer(r'[.!?](?=\s|$)', sub))
    return sub[:m[-1].end()] if m else sub

a = argparse.ArgumentParser()
a.add_argument('--doc',   required=True)   # documento de trabajo
a.add_argument('--cand',  required=True)   # candidata
a.add_argument('--start', required=True)   # marca literal donde empieza lo que sustituye
a.add_argument('--end',   required=True)   # marca literal donde termina, o EOF
a.add_argument('--probe', required=True)
a.add_argument('--left',  type=int, default=520)
a.add_argument('--right', type=int, default=300)
a.add_argument('--commit', action='store_true')
o = a.parse_args()

doc  = open(o.doc,  encoding='utf-8').read()
cand = open(o.cand, encoding='utf-8').read().strip()
i = doc.index(o.start)
j = len(doc) if o.end == 'EOF' else doc.index(o.end, i)

probe = (sent_left(doc[:i], o.left).strip() + "\n\n" + cand + "\n\n"
         + sent_right(doc[j:], o.right).strip())
open(o.probe, 'w', encoding='utf-8').write(probe)

run, tot = len(cand.split()), len(probe.split())
print(f"sustituye {len(doc[i:j].split())}w -> {run}w | sonda {tot}w "
      f"| serie {100*run/tot:.1f}% | ~{-(-tot//100)} creditos")
if o.commit:
    open(o.doc, 'w', encoding='utf-8').write(doc[:i] + cand + "\n\n" + doc[j:])
    print("COMMIT")
