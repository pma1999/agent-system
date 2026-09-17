# Recetas

Casos concretos que aparecen a menudo. Todo asume que `pangram` está resuelto (ver SKILL.md) y que
la sesión es válida.

## Índice

1. Auditar una carpeta de entregas
2. Extraer solo los fragmentos marcados como IA
3. Comparar dos versiones de un mismo texto
4. Analizar un documento muy largo
5. Reabrir análisis anteriores sin gastar créditos
6. Encadenar con otras herramientas (JSON)
7. Servir la API a otro lenguaje o script
8. Texto sensible o confidencial

---

## 1. Auditar una carpeta de entregas

```bash
pangram batch ./entregas -p "*.docx" -o informes/entregas
```

Genera un `.html` y un `.json` por documento, más `resumen.csv` (una fila por documento) y
`fragmentos.csv` (una fila por fragmento de cada documento). El lote cachea por hash del texto: si
falla a mitad y lo relanzas, lo ya analizado no se vuelve a cobrar.

Para ordenar los resultados por sospecha:

```bash
python -c "import csv,sys; r=sorted(csv.DictReader(open('informes/entregas/resumen.csv',encoding='utf-8-sig')), key=lambda x: -float(x['ai_likelihood'] or 0)); [print(f\"{float(x['ai_likelihood'])*100:5.1f}%  {x['source']}\") for x in r]"
```

Concurrencia por defecto: 2. Subirla con `-j` acelera poco y arriesga un 429.

## 2. Extraer solo los fragmentos marcados como IA

```bash
pangram check -f documento.docx --json > resultado.json
python -c "
import json
d = json.load(open('resultado.json', encoding='utf-8'))
for s in d['segments']:
    if s['label'] == 'AI-Generated':
        print(f\"[{s['start']}:{s['end']}] {s['ai_likelihood']*100:.1f}% ({s['confidence']})\")
        print(s['text'][:300], '\n')
"
```

Los índices `start`/`end` son de carácter sobre el texto original, así que sirven para resaltar el
fragmento en el documento fuente o para citarlo literalmente.

## 3. Comparar dos versiones de un mismo texto

Útil cuando alguien reescribe un texto para reducir la señal de IA.

```bash
pangram check -f v1.txt --json > v1.json
pangram check -f v2.txt --json > v2.json
python -c "
import json
a, b = (json.load(open(f, encoding='utf-8')) for f in ('v1.json','v2.json'))
for n, d in (('v1', a), ('v2', b)):
    print(f\"{n}: {d['verdict']:<15} {d['ai_likelihood']*100:5.1f}%  IA={d['fractions']['ai']:.0%}  fragmentos={len(d['segments'])}\")
"
```

Cuesta el doble de créditos, claro. Avísalo antes.

## 4. Analizar un documento muy largo

El límite es 100 000 caracteres (~15 000 palabras). Por encima, la CLI se niega, y con razón:
trocear cambia el resultado porque la ventana deslizante trabaja sobre el documento completo, así
que los porcentajes de los trozos no son comparables con los del entero.

Si hay que hacerlo igualmente, córtalo por unidades con sentido propio (capítulos, secciones), nunca
a ciegas por número de caracteres, y presenta cada parte como un análisis independiente en lugar de
promediar los porcentajes.

## 5. Reabrir análisis anteriores sin gastar créditos

```bash
pangram history -n 20                 # lista con UUIDs
pangram history show <uuid> -T        # desglose completo, gratis
pangram history show <uuid> --out informes --format html --open
```

Antes de analizar algo que suene a repetido, mira el historial: `pangram history --search "palabra"`.

## 6. Encadenar con otras herramientas (JSON)

`--json` imprime la estructura completa por stdout. Campos más útiles:

```
verdict, prediction, ai_likelihood, word_count
fractions.{ai,human,ai_assisted,breakdown}
segment_counts.{ai,human,ai_assisted,total}
word_split.{ai,human,ai_assisted}
segments[].{index,start,end,label,confidence,ai_likelihood,word_count,is_humanized,text}
textquery_uuid, url, credits_required, credits_remaining
```

En scripts no interactivos añade `--yes`, o el comando se quedará esperando la confirmación de gasto.

## 7. Servir la API a otro lenguaje o script

```bash
pangram serve --port 8765 --token secreto   # deja el proceso vivo
curl -X POST http://127.0.0.1:8765/analyze \
     -H "Content-Type: application/json" -H "X-API-Key: secreto" \
     -d '{"text":"..."}'
```

`?format=html` devuelve el informe HTML ya montado, útil para incrustar en otra interfaz.
`/estimate` calcula el coste sin gastar nada. Documentación viva en `/docs`.

## 8. Texto sensible o confidencial

Por defecto el análisis queda guardado en el historial de Pangram del usuario, igual que en la web.
`--no-log` **no** lo evita: la web siempre manda `logging:true`, y mandando `false` el análisis
aparece igual en el historial (comprobado), así que su efecto real es desconocido.
Para que no quede rastro en la cuenta, añade `--forget`, que borra la entrada al recibir el resultado:

```bash
pangram check -f confidencial.docx --no-log --forget
pangram history delete <uuid>            # si hay que limpiar algo a posteriori
```

El borrado es irreversible, así que hazlo solo cuando el usuario lo pida. Y ten presente que el texto
viaja igualmente a los servidores de Pangram: esto solo controla lo que queda almacenado en la cuenta.
Si eso no es aceptable, no lo analices.
