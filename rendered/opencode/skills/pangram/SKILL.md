---
name: pangram
description: >-
  Detecta si un texto está escrito por IA usando Pangram (suscripción del usuario), con veredicto
  global y desglose fragmento a fragmento: qué partes son IA, cuáles humanas y con qué probabilidad.
  Úsala SIEMPRE que se pida comprobar, verificar, detectar o "pasar por Pangram" la autoría de un
  texto — "¿esto lo ha escrito una IA?", "analiza este TFG/tesis/artículo/redacción", "qué partes de
  este texto parecen IA", "revisa si el trabajo de mis alumnos es ChatGPT", "detector de IA",
  "AI detection", "humanizado" — incluso si no se menciona Pangram explícitamente, y también para
  análisis en lote de carpetas de documentos, análisis de una URL, o consultar/reabrir análisis
  anteriores del historial. No la uses para *escribir* texto que parezca humano ni para reescribir
  o "humanizar" (eso es otra tarea), ni para detectar plagio sin análisis de IA, ni para imágenes.
---

# Pangram — detección de IA en textos

Pangram es un detector de texto generado por IA. Este entorno tiene `pangram-auto`, un cliente que
automatiza la web de Pangram con la sesión del usuario: CLI, librería Python y API HTTP local.

Lo valioso frente a mirar la web a mano: además del veredicto global devuelve el **desglose por
fragmentos** (segmentos contiguos con su propia probabilidad e índices de carácter), y permite
lotes, informes HTML/CSV/JSON y reconsulta gratuita del historial.

## Primero: localizar la herramienta y comprobar la sesión

Resuelve el ejecutable en este orden y usa el primero que responda:

1. `pangram` (si está en el PATH)
2. `C:\Users\PcVIP\Documents\Stuff\Pangram\.venv\Scripts\pangram.exe`
3. desde el repo: `.venv\Scripts\python -m pangram_auto`

Si ninguno responde, `pangram-auto` no está instalado en esta máquina: localiza el repo (un
`pyproject.toml` con `name = "pangram-auto"`) e instálalo en un entorno virtual con
`pip install -e ".[all]"`, o pregunta al usuario dónde lo tiene. No intentes hablar con la API de
Pangram a mano: la autenticación y el sondeo tienen trampas que el cliente ya resuelve.

```bash
pangram whoami          # usuario, plan y créditos restantes
```

Si falla con "sesión no válida o caducada", la cookie ha expirado. No intentes adivinarla: pide al
usuario que ejecute `pangram login --from-browser`, o que abra
`https://web.pangram.com/api/session-status/` en el navegador donde tenga la sesión y copie el valor
de `sessionId` para `pangram login --session-id "<valor>"`.

## Presupuesto: los créditos son dinero real

Es una suscripción personal (3000 créditos/mes), no un plan de API. **1 crédito por cada 100
palabras empezadas**; `--plagiarism` duplica el coste. Mínimo 50 palabras, máximo 100 000 caracteres.

Regla de gasto, sin ambigüedad:

- **Hasta 50 créditos (≈5000 palabras)**: si el usuario ha pedido el análisis, adelante. No hace
  falta preguntarle "¿seguro?" por 3 créditos; eso solo entorpece.
- **Más de 50 créditos**: di cuántas palabras y cuántos créditos son y **espera su visto bueno**
  antes de lanzarlo. La propia CLI te frena: en ejecución no interactiva rechaza cualquier gasto
  por encima de ese umbral salvo que pases `--yes`, así que si te devuelve ese error no lo saltes
  con `--yes` por inercia — pregunta primero.
- **Lo que el usuario no pidió, no se analiza.** Si hay una carpeta con 40 documentos y solo te han
  preguntado por uno, analiza uno.

Además:

- Comprueba créditos con `whoami` cuando el texto sea largo o sean varios documentos.
- Si el texto ya se analizó antes, reabre el resultado del historial (`pangram history`,
  `pangram history show <uuid>`): es **gratis** y devuelve exactamente los mismos datos.
- No trocees un texto largo para "ahorrar": cambiaría el resultado, porque Pangram usa una ventana
  deslizante sobre el documento completo. Si excede los 100 000 caracteres, dilo y pide criterio.

## Flujo que funciona

1. `pangram whoami` — confirma que la sesión vive y cuántos créditos quedan.
2. Estima el tamaño del texto (palabras ÷ 100 = créditos) y aplica la regla de gasto de arriba.
3. Lanza el análisis con `-T` si interesa ver dónde está la IA, y con `--out ... --format html,json`
   si el usuario va a querer conservarlo o enseñarlo.
4. Presenta veredicto global **y** desglose por fragmentos (ver más abajo), y da la ruta del informe.

## Comandos

| Objetivo | Comando |
|---|---|
| Texto suelto | `pangram check "..." -T` |
| Fichero (txt, md, html, pdf, docx) | `pangram check -f ruta.pdf -T` |
| Desde stdin | `type doc.txt \| pangram check --stdin` |
| Una URL | `pangram check --url https://...` |
| Carpeta entera | `pangram batch ./textos -p "*.md" -o informes` |
| Informe HTML + JSON | `pangram check -f doc.docx --out informes --format html,json` |
| Salida para procesar | `pangram check -f doc.txt --json` |
| Historial (gratis) | `pangram history` · `pangram history show <uuid> -T` |
| Borrar del historial | `pangram history delete <uuid>` |
| API HTTP local | `pangram serve --port 8765` |

Banderas que importan:

- `-T` / `--show-text`: imprime el texto con cada fragmento coloreado. Úsalo cuando el usuario
  quiera ver *dónde* está la IA, no solo cuánta hay.
- `--json`: estructura completa por stdout, para encadenar con otras herramientas.
- `--yes`: salta la confirmación de gasto. Sin terminal, la CLI deja pasar sola lo barato y rechaza
  lo que supere 50 créditos: ahí `--yes` significa "el usuario ya lo ha aprobado", no "cállate".
- `--forget`: borra la entrada del historial de Pangram nada más recibir el resultado. **Por defecto
  no lo uses**: dejar el análisis en el historial permite reabrirlo gratis más tarde. Úsalo solo si
  el usuario menciona confidencialidad, datos personales, material sin publicar, o pide que no quede
  rastro. Ojo con `--no-log`: no sirve para eso. La web siempre manda `logging:true`; mandando
  `false` la petición se acepta pero el análisis aparece igualmente en el historial (comprobado),
  así que su efecto real es desconocido y no debes contar con él.
- `--out DIR --format html,json,md,csv`: informes en disco. El HTML es autocontenido y muestra el
  texto resaltado; es lo que conviene entregar cuando hay que enseñar el resultado a alguien.

## Interpretar el resultado

El resultado tiene dos niveles y conviene reportar los dos:

**Documento**: `verdict` (`AI Generated`, `AI Detected`, `Human Written`…), `ai_likelihood` (0–1),
`fraction_ai` / `fraction_human` / `fraction_ai_assisted` (proporción del texto de cada tipo) y una
descripción de cómo se reparte la IA por el documento.

**Fragmentos** (`segments`): tramos contiguos con `start`/`end` (índices de carácter sobre el texto
original), `label` (`AI-Generated` / `Human` / `AI-Assisted`), `confidence` (`High`/`Medium`/`Low`),
`ai_likelihood` propio, `word_count`, y `is_humanized` / `humanizer_score` (indicios de texto pasado
por un "humanizador").

Dos matices que evitan conclusiones erróneas:

- **Un solo fragmento no significa "análisis pobre"**: Pangram fusiona ventanas contiguas con la
  misma etiqueta, así que un texto homogéneo sale como un único segmento. Es información, no fallo.
- **`confidence` modula el veredicto**: un fragmento marcado IA con confianza `Medium` y 52 % no es
  comparable a otro con `High` y 93 %. Menciona la confianza cuando el resultado sea intermedio.

Trasládalo con prudencia: Pangram da una probabilidad, no una prueba. Si el usuario va a tomar una
decisión con consecuencias (calificar a un alumno, acusar a alguien), dilo explícitamente y apóyate
en los fragmentos concretos en lugar de en un único porcentaje.

## Cómo presentar el resultado

Estructura que funciona bien en la respuesta al usuario:

```
**Veredicto**: <verdict> — <ai_likelihood en %> de probabilidad de IA
**Reparto**: IA X% · IA asistida Y% · Humano Z%  (N fragmentos)

| # | Rango | Palabras | Veredicto | Confianza | IA |
|---|---|---|---|---|---|
(una fila por fragmento; cita literalmente el inicio de los fragmentos relevantes)

<una o dos frases interpretando el patrón: concentrado al final, alterna párrafos, homogéneo...>
```

Cuando haya varios documentos, encabeza con una tabla de una fila por documento ordenada por
probabilidad y luego detalla solo los casos interesantes. Si generaste informes con `--out`, da las
rutas: el HTML es lo que el usuario puede abrir y compartir.

## Errores y qué hacer

| Síntoma | Causa | Salida |
|---|---|---|
| "Sesión no válida o caducada" (código 2) | cookie expirada | pide `pangram login --from-browser` |
| "Créditos insuficientes" (código 3) | cuota agotada | di cuántos faltan; ofrece analizar menos |
| "necesita al menos 50 palabras" | texto corto | no hay solución técnica: hace falta más texto |
| "el máximo es 100.000 caracteres" | texto enorme | consulta al usuario cómo dividirlo |
| Timeout esperando el análisis | backend lento | el análisis sigue vivo: búscalo en `pangram history` |

Códigos de salida: `0` correcto · `1` error · `2` sesión · `3` créditos.

## Uso programático

Desde Python, cuando haya que integrarlo en otro flujo:

```python
from pangram_auto import PangramClient

with PangramClient() as client:
    result = client.analyze_text(texto)
    print(result.verdict, result.percent)
    for s in result.segments:
        print(s.start, s.end, s.label, s.ai_likelihood)
```

Para servirlo a otras herramientas o lenguajes: `pangram serve` levanta una API local con
`/analyze`, `/analyze/file`, `/analyze/url`, `/history` y `/session` (docs en `/docs`).

## Detalle adicional

- `references/api.md` — endpoints internos de Pangram, formato exacto de las respuestas y campos
  del JSON. Léelo si necesitas ir más allá de la CLI o interpretar campos poco habituales.
- `references/recetas.md` — recetas para casos concretos: comparar varias versiones de un texto,
  auditar una carpeta de entregas, extraer solo los fragmentos IA, integrar en un script.
