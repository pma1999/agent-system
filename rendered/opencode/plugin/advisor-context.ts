import { appendFileSync } from "node:fs"
import type { Plugin } from "@opencode-ai/plugin"

/**
 * advisor-context — plugin dual V1/V2
 *
 * Inyecta automáticamente el transcript de la sesión del consultante en cada consulta
 * al agente `advisor` (V1: task tool con `subagent_type: "advisor"`; V2: subagent tool
 * con `agent: "advisor"`). Replica el Advisor tool de Claude Code: el advisor recibe
 * todo el contexto previo sin que el consultante tenga que resumirlo, y los bloques de
 * razonamiento interno se omiten.
 *
 * - V1 (opencode): export `server` — hook clásico `tool.execute.before`; lee los mensajes
 *   de la sesión vía `client.session.messages` (mensajes con `info.role` + `parts`).
 * - V2 (opencode2): export `setup` — `ctx.session.hook("context")` cachea los mensajes de
 *   cada sesión en cada dispatch al modelo; `ctx.tool.hook("execute.before")` inyecta el
 *   transcripto en el prompt del advisor. Fuente primaria: `ctx.session.context()`
 *   (transcripto completo V2, mensajes planos: `user.text`, `assistant.content[]`);
 *   fallback: la cache del hook de contexto. El tool de delegación en V2 es `subagent`
 *   y el nombre del agente viaja en `input.agent` (no `task`/`subagent_type`).
 *   La mutación/reasignación de `event.input` se propaga a la ejecución (es el mismo
 *   mecanismo que usa el adaptador V2 de oh-my-opencode-slim).
 *
 * Cualquier fallo se registra en el log del servidor: la consulta continúa con el brief
 * manual.
 */

const MAX_MESSAGES = 1000
const MAX_TOTAL_CHARS = 400_000
const MAX_PART_CHARS = 32_000
const MAX_TOOL_CHARS = 6_000
const MAX_CACHED_SESSIONS = 60

const LOG_PREFIX = "[advisor-context]"

// El servicio V2 no captura console.log de los plugins: se registra también en
// un fichero propio para que los fallos de inyección sean diagnosticables.
let logFile: string | undefined
try {
  logFile = `${process.env.XDG_DATA_HOME ?? `${process.env.HOME}/.local/share`}/opencode/log/advisor-context.log`
} catch {}

function log(...args: unknown[]): void {
  try {
    console.log(LOG_PREFIX, ...args)
  } catch {}
  if (!logFile) return
  try {
    const line = `${new Date().toISOString()} ${args.map((a) => (typeof a === "string" ? a : JSON.stringify(a))).join(" ")}\n`
    appendFileSync(logFile, line)
  } catch {}
}

function cut(text: string, max: number): { text: string; cut: boolean } {
  if (text.length <= max) return { text, cut: false }
  return { text: text.slice(0, max), cut: true }
}

function toolStateError(s: any): string | undefined {
  if (typeof s?.error === "string") return s.error
  if (s?.error && typeof s.error === "object") return s.error.message ?? JSON.stringify(s.error)
  return undefined
}

/** Salida textual de un tool part en cualquiera de las dos APIs:
 *  V1: state.output (string). V2: state.content[] ({type:"text",text}|{type:"file",...}). */
function toolOutputText(s: any): string | undefined {
  if (typeof s?.output === "string") return s.output
  if (Array.isArray(s?.content)) {
    const texts = s.content
      .filter((c: any) => c?.type === "text" && typeof c.text === "string")
      .map((c: any) => c.text)
    if (texts.length > 0) return texts.join("\n")
  }
  return undefined
}

function renderPart(part: any): string | null {
  if (!part || typeof part !== "object") return null
  switch (part.type) {
    case "text":
      return typeof part.text === "string" ? part.text : null
    case "tool": {
      const s = part.state ?? {}
      const name = part.tool ?? part.name ?? "?"
      const lines: string[] = [`[herramienta: ${name}]`]
      if (s.input) lines.push(`  input: ${cut(JSON.stringify(s.input), MAX_TOOL_CHARS).text}`)
      const out = toolOutputText(s)
      if (out) lines.push(`  output: ${cut(out, MAX_TOOL_CHARS).text}`)
      const err = toolStateError(s)
      if (err) lines.push(`  error: ${cut(err, MAX_TOOL_CHARS).text}`)
      if (s.status) lines.push(`  estado: ${s.status}`)
      return lines.join("\n")
    }
    case "subtask":
      return `[subagente lanzado: ${part.agent ?? "?"} — ${part.description ?? ""}]`
    default:
      return null // reasoning, file, image, step-*: omitidos
  }
}

/** Rol del mensaje en cualquiera de las dos APIs:
 *  V1 REST: msg.info.role; V1 hooks: msg.role;
 *  V2 REST (/session/{id}/context): msg.type ("user"|"assistant"|...);
 *  V2 context hook: msg.role. */
function messageRole(msg: any): string {
  const role = msg?.type ?? msg?.role ?? msg?.info?.role
  if (role === "user") return "Usuario"
  if (role === "assistant") return "Agente"
  if (role === "synthetic" || role === "system") return "Sistema"
  return String(role ?? "?")
}

function messageAgent(msg: any): string {
  const agent = msg?.agent ?? msg?.info?.agent
  return typeof agent === "string" && agent ? ` (${agent})` : ""
}

/** Partes renderizables del mensaje: V2 assistant usa content[], V1 usa parts[],
 *  y los mensajes planos V2 (user/synthetic/shell) traen el texto en msg.text. */
function messageParts(msg: any): any[] {
  if (Array.isArray(msg?.content) && msg.content.length > 0) return msg.content
  if (Array.isArray(msg?.parts)) return msg.parts
  if (typeof msg?.text === "string" && msg.text.trim() !== "") return [{ type: "text", text: msg.text }]
  return []
}

function buildTranscript(messages: any[] | undefined): string | null {
  if (!Array.isArray(messages) || messages.length === 0) return null

  const blocks: string[] = []
  let total = 0
  let truncated = false

  // Del más reciente al más antiguo: si hay que truncar, se pierde lo más viejo.
  for (const msg of [...messages].reverse()) {
    const linePrefix = `${messageRole(msg)}${messageAgent(msg)}: `
    for (const part of messageParts(msg)) {
      const rendered = renderPart(part)
      if (!rendered) continue
      const t = cut(rendered, MAX_PART_CHARS)
      if (t.cut) truncated = true
      const line = linePrefix + t.text
      total += line.length
      if (total > MAX_TOTAL_CHARS) {
        truncated = true
        break
      }
      blocks.push(line)
    }
    if (total > MAX_TOTAL_CHARS) break
  }

  if (blocks.length === 0) return null

  return [
    "──────────────────────────────────────────────",
    "CONTEXTO PREVIO COMPLETO (inyectado automáticamente)",
    "Transcript de la sesión del consultante, en orden cronológico. Los bloques de",
    "razonamiento interno se omitieron. No necesitas leer archivos para conocer lo",
    "ocurrido; lee artefactos citados solo si tu decisión depende de su contenido exacto.",
    truncated
      ? "AVISO: transcript truncado por tamaño — las interacciones más recientes están incluidas."
      : "",
    "──────────────────────────────────────────────",
    ...blocks.reverse(),
  ]
    .filter((l) => l !== "")
    .join("\n")
}

// ---------------------------------------------------------------------------
// V1 (opencode) — API clásica de plugins
// ---------------------------------------------------------------------------
async function server({ client }: { client: any }) {
  return {
    "tool.execute.before": async (input: any, output: any) => {
      try {
        if (input.tool !== "task") return
        const args = output?.args
        if (!args || typeof args !== "object") return
        if (args.subagent_type !== "advisor") return
        if (typeof args.prompt !== "string") return

        const res = await client.session.messages({
          path: { id: input.sessionID },
          query: { limit: MAX_MESSAGES },
        })
        const messages: any[] = Array.isArray(res?.data) ? res.data : []
        const body = buildTranscript(messages)
        if (body) {
          args.prompt = `${args.prompt}\n\n${body}`
          log(`transcripto inyectado (${body.length} chars, V1 client.session.messages) → advisor`)
        } else {
          log("V1: sin transcripto disponible; no se inyecta")
        }
      } catch (e) {
        log("V1: inyección fallida; la consulta continúa solo con el brief manual:", String(e))
      }
    },
  } satisfies Plugin
}

// ---------------------------------------------------------------------------
// V2 (opencode2) — API nativa de plugins
// ---------------------------------------------------------------------------
async function setup(ctx: any) {
  // En OpenCode V1 este `setup` tambien se invoca, pero las APIs de plugin de V2
  // no existen. Sin esta guarda, cada arranque escupia dos errores por stderr
  // que parecian una rotura del plugin cuando en realidad la inyeccion la hace
  // el hook V1 `tool.execute.before` de `server`, mas abajo.
  if (typeof ctx?.session?.hook !== "function" || typeof ctx?.tool?.hook !== "function") {
    log("APIs de plugin V2 ausentes: se usa la ruta V1 (server/tool.execute.before)")
    return
  }

  // Cachea los mensajes de cada sesión en cada dispatch al modelo.
  // La sesión que lanza el subagent tool ya pasó por aquí al menos una vez.
  const transcripts = new Map<string, any[]>()
  const sessionOrder: string[] = []

  try {
    await ctx.session.hook("context", (event: any) => {
      if (!event?.sessionID) return
      transcripts.set(event.sessionID, event.messages)
      if (!sessionOrder.includes(event.sessionID)) {
        sessionOrder.push(event.sessionID)
        while (sessionOrder.length > MAX_CACHED_SESSIONS) {
          const evicted = sessionOrder.shift()
          if (evicted) transcripts.delete(evicted)
        }
      }
    })
    log("hook session/context registrado")
  } catch (e) {
    log("session.hook(context) falló:", String(e))
  }

  try {
    await ctx.tool.hook("execute.before", async (event: any) => {
      try {
        const tool = String(event?.tool ?? "").toLowerCase()
        // V2 delega con `subagent`; se acepta `task` por compatibilidad.
        if (tool !== "subagent" && tool !== "task") return
        let args: any = event?.input
        if (!args || typeof args !== "object") return
        // V2: input.agent; v1-style: subagent_type / subagentType
        const target = args.agent ?? args.subagent_type ?? args.subagentType
        if (target !== "advisor") return
        if (typeof args.prompt !== "string") return

        let messages: any[] | undefined
        let source = "cache"
        try {
          if (typeof ctx.session?.context === "function") {
            const res = await ctx.session.context({ sessionID: event.sessionID })
            const arr = Array.isArray(res) ? res : (res?.data ?? res?.messages)
            if (Array.isArray(arr) && arr.length > 0) {
              messages = arr
              source = "session.context"
            }
          }
        } catch (e) {
          log("session.context() falló; uso la cache del hook de contexto:", String(e))
        }
        if (!messages || messages.length === 0) {
          messages = transcripts.get(event.sessionID)
        }

        const body = buildTranscript(messages)
        if (body) {
          const injected = `${args.prompt}\n\n${body}`
          args.prompt = injected // mutación in-place del input real
          event.input = { ...args, prompt: injected } // reasignación defensiva
          log(
            `transcripto inyectado (${body.length} chars, fuente ${source}) → advisor en sesión ${event.sessionID}`,
          )
        } else {
          log(`sin transcripto disponible (fuente ${source}); no se inyecta`)
        }
      } catch (e) {
        log("execute.before: inyección fallida; la consulta continúa solo con el brief manual:", String(e))
      }
    })
    log("hook tool/execute.before registrado")
  } catch (e) {
    log("tool.hook(execute.before) falló:", String(e))
  }
}

export default { id: "advisor-context", server, setup }

// Internals expuestos solo para tests.
export const __internals = { buildTranscript, renderPart, messageRole, messageParts }
