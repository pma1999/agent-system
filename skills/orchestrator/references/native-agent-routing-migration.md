# Native Custom-Agent Routing Migration

## Purpose

Use this reference when a new Codex release may support the orchestrator's complete routing contract natively. Verify the release first, then simplify the local system in one controlled change.

The target native workflow is:

1. Select the specialist role for the work unit.
2. Select and explicitly dispatch the task-specific model and reasoning effort.
3. Start the specialist through native multi-agent tools with a context-free or partial fork.
4. Record the canonical agent target in `progress.md`.
5. Resume that same target for review remediation and re-review.

`implementation-planner` remains fixed at `gpt-5.6-sol` / `xhigh`. Every other new dispatch uses the profile selected for its actual task.

## System Snapshot

This snapshot explains why the compatibility backend exists. Treat it as historical evidence; use the verification procedure below to establish the behavior of the installed release.

As of Codex CLI 0.144.3 on 2026-07-13:

- Default GPT-5.6 Sol / Multi-Agent V2 exposed `task_name`, `message`, and `fork_turns`, while hiding role and routing inputs.
- Configuring `features.multi_agent_v2.hide_spawn_agent_metadata = false` with `tool_namespace = "agents"` exposed `agent_type`, `model`, and `reasoning_effort` on the tested installation.
- A built-in `worker` respected an explicit Luna/low dispatch and retained that resolved profile across `followup_task`.
- A custom role loaded its developer instructions but reapplied role configuration after the explicit spawn override.
- A custom role with Terra/high in its TOML ran Terra/high after a conflicting Luna/low dispatch.
- A custom role without model fields reverted to the Sol parent instead of retaining the explicit Luna model.
- A resumed `codex exec` session applied the requested role instructions, model, and effort exactly and preserved task context across resume.

The local compatibility path therefore consists of:

- `native-collab` when the native surface can apply the complete selected route;
- `skills/orchestrator/scripts/invoke-specialist.ps1` plus `invoke-specialist-worker.ps1` when a resumable explicit route is needed outside native collaboration; on Windows the dispatcher bypasses the 8191-character `codex.cmd`/`cmd.exe` boundary by invoking Codex's official JavaScript launcher directly with Node, then validates the real 32767-character `CreateProcess` ceiling before launch;
- a persistent background job under `.orchestrator/jobs/<job-id>/`; on Windows a hidden Scheduled Task owns the process with `ExecutionTimeLimit = 0`, while the single-call wrapper in `codex-exec-passive-wait.md` keeps the parent suspended until passive `-Wait` wakes from the durable result-file event, without polling or intermediate model turns;
- backend and owner fields in `progress.md` so remediation returns to the original implementer and reviewer.

Relevant upstream state at the snapshot date:

- [Issue #31814](https://github.com/openai/codex/issues/31814) tracks Sol/V2 hiding subagent routing controls.
- [PR #32749](https://github.com/openai/codex/pull/32749) is merged into `main` and separates model/reasoning exposure from other hidden spawn metadata. It was not yet present in the tested 0.144.3 release.
- [Issue #32831](https://github.com/openai/codex/issues/32831) tracks explicit model/reasoning being discarded when a custom role leaves those fields unset.
- [PR #22169](https://github.com/openai/codex/pull/22169) records the existing locked-role precedence: values explicitly defined by a role take precedence over conflicting spawn values.

## Native Readiness Contract

Adopt the fully native path when one installed release satisfies all of these conditions in a fresh top-level Sol session:

- The callable spawn schema supports the configured custom role plus explicit `model` and `reasoning_effort`.
- A context-free custom-role spawn runs the exact requested model and reasoning effort.
- The custom role's developer instructions and required permissions are active in the child.
- A role that leaves model or reasoning unset preserves the corresponding explicit dispatch value.
- A role that intentionally fixes a value follows the current documented locking or override contract.
- `followup_task` reactivates the same canonical target and retains its resolved child configuration and task context.
- Planner dispatch resolves to Sol/xhigh.
- Full-history and partial/context-free fork behavior matches current official documentation.
- The behavior is supported by the released runtime rather than only by unreleased `main` source.

Treat model-visible arguments, child rollout metadata, and observable execution as separate evidence. Use rollout/session metadata or request-level evidence where available; use agent self-report only as supplementary evidence.

## Release Verification Procedure

### 1. Establish the current supported contract

Before editing local files:

1. Record `codex --version` and the Codex Desktop build when applicable.
2. Read the current official [subagent configuration documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), release notes, and the linked upstream issues/PRs.
3. Inspect the model-visible native spawn schema in a fresh GPT-5.6 Sol session.
4. Record the currently supported V2 namespace and feature configuration.
5. Compare the released source or tagged source with the installed behavior when the result is ambiguous.

This establishes which configuration keys are still part of the supported native setup. Keep any feature settings that the current release requires for custom-role selection, and remove compatibility settings that the release has made unnecessary.

### 2. Run a bounded native smoke test

Create or reuse a temporary custom role whose instructions produce a deterministic response and whose TOML leaves `model` and `model_reasoning_effort` unset. From a Sol parent, start it with:

- `agent_type`: the temporary custom role;
- `model`: `gpt-5.6-luna`;
- `reasoning_effort`: `low`;
- `fork_turns`: `none`;
- a prompt requiring one exact short response.

Verify:

1. The spawn call includes every requested routing value.
2. The child has the custom role and instructions.
3. The child actually runs Luna/low.
4. `followup_task` on the returned target triggers a second turn in the same child.
5. The second turn retains Luna/low and the first-turn context.

Run two controls:

- a built-in `worker` with the same Luna/low pair;
- `implementation-planner` at Sol/xhigh.

If the documented native contract supports partial locks, also verify a role that fixes only model and a role that fixes only reasoning. Confirm each field independently.

Delete temporary role configuration and test sessions after collecting the result.

### 3. Record the migration decision

Write a short migration note containing:

- installed version and platform;
- effective V2 configuration;
- exposed spawn fields;
- initial and follow-up child model/effort evidence;
- custom instructions evidence;
- pass/fail for every readiness condition;
- links to the supporting release or upstream fix.

Proceed with simplification when every readiness condition passes. Continue using the dual backend when a released runtime still needs compatibility handling.

## Native Migration Changes

Apply these changes together after the readiness gate passes.

### 1. Make routing values dispatch-owned

Keep these values in `agents/implementation-planner.toml`:

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
```

Remove `model` and `model_reasoning_effort` from the other specialist TOMLs when the accepted native contract treats role-defined values as locks. Their developer instructions, descriptions, nicknames, sandbox, permissions, and tool configuration remain role-owned.

The affected current profiles are:

- `codebase-explorer`
- `integration-researcher`
- `root-cause-debugger`
- `task-implementer-bdd`
- `implementation-reviewer`

Every new dispatch then supplies the model and reasoning effort selected by the planner or orchestrator. This makes the recorded routing matrix the authoritative selection and keeps role files focused on specialist behavior.

If the released native contract introduces an explicit role-level fallback or override policy, configure that documented policy instead and preserve the same outcome: planner fixed, all other work units explicitly routed per task.

### 2. Use native collaboration as the single dispatch path

Update `skills/orchestrator/SKILL.md` so a new specialist is started with the native spawn tool using:

- the selected custom role;
- the selected model;
- the selected reasoning effort;
- `fork_turns: "none"` by default for artifact handoffs;
- a path-based prompt naming the brief/report artifacts.

Store `native-collab:<canonical-target>` as the owner in `progress.md`. Use:

- `followup_task` to reactivate an idle owner for remediation or re-review;
- `send_message` for supplemental information to an already active owner;
- `list_agents` to recover or verify a retained canonical target;
- `interrupt_agent` only for an intentional cancellation;
- a new spawn when the original owner is unavailable or changed scope requires a newly routed work unit.

A follow-up continues the existing work unit and therefore retains the child's resolved profile. Select a fresh model/effort pair whenever a new work unit is spawned.

### 3. Retire compatibility artifacts

After native dispatch and follow-up tests pass from the updated skill:

1. This is an explicit backend-retirement operation, so use `invoke-specialist.ps1 -List` to inventory all compatibility jobs, map them to their owning workflow ledgers, let every active job reach completion through `-Wait`, and run `-Cleanup` for each terminal job so its Scheduled Task and durable state are removed. Ordinary workflow closure must use only that workflow's recorded job IDs; global `-List` is not a normal cleanup scope.
2. Delete `skills/orchestrator/scripts/invoke-specialist.ps1` and `invoke-specialist-worker.ps1`.
3. Remove `codex-exec` selection, invocation, resume, and error-handling branches from `skills/orchestrator/SKILL.md`.
4. Simplify plan/report/review templates and `progress.md` guidance to store the canonical native target and actual dispatched profile.
5. Remove the `External Dispatch` instructions that exist only for `codex exec` from specialist TOMLs.
6. Update `AGENTS.md` routing guidance to describe the released native contract and its required configuration.
7. Set `config.toml` to the smallest currently documented V2 configuration that exposes custom-role selection and explicit routing.
8. Remove this migration reference once the native-only instructions are self-contained and verified.

Use one focused change so the skill, profiles, script removal, configuration, and templates cannot drift into mixed backend semantics.

## Post-Migration Verification

Validate the native-only system with one short end-to-end workflow:

1. Dispatch `implementation-planner` and verify Sol/xhigh.
2. Dispatch one model-free custom specialist using a non-default approved pair.
3. Verify its role instructions, actual model/effort, artifact output, and canonical target.
4. Dispatch a reviewer using an independently selected pair.
5. Send one required-change follow-up to the original implementer.
6. Send the re-review follow-up to the original reviewer.
7. Verify both continuations reuse their original targets and artifacts.
8. Confirm `progress.md` contains the planned and actual profiles plus canonical owners.

Run the orchestrator skill validator and search for stale compatibility references:

```powershell
python "$env:CODEX_HOME\skills\.system\skill-creator\scripts\quick_validate.py" "$env:CODEX_HOME\skills\orchestrator"
rg -n "codex-exec|invoke-specialist|SessionId|External Dispatch|\.orchestrator/jobs" `
  "$env:CODEX_HOME\skills\orchestrator" `
  "$env:CODEX_HOME\agents" `
  "$env:CODEX_HOME\AGENTS.md"
```

The native migration is complete when the end-to-end workflow passes and remaining compatibility search results are intentional historical evidence outside the active instructions.
