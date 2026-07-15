#!/usr/bin/env node
/**
 * Re-applies the local Codex runtime patch to the installed Codex plugin
 * (codex@openai-codex) after a plugin update wipes the cache copy.
 *
 * What the patch does: (1) adds `--agent <name>` to the companion `task`
 * command, resolving `$CODEX_HOME/agents/<name>.toml` and injecting its
 * `developer_instructions` natively as app-server `developerInstructions`;
 * and (2) adds the model-dependent `max` reasoning effort accepted by current
 * GPT-5.6-Sol runtimes. The agent injection requires codex-cli >= 0.142.4.
 *
 * Usage:
 *   node codex-plugin-agent-patch.mjs [--dir <plugin-version-dir>] [--dry-run]
 *
 * Exit codes: 0 = all core edits applied or already present; 1 = a core edit
 * failed (anchor not found — plugin code drifted; apply manually per the
 * memory note codex-plugin-agent-flag-patch).
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";

const argv = process.argv.slice(2);
const dryRun = argv.includes("--dry-run");
const dirFlag = argv.indexOf("--dir");
const explicitDir = dirFlag !== -1 ? argv[dirFlag + 1] : null;

function findPluginDir() {
  if (explicitDir) return path.resolve(explicitDir);
  const base = path.join(os.homedir(), ".claude", "plugins", "cache", "openai-codex", "codex");
  if (!fs.existsSync(base)) throw new Error(`Plugin cache not found: ${base}`);
  const versions = fs
    .readdirSync(base, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name);
  if (!versions.length) throw new Error(`No plugin versions under ${base}`);
  versions.sort((a, b) => {
    const pa = a.split(".").map(Number);
    const pb = b.split(".").map(Number);
    for (let i = 0; i < Math.max(pa.length, pb.length); i++) {
      const d = (pa[i] ?? 0) - (pb[i] ?? 0);
      if (d) return d;
    }
    return 0;
  });
  return path.join(base, versions[versions.length - 1]);
}

/** Try an exact replacement; retries with CRLF-normalized anchors. */
function applyEdit(src, find, replace) {
  if (src.includes(find)) return src.replace(find, replace);
  const crlfFind = find.replaceAll("\n", "\r\n");
  if (src.includes(crlfFind)) return src.replace(crlfFind, replace.replaceAll("\n", "\r\n"));
  return null;
}

const HELPERS = `function extractDeveloperInstructions(tomlText) {
  const match = tomlText.match(
    /(?:^|\\r?\\n)\\s*developer_instructions\\s*=\\s*(?:'''\\r?\\n?([\\s\\S]*?)'''|"""\\r?\\n?([\\s\\S]*?)"""|'([^'\\r\\n]*)'|"([^"\\r\\n]*)")/
  );
  if (!match) {
    return null;
  }
  const value = match[1] ?? match[2] ?? match[3] ?? match[4] ?? "";
  return value.trim() || null;
}

/**
 * Load the \`developer_instructions\` of a Codex custom agent defined in
 * \`$CODEX_HOME/agents/<name>.toml\`, for injection as thread-level
 * \`developerInstructions\` via the app server.
 */
export function loadAgentDeveloperInstructions(agentName) {
  const name = String(agentName ?? "").trim();
  if (!/^[A-Za-z0-9][A-Za-z0-9._-]*$/.test(name)) {
    throw new Error(\`Invalid Codex agent name "\${agentName}".\`);
  }
  const codexHome = path.resolve(process.env.CODEX_HOME || path.join(os.homedir(), ".codex"));
  const agentPath = path.join(codexHome, "agents", \`\${name}.toml\`);
  if (!fs.existsSync(agentPath)) {
    throw new Error(\`Unknown Codex agent "\${name}": expected \${agentPath}.\`);
  }
  const instructions = extractDeveloperInstructions(fs.readFileSync(agentPath, "utf8"));
  if (!instructions) {
    throw new Error(\`Codex agent file \${agentPath} has no developer_instructions.\`);
  }
  return instructions;
}

`;

const EDITS = [
  // ---------- scripts/lib/codex.mjs ----------
  {
    file: "scripts/lib/codex.mjs",
    id: "lib: helper loadAgentDeveloperInstructions",
    core: true,
    applied: (s) => s.includes("export function loadAgentDeveloperInstructions"),
    find: "/** @returns {UserInput[]} */",
    replace: HELPERS + "/** @returns {UserInput[]} */"
  },
  {
    file: "scripts/lib/codex.mjs",
    id: "lib: buildThreadParams developerInstructions",
    core: true,
    applied: (s) => /buildThreadParams[\s\S]{0,600}?developerInstructions/.test(s),
    find: `function buildThreadParams(cwd, options = {}) {
  return {
    cwd,
    model: options.model ?? null,
    approvalPolicy: options.approvalPolicy ?? "never",
    sandbox: options.sandbox ?? "read-only",
    serviceName: SERVICE_NAME,
    ephemeral: options.ephemeral ?? true
  };
}`,
    replace: `function buildThreadParams(cwd, options = {}) {
  const params = {
    cwd,
    model: options.model ?? null,
    approvalPolicy: options.approvalPolicy ?? "never",
    sandbox: options.sandbox ?? "read-only",
    serviceName: SERVICE_NAME,
    ephemeral: options.ephemeral ?? true
  };
  if (options.developerInstructions) {
    params.developerInstructions = options.developerInstructions;
  }
  return params;
}`
  },
  {
    file: "scripts/lib/codex.mjs",
    id: "lib: buildResumeParams developerInstructions",
    core: true,
    applied: (s) => /buildResumeParams[\s\S]{0,600}?developerInstructions/.test(s),
    find: `function buildResumeParams(threadId, cwd, options = {}) {
  return {
    threadId,
    cwd,
    model: options.model ?? null,
    approvalPolicy: options.approvalPolicy ?? "never",
    sandbox: options.sandbox ?? "read-only"
  };
}`,
    replace: `function buildResumeParams(threadId, cwd, options = {}) {
  const params = {
    threadId,
    cwd,
    model: options.model ?? null,
    approvalPolicy: options.approvalPolicy ?? "never",
    sandbox: options.sandbox ?? "read-only"
  };
  if (options.developerInstructions) {
    params.developerInstructions = options.developerInstructions;
  }
  return params;
}`
  },
  {
    file: "scripts/lib/codex.mjs",
    id: "lib: runAppServerTurn resume branch",
    core: true,
    applied: (s) =>
      /resumeThread\(client, options\.resumeThreadId, cwd, \{[\s\S]{0,300}?developerInstructions/.test(s),
    find: `      const response = await resumeThread(client, options.resumeThreadId, cwd, {
        model: options.model,
        sandbox: options.sandbox,
        ephemeral: false
      });`,
    replace: `      const response = await resumeThread(client, options.resumeThreadId, cwd, {
        model: options.model,
        sandbox: options.sandbox,
        developerInstructions: options.developerInstructions ?? null,
        ephemeral: false
      });`
  },
  {
    file: "scripts/lib/codex.mjs",
    id: "lib: runAppServerTurn start branch",
    core: true,
    applied: (s) => /startThread\(client, cwd, \{[\s\S]{0,400}?developerInstructions/.test(s),
    find: `      const response = await startThread(client, cwd, {
        model: options.model,
        sandbox: options.sandbox,
        ephemeral: options.persistThread ? false : true,`,
    replace: `      const response = await startThread(client, cwd, {
        model: options.model,
        sandbox: options.sandbox,
        developerInstructions: options.developerInstructions ?? null,
        ephemeral: options.persistThread ? false : true,`
  },
  // ---------- scripts/codex-companion.mjs ----------
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: import loader",
    core: true,
    applied: (s) => s.includes("loadAgentDeveloperInstructions"),
    find: `    interruptAppServerTurn,`,
    replace: `    interruptAppServerTurn,
    loadAgentDeveloperInstructions,`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: max reasoning effort validation",
    core: true,
    applied: (s) => /VALID_REASONING_EFFORTS[^\n]*["']max["']/.test(s),
    find: `const VALID_REASONING_EFFORTS = new Set(["none", "minimal", "low", "medium", "high", "xhigh"]);`,
    replace: `const VALID_REASONING_EFFORTS = new Set(["none", "minimal", "low", "medium", "high", "xhigh", "max"]);`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: max reasoning effort error",
    core: true,
    applied: (s) => s.includes("Use one of: none, minimal, low, medium, high, xhigh, max."),
    find: `Use one of: none, minimal, low, medium, high, xhigh.`,
    replace: `Use one of: none, minimal, low, medium, high, xhigh, max.`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: usage string",
    core: false,
    applied: (s) => s.includes("[--agent <codex-agent-name>]"),
    find: `[--effort <none|minimal|low|medium|high|xhigh>] [prompt]"`,
    replace: `[--effort <none|minimal|low|medium|high|xhigh>] [--agent <codex-agent-name>] [prompt]"`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: max reasoning effort usage",
    core: false,
    applied: (s) => s.includes("none|minimal|low|medium|high|xhigh|max"),
    find: `none|minimal|low|medium|high|xhigh`,
    replace: `none|minimal|low|medium|high|xhigh|max`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: buildTaskRequest fields",
    core: true,
    applied: (s) => /function buildTaskRequest\([\s\S]{0,400}?developerInstructions/.test(s),
    find: `function buildTaskRequest({ cwd, model, effort, prompt, write, resumeLast, jobId }) {
  return {
    cwd,
    model,
    effort,
    prompt,
    write,
    resumeLast,
    jobId
  };
}`,
    replace: `function buildTaskRequest({ cwd, model, effort, prompt, write, resumeLast, jobId, agent, developerInstructions }) {
  return {
    cwd,
    model,
    effort,
    prompt,
    write,
    resumeLast,
    jobId,
    agent: agent ?? null,
    developerInstructions: developerInstructions ?? null
  };
}`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: executeTaskRun injection",
    core: true,
    applied: (s) => /executeTaskRun[\s\S]{0,1500}?request\.developerInstructions/.test(s),
    find: `  const result = await runAppServerTurn(workspaceRoot, {
    resumeThreadId,
    prompt: request.prompt,
    defaultPrompt: resumeThreadId ? DEFAULT_CONTINUE_PROMPT : "",
    model: request.model,
    effort: request.effort,
    sandbox: request.write ? "workspace-write" : "read-only",
    onProgress: request.onProgress,`,
    replace: `  const developerInstructions =
    request.developerInstructions ?? (request.agent ? loadAgentDeveloperInstructions(request.agent) : null);

  const result = await runAppServerTurn(workspaceRoot, {
    resumeThreadId,
    prompt: request.prompt,
    defaultPrompt: resumeThreadId ? DEFAULT_CONTINUE_PROMPT : "",
    model: request.model,
    effort: request.effort,
    sandbox: request.write ? "workspace-write" : "read-only",
    developerInstructions,
    onProgress: request.onProgress,`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: handleTask --agent option",
    core: true,
    applied: (s) => s.includes(`"prompt-file", "agent"`),
    find: `    valueOptions: ["model", "effort", "cwd", "prompt-file"],
    booleanOptions: ["json", "write", "resume-last", "resume", "fresh", "background"],`,
    replace: `    valueOptions: ["model", "effort", "cwd", "prompt-file", "agent"],
    booleanOptions: ["json", "write", "resume-last", "resume", "fresh", "background"],`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: handleTask resolve agent",
    core: true,
    applied: (s) => s.includes("const agent = options.agent"),
    find: `  const effort = normalizeReasoningEffort(options.effort);
  const prompt = readTaskPrompt(cwd, options, positionals);`,
    replace: `  const effort = normalizeReasoningEffort(options.effort);
  const agent = options.agent ? String(options.agent).trim() : null;
  const developerInstructions = agent ? loadAgentDeveloperInstructions(agent) : null;
  const prompt = readTaskPrompt(cwd, options, positionals);`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: background request fields",
    core: true,
    applied: (s) => /buildTaskRequest\(\{[\s\S]{0,300}?jobId: job\.id,\s*agent,/.test(s),
    find: `      resumeLast,
      jobId: job.id
    });
    const { payload } = enqueueBackgroundTask(cwd, job, request);`,
    replace: `      resumeLast,
      jobId: job.id,
      agent,
      developerInstructions
    });
    const { payload } = enqueueBackgroundTask(cwd, job, request);`
  },
  {
    file: "scripts/codex-companion.mjs",
    id: "companion: foreground call fields",
    core: true,
    applied: (s) => /executeTaskRun\(\{[\s\S]{0,300}?jobId: job\.id,\s*agent,/.test(s),
    find: `        resumeLast,
        jobId: job.id,
        onProgress: progress
      }),`,
    replace: `        resumeLast,
        jobId: job.id,
        agent,
        developerInstructions,
        onProgress: progress
      }),`
  },
  // ---------- docs (non-core: failures are warnings) ----------
  {
    file: "agents/codex-rescue.md",
    id: "docs: rescue agent --agent rule",
    core: false,
    applied: (s) => s.includes("--agent"),
    find: `- If the user asks for a concrete model name such as \`gpt-5.4-mini\`, pass it through with \`--model\`.
- Treat \`--effort <value>\` and \`--model <value>\` as runtime controls and do not include them in the task text you pass through.`,
    replace: `- If the user asks for a concrete model name such as \`gpt-5.4-mini\`, pass it through with \`--model\`.
- If the forwarded request includes \`--agent <name>\`, pass it through to \`task\` unchanged. It selects a Codex custom agent role from \`~/.codex/agents/<name>.toml\` that the runtime injects as developer instructions.
- Treat \`--effort <value>\`, \`--model <value>\`, and \`--agent <value>\` as runtime controls and do not include them in the task text you pass through.`
  },
  {
    file: "agents/codex-rescue.md",
    id: "docs: rescue agent max effort",
    core: false,
    applied: (s) => s.includes("`max` is model-dependent"),
    find: `- Leave \`--effort\` unset unless the user explicitly requests a specific reasoning effort.`,
    replace: `- Leave \`--effort\` unset unless the user explicitly requests a specific reasoning effort.
- Pass explicit supported effort values through unchanged; \`max\` is model-dependent and is supported by the current GPT-5.6-Sol runtime.`
  },
  {
    file: "agents/codex-rescue.md",
    id: "docs: rescue agent stay-alive protocol",
    core: false,
    applied: (s) => s.includes("status <job-id> --wait --timeout-ms 540000"),
    find: "- Use exactly one `Bash` call to invoke `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" task ...`.\n- If the user did not explicitly choose `--background` or `--wait`, prefer foreground for a small, clearly bounded rescue request.\n- If the user did not explicitly choose `--background` or `--wait` and the task looks complicated, open-ended, multi-step, or likely to keep Codex running for a long time, prefer background execution.",
    replace:
      "- Codex runs are slow (minutes to half an hour or more) and you must stay alive until Codex finishes: never end your turn while the Codex job is still running, and never launch it with `run_in_background: true` and then stop to \"wait\" — a finished subagent cannot receive completion notifications, so the result would be lost.\n- Follow this launch protocol, using only foreground Bash calls:\n  1. Launch: one `Bash` call to `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" task --background ...` with the forwarded task. It returns immediately with a job id (\"started in the background as <job-id>\"); the companion runs Codex in a detached worker that does not depend on this subagent.\n  2. Wait loop: `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" status <job-id> --wait --timeout-ms 540000`, with the Bash `timeout` parameter set to 600000. This call blocks until the job ends or the wait window expires. If the report still shows queued/running, run the same call again. Repeat as many times as needed — do not give up and do not end your turn between iterations.\n  3. Result: once the job reaches a terminal state, run `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" result <job-id>` and return its stdout."
  },
  {
    file: "agents/codex-rescue.md",
    id: "docs: rescue agent sanctioned status/result",
    core: false,
    applied: (s) => s.includes("the only sanctioned extra calls"),
    find: "- Do not inspect the repository, read files, grep, monitor progress, poll status, fetch results, cancel jobs, summarize output, or do any follow-up work of your own.\n- Do not call `review`, `adversarial-review`, `status`, `result`, or `cancel`. This subagent only forwards to `task`.",
    replace:
      "- Do not inspect the repository, read files, grep, cancel jobs, summarize output, or do any follow-up work of your own. The `status <job-id> --wait` loop and the final `result <job-id>` call for the job you launched are the only sanctioned extra calls.\n- Do not call `review`, `adversarial-review`, or `cancel`, and do not use `status` or `result` for any job other than the one you launched."
  },
  {
    file: "agents/codex-rescue.md",
    id: "docs: rescue agent return result stdout",
    core: false,
    applied: (s) => s.includes("final `result <job-id>` command exactly as-is"),
    find: "- Return the stdout of the `codex-companion` command exactly as-is.",
    replace:
      "- Return the stdout of the final `result <job-id>` command exactly as-is (if the launch failed before a job id existed, return the launch command's stdout instead)."
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill stay-alive protocol",
    core: false,
    applied: (s) => s.includes("Waiting protocol"),
    find: "- The rescue subagent is a forwarder, not an orchestrator. Its only job is to invoke `task` once and return that stdout unchanged.\n- Prefer the helper over hand-rolled `git`, direct Codex CLI strings, or any other Bash activity.\n- Do not call `setup`, `review`, `adversarial-review`, `status`, `result`, or `cancel` from `codex:codex-rescue`.",
    replace:
      "- The rescue subagent is a forwarder, not an orchestrator. Its job is to launch one `task`, stay alive until it finishes, and return the result unchanged.\n- Codex runs are slow (minutes to half an hour or more) and the subagent must not end its turn while the job runs — a finished subagent cannot receive completion notifications. Never use `run_in_background: true` for the companion call.\n- Waiting protocol (all foreground Bash calls): launch with `task --background ...` (returns a job id; the companion runs Codex in a detached worker), then loop `status <job-id> --wait --timeout-ms 540000` (Bash `timeout` 600000) until the job leaves queued/running, then fetch `result <job-id>` and return that stdout unchanged.\n- Prefer the helper over hand-rolled `git`, direct Codex CLI strings, or any other Bash activity.\n- Do not call `setup`, `review`, `adversarial-review`, or `cancel` from `codex:codex-rescue`; use `status`/`result` only for the job this rescue launched."
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill one launch per handoff",
    core: false,
    applied: (s) => s.includes("one `task` launch per rescue handoff"),
    find: "- Use exactly one `task` invocation per rescue handoff.",
    replace:
      "- Use exactly one `task` launch per rescue handoff (plus the sanctioned `status --wait` loop and final `result` for that job)."
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill strip-flags rule",
    core: false,
    applied: (s) => s.includes("the protocol's own `task --background`"),
    find: "- If the forwarded request includes `--background` or `--wait`, treat that as Claude-side execution control only. Strip it before calling `task`, and do not treat it as part of the natural-language task text.",
    replace:
      "- If the forwarded request includes `--background` or `--wait`, treat that as Claude-side execution control only. Strip it from the task text; the launch always uses the protocol's own `task --background` regardless."
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill return result stdout",
    core: false,
    applied: (s) => s.includes("beyond the waiting protocol"),
    find: "- Do not inspect the repository, read files, grep, monitor progress, poll status, fetch results, cancel jobs, summarize output, or do any follow-up work of your own.\n- Return the stdout of the `task` command exactly as-is.",
    replace:
      "- Do not inspect the repository, read files, grep, cancel jobs, summarize output, or do any follow-up work of your own beyond the waiting protocol.\n- Return the stdout of the final `result <job-id>` command exactly as-is."
  },
  {
    file: "commands/rescue.md",
    id: "docs: rescue command stay-alive forwarder",
    core: false,
    applied: (s) => s.includes("stays alive until Codex finishes"),
    find: "- The subagent is a thin forwarder only. It should use one `Bash` call to invoke `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" task ...` and return that command's stdout as-is.",
    replace:
      "- The subagent is a thin forwarder that stays alive until Codex finishes: it launches `node \"${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs\" task --background ...`, blocks on `status <job-id> --wait` foreground calls until the job ends, then returns the `result <job-id>` stdout as-is. That internal waiting is expected — do not treat it as extra work."
  },
  {
    file: "commands/rescue.md",
    id: "docs: rescue command do-not scope",
    core: false,
    applied: (s) => s.includes("launch/wait/result protocol"),
    find: "- Do not ask the subagent to inspect files, monitor progress, poll `/codex:status`, fetch `/codex:result`, call `/codex:cancel`, summarize output, or do follow-up work of its own.",
    replace:
      "- Do not ask the subagent to inspect files, call `/codex:cancel`, summarize output, or do follow-up work of its own beyond its launch/wait/result protocol."
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill --agent rule",
    core: false,
    applied: (s) => s.includes("--agent"),
    find: `- If the forwarded request includes \`--effort\`, pass it through to \`task\`.`,
    replace: `- If the forwarded request includes \`--effort\`, pass it through to \`task\`.
- If the forwarded request includes \`--agent <name>\`, pass it through to \`task\` unchanged; the runtime resolves \`~/.codex/agents/<name>.toml\` and injects its developer_instructions at thread start. Do not include it in the task text.`
  },
  {
    file: "skills/codex-cli-runtime/SKILL.md",
    id: "docs: runtime skill max effort",
    core: false,
    applied: (s) => s.includes("none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`"),
    find: `- \`--effort\`: accepted values are \`none\`, \`minimal\`, \`low\`, \`medium\`, \`high\`, \`xhigh\`.`,
    replace: `- \`--effort\`: accepted values are \`none\`, \`minimal\`, \`low\`, \`medium\`, \`high\`, \`xhigh\`, \`max\`; the selected model must support the requested level.`
  },
  {
    file: "commands/rescue.md",
    id: "docs: rescue command hint",
    core: false,
    applied: (s) => s.includes("[--agent <codex-agent-name>]"),
    find: `[--effort <none|minimal|low|medium|high|xhigh>] [what Codex should investigate, solve, or continue]"`,
    replace: `[--effort <none|minimal|low|medium|high|xhigh>] [--agent <codex-agent-name>] [what Codex should investigate, solve, or continue]"`
  },
  {
    file: "commands/rescue.md",
    id: "docs: rescue command max effort hint",
    core: false,
    applied: (s) => s.includes("none|minimal|low|medium|high|xhigh|max"),
    find: `none|minimal|low|medium|high|xhigh`,
    replace: `none|minimal|low|medium|high|xhigh|max`
  },
  {
    file: "commands/rescue.md",
    id: "docs: rescue command flags rule",
    core: false,
    applied: (s) => s.includes("`--agent` are runtime-selection flags") || s.includes("and `--agent` are runtime-selection"),
    find: `- \`--model\` and \`--effort\` are runtime-selection flags. Preserve them for the forwarded \`task\` call, but do not treat them as part of the natural-language task text.`,
    replace: `- \`--model\`, \`--effort\`, and \`--agent\` are runtime-selection flags. Preserve them for the forwarded \`task\` call, but do not treat them as part of the natural-language task text. \`--agent <name>\` selects a Codex custom agent role from \`~/.codex/agents/<name>.toml\`.`
  }
];

// ---------- run ----------
const pluginDir = findPluginDir();
console.log(`Plugin dir: ${pluginDir}${dryRun ? "  (dry run)" : ""}`);

const contents = new Map();
const results = [];
let coreFailed = false;

for (const edit of EDITS) {
  const filePath = path.join(pluginDir, edit.file);
  if (!fs.existsSync(filePath)) {
    results.push([edit.core ? "FAILED " : "WARNING", edit.id, "file missing"]);
    if (edit.core) coreFailed = true;
    continue;
  }
  const src = contents.get(filePath) ?? fs.readFileSync(filePath, "utf8");
  if (edit.applied(src)) {
    results.push(["already", edit.id, ""]);
    contents.set(filePath, src);
    continue;
  }
  const next = applyEdit(src, edit.find, edit.replace);
  if (next === null) {
    results.push([edit.core ? "FAILED " : "WARNING", edit.id, "anchor not found (code drifted)"]);
    if (edit.core) coreFailed = true;
    contents.set(filePath, src);
    continue;
  }
  results.push(["applied", edit.id, ""]);
  contents.set(filePath, next);
}

if (!dryRun) {
  for (const [filePath, text] of contents) {
    fs.writeFileSync(filePath, text);
  }
}

for (const [status, id, note] of results) {
  console.log(`  [${status}] ${id}${note ? ` — ${note}` : ""}`);
}

if (coreFailed) {
  console.error(
    "\nSome CORE edits failed: the plugin code has drifted. Apply manually per the memory note 'codex-plugin-agent-flag-patch', or update this patcher."
  );
  process.exit(1);
}

// ---------- verify ----------
if (!dryRun) {
  const companion = path.join(pluginDir, "scripts", "codex-companion.mjs");
  const lib = path.join(pluginDir, "scripts", "lib", "codex.mjs");
  try {
    execFileSync(process.execPath, ["--check", companion], { stdio: "pipe" });
    execFileSync(process.execPath, ["--check", lib], { stdio: "pipe" });
    console.log("Syntax check: OK");
  } catch (err) {
    console.error(`Syntax check FAILED:\n${err.stderr?.toString() ?? err.message}`);
    process.exit(1);
  }
  try {
    const mod = await import(pathToFileURL(lib).href);
    const text = mod.loadAgentDeveloperInstructions("task-implementer-bdd");
    console.log(`Loader check: OK (${text.length} chars of developer_instructions)`);
  } catch (err) {
    console.error(`Loader check FAILED: ${err.message}`);
    process.exit(1);
  }
  const companionText = fs.readFileSync(companion, "utf8");
  if (!/VALID_REASONING_EFFORTS[^\n]*["']max["']/.test(companionText)) {
    console.error("Effort check FAILED: max is not accepted by VALID_REASONING_EFFORTS.");
    process.exit(1);
  }
  console.log("Effort check: OK (max accepted; model compatibility remains runtime-validated)");
  console.log(
    "\nDone. Optional live checks:\n" +
      `  node "${path.join(pluginDir, "scripts", "codex-companion.mjs")}" task --agent task-implementer-bdd --effort low "Do not read files or run commands. State your allowed report Status values on one line."\n` +
      "  -> must echo: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT | PACK_GAP\n" +
      `  node "${path.join(pluginDir, "scripts", "codex-companion.mjs")}" task --agent implementation-planner --model gpt-5.6-sol --effort max "Read-only handshake: do not read or write files. Reply exactly PLANNER_MAX_READY."\n` +
      "  -> must reach the runtime and echo: PLANNER_MAX_READY"
  );
}
