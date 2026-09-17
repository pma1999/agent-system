# Agent Studio — referencia de proyecto para candidaturas

> **Fuente de verdad.** Agent Studio es un proyecto propio de Pablo: un
> espacio de trabajo personal para crear, configurar y utilizar agentes de IA.
> Esta ficha resume la documentación del proyecto compartida por Pablo y debe
> servir como fuente para futuras candidaturas técnicas, entrevistas y
> portfolio. Describe capacidades implementadas/documentadas; no convierte por
> sí sola esas capacidades en métricas de adopción, producto comercial o
> despliegue para clientes.

## 1. Posicionamiento

Agent Studio reúne en una única aplicación la creación de agentes con prompts de
sistema propios, chat en streaming, herramientas reales, servidores MCP,
skills reutilizables, deliberación entre modelos y conexión segura con el PC
local. Está pensado como un espacio de trabajo personal, responsive y orientado
a escritorio y móvil, con una interfaz oscura propia denominada **Obsidian
Atelier**.

El proyecto demuestra capacidad full-stack y de plataforma AI: diseño de
producto, arquitectura cliente-servidor, streaming, persistencia, integración
de proveedores heterogéneos, tool use, MCP, skills, ejecución local/remota,
multiusuario, seguridad, auditoría, tests de integración y preparación para
despliegue.

## 2. Capacidades de producto

### Chat y agentes

- Estudio de agentes con nombre, emoji, descripción, prompt de sistema, modelo,
  temperatura, máximo de tokens, esfuerzo de razonamiento, salida estructurada
  mediante JSON Schema, response healing, `tool_choice`, llamadas paralelas y
  vínculos a herramientas, MCP y skills.
- Chat en streaming con Markdown, resaltado de sintaxis y razonamiento plegable.
- Árbol de mensajes con edición y relanzamiento como variantes hermanas,
  paginación de variantes, reintento de respuestas y botón Stop con cancelación
  real.
- Persistencia del borrador y recuperación del turno cuando el navegador se
  desconecta; cambiar de conversación no detiene los streams de las demás.
- Adjuntos PDF (hasta 5 de 20 MB), con extracción de texto, OCR mediante Mistral
  o procesamiento nativo del proveedor.
- Menciones de agentes con `@`, activación de skills con `/`, contadores de
  tokens y coste, títulos automáticos y deep links a conversaciones.

### Model Council

Permite enviar una pregunta en paralelo a N modelos miembros, persistir sus
respuestas, comparar acuerdos, desacuerdos y hallazgos únicos mediante un
esquema estructurado, y pedir a un modelo sintetizador una respuesta final en
streaming. Los councils son configurables, consultables después y pueden usar
herramientas y MCP con aprobación humana.

### Proveedores de modelos

La aplicación no depende de un proveedor único y admite:

- OpenRouter, con acceso a más de 300 modelos, selección de proveedor inferior,
  fallbacks, OAuth PKCE o clave manual.
- DeepSeek directo, con validación y cálculo local de coste.
- ChatGPT/Codex mediante inicio de sesión por código de dispositivo, usando el
  plan de ChatGPT sin clave de API.
- Modelos locales de llama.cpp, con lanzamiento y supervisión de `llama-server`
  en el PC emparejado, presets de rendimiento, logs y descarga por inactividad.

La precedencia de configuración es mensaje → conversación → agente → valores
generales.

### Herramientas y extensibilidad

- Herramientas integradas de búsqueda y lectura web, hora actual, ejecución de
  comandos, operaciones de ficheros y envío/recepción de archivos.
- Ejecución en el PC local mediante agente emparejado o en sandbox E2B.
- Herramientas HTTP personalizadas GET/POST con esquema JSON, límites de tiempo y
  tamaño y prohibición de localhost.
- MCP por StreamableHTTP/SSE, stdio opcional o relay alojado en el PC
  emparejado; prueba de conexión, credenciales cifradas y aprobación humana por
  llamada.
- Skills estilo Claude a partir de `SKILL.md`, con validación previa, importación
  ZIP, recursos y scripts ejecutables `.py`, `.sh`, `.js`, `.ts`, `.rb` y `.ps1`.
- Compartición mediante instantáneas congeladas y revocables, exportación e
  importación JSON de agentes, herramientas y MCP, buscadores configurables y
  lectura web con fallback.

## 3. Arquitectura y stack

### Arquitectura de despliegue

La arquitectura preparada para producción separa **frontend estático en Vercel**
y **API en Railway**; durante el desarrollo puede ejecutarse todo localmente.
El backend es solo API y no sirve ficheros estáticos.

```text
Frontend React/Vite/Zustand  ← REST + SSE →  Backend Express/TypeScript
                                      ├── SQLite/better-sqlite3 en WAL
                                      ├── Proveedores LLM
                                      ├── Agente local por WebSocket
                                      └── E2B, MCP y servicios web externos
```

El frontend consume REST y streaming SSE mediante `fetch`; el WebSocket del
servidor se reserva para el agente local emparejado. El estado de stream se
mantiene por conversación y la base de datos es un único fichero SQLite con
migraciones idempotentes al arrancar.

### Frontend

React 18, TypeScript, Vite 6, Zustand 5, Framer Motion 11 y lucide-react;
react-markdown, remark-gfm, rehype-highlight y highlight.js para contenido; CSS
artesanal con el sistema visual Obsidian Atelier. La interfaz incluye layout
responsive con cajón lateral, barra inferior, sheets y compositor adaptado al
teclado móvil.

### Backend y tiempo real

Node.js ≥20.19, Express 4 y TypeScript ejecutado con `tsx` en desarrollo y
`tsc` en producción. Tiempo real mediante SSE para chat y WebSocket para el
agente local. Integraciones principales: cliente/SDK MCP, @openai/codex, E2B,
jsdom, Mozilla Readability, undici, js-yaml y adm-zip.

### Datos y operaciones

SQLite con better-sqlite3 en modo WAL y claves foráneas activadas; migraciones
idempotentes, autoreparación de borradores huérfanos y semillas por usuario.
El modelo cubre usuarios, ajustes, agentes, conversaciones, árbol de mensajes,
herramientas, MCP, skills, ejecuciones auditadas, agentes emparejados, ficheros,
comparticiones, councils y respuestas de councils.

## 4. Agente local

`local-agent/` es un subproyecto independiente que se ejecuta en el PC y
mantiene una conexión WebSocket persistente con el backend. Permite, con los
permisos de la cuenta local:

- ejecutar comandos reales y operar sobre ficheros;
- enviar y recibir ficheros;
- alojar servidores MCP relay y stdio locales;
- lanzar, detener y supervisar `llama-server`;
- aplicar detección de shell y control de seguridad de comandos.

El emparejamiento usa una URL del backend, workspace root, nombre de dispositivo
y código de 8 caracteres de un solo uso durante 10 minutos. El token se muestra
una sola vez y solo se conserva como hash en el servidor.

## 5. Seguridad y aislamiento

La documentación del proyecto contempla modo local sin login y modo
multiusuario con JWT HS256, bcrypt, cookie httpOnly y aislamiento por `user_id`.
Las capas de seguridad incluyen:

- cifrado AES-256-GCM en reposo para claves sensibles, con lecturas enmascaradas;
- rate limiting diferenciado para API, chat y Model Council;
- CORS mediante allowlist;
- aprobación MCP por llamada, fail-closed, con huella SHA-256 de argumentos y
  ventana de 60 segundos;
- `commandSafety` por niveles, con bloqueo de comandos peligrosos y
  confirmaciones humanas para acciones de riesgo;
- protección SSRF en el relay y allowlist de destinos `host:port`;
- validación de URLs web mediante zod;
- tokens de agente local aleatorios, mostrados una sola vez y almacenados como
  SHA-256;
- homes de Codex aislados por usuario y auditoría en `tool_executions`.

La documentación advierte expresamente que el control de comandos es un
cinturón de seguridad, no una sandbox, y que una configuración sin clave de
cifrado puede dejar settings sensibles en claro; estas limitaciones deben
conservarse en una entrevista técnica honesta.

## 6. Testing y calidad

El proyecto incluye una suite propia de integración con scripts TypeScript y
`node:assert`, ejecutada mediante `npm test` y complementada por cinco pruebas
MCP en `posttest`. La documentación contabiliza 36 scripts de integración y
ocho suites para el agente local.

La cobertura documentada incluye sincronización y seguridad de URLs,
proveedores, títulos, overrides de herramientas, presupuesto de tool-calls,
command safety y auditoría, E2B mediante dobles, relay y ficheros, parser y
resolución de skills, MCP cliente/seguridad/aislamiento/stdio/relay,
llama.cpp, edición de mensajes, supervivencia de turnos y compartición.

## 7. Preparación para despliegue

La configuración documentada automatiza un despliegue frontend en Vercel y API
en Railway: Nixpacks con Node 22, `npm ci`, compilación del servidor y health
check `/api/health`. Para persistencia se prevé un volumen Railway montado en
`/data` y `DATABASE_PATH=/data/agent-studio.db`; el frontend usa un build Vite y
la variable `VITE_API_URL`.

En desarrollo, `npm run dev` arranca backend y frontend juntos y espera a que el
health check del puerto 3001 responda antes de abrir Vite en el 5173.

## 8. Qué demuestra profesionalmente

Agent Studio puede posicionar a Pablo como **AI platform / agent infrastructure
builder** con experiencia práctica en:

- convertir capacidades de modelos en producto utilizable;
- diseñar contratos de streaming, persistencia y recuperación de estado;
- integrar múltiples proveedores sin acoplar el producto a uno solo;
- implementar tool use, MCP, skills y ejecución local con controles humanos;
- trabajar con seguridad aplicada, aislamiento multiusuario, auditoría y SSRF;
- construir una interfaz completa y responsive además del backend;
- probar integraciones y flujos críticos de forma reproducible;
- preparar un sistema para desarrollo local y despliegue cloud.

## 9. Formulaciones reutilizables

### Perfil técnico en español

> **Agent Studio** es una plataforma full-stack propia para crear y utilizar
> agentes de IA, con chat en streaming, herramientas, MCP, skills reutilizables,
> Model Council, proveedores múltiples y un agente local emparejado. Combina
> React/TypeScript/Vite/Zustand en frontend con Node/Express/TypeScript y
> SQLite/WAL en backend, además de seguridad multiusuario, cifrado, auditoría y
> una suite de integración propia.

### Bullet breve para CV

> **Agent Studio:** plataforma full-stack propia de agentes IA con streaming,
> tool use, MCP, skills, Model Council, proveedores OpenRouter/DeepSeek/Codex/
> llama.cpp y agente local; React/TypeScript/Vite + Node/Express/SQLite.

### English version

> **Agent Studio:** personal full-stack AI-agent workspace with streaming chat,
> tool use, MCP, reusable skills, Model Council, multi-provider LLM support and
> a paired local agent; built with React/TypeScript/Vite/Zustand,
> Node/Express/TypeScript and SQLite/WAL, with multi-user isolation, encryption,
> auditing and integration tests.

## 10. Uso en candidaturas

- Para roles de **AI agent engineer, AI platform, backend/full-stack o developer
  productivity**, incluirlo como uno de los proyectos principales y elegir dos o
  tres pruebas: arquitectura de proveedores/streaming, MCP/tools/skills,
  seguridad/auditoría o testing/despliegue.
- Para roles de **software engineering generalistas**, presentar el proyecto
  como evidencia de ownership end-to-end y no como una lista exhaustiva de cada
  función.
- Para roles ESG, política o comunicación, usarlo solo si la dimensión digital
  es relevante.
- No afirmar sin confirmación específica: usuarios activos, clientes,
  ingresos, disponibilidad pública, SLA/uptime, auditoría de seguridad externa,
  certificaciones de cumplimiento, escala de producción o despliegue real de
  todos los proveedores. Distinguir siempre entre capacidad implementada,
  configuración preparada para despliegue y uso efectivo en producción.
