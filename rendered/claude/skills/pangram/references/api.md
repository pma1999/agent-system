# API interna de Pangram y formato de datos

Referencia verificada contra el servicio real (`web.pangram.com`, septiembre 2026). Léela cuando
necesites algo que la CLI no expone, interpretar un campo raro o depurar un fallo.

## Índice

1. Autenticación
2. Flujo de análisis
3. Endpoints
4. Estructura de la respuesta
5. Errores del backend
6. Límites y costes

---

## 1. Autenticación

Sesión de Django. Basta la cookie **`sessionid`** sobre `https://web.pangram.com`.

El token CSRF **no viaja en cookie** (`CSRF_USE_SESSIONS`): se pide a
`GET /api/accounts/get-csrf/`, que devuelve `{"csrfToken": "<64 chars>"}`, y se manda en la cabecera
`X-CSRFToken` en todo lo que no sea GET. Un token inventado NO vale: va ligado a la sesión.

Cabeceras que el backend valida: `Origin: https://www.pangram.com` y `Referer: https://www.pangram.com/`.

`pangram-auto` gestiona todo esto solo, incluido renovar el token si el backend devuelve 403 CSRF.

## 2. Flujo de análisis

```
GET  /api/accounts/get-csrf/                    -> {"csrfToken": "..."}
POST /api/classify-text-sliding-window/         -> 202 {"task_id", "credits_required", "status"}
POST /api/classify-text-sliding-window/status/  {"task_ids": ["..."]}
     -> {"tasks":[{"task_id","status":"background_processing"}]}
     -> {"tasks":[{"task_id","status":"success","result":{...}}]}
GET  /api/history/<textquery_uuid>/             -> el mismo resultado, persistido (gratis)
```

Estados de tarea: `background_processing`, `success`, `failed`, `not_found`.
Escalonado de sondeo que usa la web: 1 s los primeros 30 s, luego 2 s hasta 120 s, luego 5 s.

Cuerpo del envío:

```json
{"text": "...", "source": "product", "logging": true,
 "distinctId": "email@usuario", "include_plagiarism": false,
 "model": "default", "source_url": "https://..."}
```

`model` y `source_url` son opcionales.

**Cuidado con `logging`**: el front siempre manda `logging:true` (hardcodeado en su bundle).
Mandando `false` la petición se acepta, pero el análisis aparece igualmente en el historial de la
cuenta (comprobado): su efecto real es desconocido. Para eliminarlo hay que borrarlo con
`DELETE /api/history-list/bulk-delete/` `{"ids": [<id numerico>]}` — el id numérico viene en
`/api/history-list/`, no es el `textquery_uuid`.

## 3. Endpoints

| Endpoint | Método | Uso |
|---|---|---|
| `/api/session-status/` | GET | identidad, plan, `creditsRemaining`, `sessionId` |
| `/api/accounts/get-csrf/` | GET | token CSRF |
| `/api/classify-text-sliding-window/` | POST | encolar análisis |
| `/api/classify-text-sliding-window/status/` | POST | estado de tareas |
| `/api/classify-text-sliding-window/email-results/` | POST | pedir resultados por email |
| `/api/history/<uuid>/` | GET/PUT | leer análisis; actualizar `tags` o `notes` |
| `/api/history-list/` | GET | listado (`limit`, `offset`, `search`, `order`, `prediction`, `tags`, `date_from`, `date_to`) |
| `/api/history-list/bulk-delete/` | DELETE | `{"ids": [...]}` |
| `/api/url-scan/extract/` | POST | `{"url"}` → `{"url","text","truncated"}` |
| `/api/detection-models/` | GET | modelos disponibles |
| `/api/tags/`, `/api/tag-groups/` | GET | etiquetas del usuario |
| `/api/check-plagiarism/` (+ `/status/`) | POST | plagio, mismo patrón de tarea |
| `/api/csv-bulk-scan/` | POST | `{"file_name","rows":[{"text","tag"}]}` (máx. 100 filas) |
| `/api/batch-upload/`, `/api/upload/batch/<id>/` | POST | subida de ficheros por lotes |
| `/api/anonymous-scan/` | POST | análisis sin sesión (cuota mínima) |
| `/api/image-detection/*` | varios | detección en imágenes (cuota aparte) |

## 4. Estructura de la respuesta

```jsonc
{
  "text": "...",                       // en /history/<uuid>/ este campo se llama "prompt"
  "prediction": "We believe that this text is a mix of AI and human-written content.",
  "ai_likelihood": 0.667,
  "category_label": "AI",
  "textquery_uuid": "c194155c-...",    // enlace: https://www.pangram.com/history/<uuid>
  "credits_remaining": 2041,
  "response": {
    "overall": {
      "version": "4.0",
      "headline": "AI Detected",              // veredicto corto
      "prediction_short": "AI",
      "word_count": 764,
      "ai_likelihood": 0.667,
      "avg_ai_likelihood": 0.667,
      "fraction_ai": 0.693, "fraction_human": 0.307,
      "fraction_ai_assisted": 0.0, "fraction_mixed": 0.0,
      "fraction_breakdown": {
        "ai":          {"high-confidence": 0.545, "medium-confidence": 0.148, "low-confidence": 0.0},
        "ai-assisted": {"lightly": 0.0, "moderately": 0.0},
        "human":       {"high-confidence": 0.261, "medium-confidence": 0.046, "low-confidence": 0.0}
      },
      "num_ai_segments": 3, "num_human_segments": 3, "num_ai_assisted_segments": 0,
      "ai_distribution": {"title": "AI-generated content appears throughout",
                          "description": "AI-generated content is interspersed evenly..."},
      "window_indices": [[0,719],[719,1453]],   // pares [inicio, fin]
      "window_likelihoods": [0.301, 0.520],
      "windows": [ /* ver abajo */ ],
      "pages": [{"page_index":0,"start_index":0,"end_index":4971,
                 "window_indices":{"start":0,"end":5}}],
      "window_per_page": 20,
      "plagiarism": null, "ngram": null
    },
    "in_page": { /* mismos windows con campos extra por página */ }
  }
}
```

Cada elemento de `windows` (lo que `pangram-auto` llama **fragmento** o `Segment`):

| Campo | Significado |
|---|---|
| `window_index` | orden dentro del documento |
| `start_index` / `end_index` | índices de carácter sobre el texto original |
| `text` | el fragmento |
| `label` | `AI-Generated`, `Human`, `AI-Assisted` |
| `confidence` | `High`, `Medium`, `Low` |
| `ai_likelihood` | probabilidad de IA del fragmento (0–1) |
| `word_count` | palabras |
| `edit_level` | nivel de edición detectado |
| `is_humanized`, `humanizer_score` | indicios de paso por un "humanizador" |
| `token_length` | tokens que vio el modelo (solo en `in_page`) |
| `llm_prediction` | atribución a un modelo concreto, cuando la hay (solo en `in_page`) |
| `editlens.prediction_text` | veredicto del submodelo de edición |

`overall.windows` es la fuente principal; `in_page.windows` añade `token_length`, `humanizer_score`
y `llm_prediction`. `pangram-auto` los fusiona por `window_index`.

**Importante**: las ventanas contiguas con la misma etiqueta se fusionan, así que un texto homogéneo
produce un único fragmento que cubre todo el documento. No es un fallo del análisis.

## 5. Errores del backend

| Código | Cuerpo | Significado |
|---|---|---|
| 401/403 | `{"detail": "..."}` | sesión caducada o CSRF inválido |
| 402 | `{"error_type","credits_remaining","credits_required","max_words_for_remaining","can_continue_without_plagiarism"}` | sin créditos |
| 422 | `{"error": "..."}` | texto demasiado corto |
| 429 | — | límite de peticiones; respetar `Retry-After` |
| 5xx | página HTML | fallo del backend; reintentar con backoff |

## 6. Límites y costes

- 1 crédito por cada **100 palabras empezadas**. Comprobado: 189 palabras → 2; 529 → 6; 751 → 8.
  El valor autoritativo llega en `credits_required` al encolar.
- Mínimo **50 palabras**; máximo **100 000 caracteres** por análisis.
- `include_plagiarism: true` duplica el coste.
- El recuento de palabras del backend difiere ligeramente del local (tokenización distinta): usa el
  suyo (`word_count`) para informar.
- Plan Individual: 3000 créditos/mes ≈ 300 000 palabras.
