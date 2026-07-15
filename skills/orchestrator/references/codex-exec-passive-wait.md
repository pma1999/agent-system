# Codex-exec passive wait

Use this wrapper immediately after a start or resume dispatch returns `job_id`. Replace the three placeholders and keep the control flow unchanged.

```javascript
// @exec: {"yield_time_ms": 2147483647, "max_output_tokens": 4000}
const heartbeatMs = 55_000;
let heartbeat;

const emitHeartbeat = () => {
  notify("The delegated specialist is still running; passive event wait remains active.");
  heartbeat = setTimeout(emitHeartbeat, heartbeatMs);
};

heartbeat = setTimeout(emitHeartbeat, heartbeatMs);
try {
  const result = await tools.shell_command({
    command: "& '<absolute-invoke-specialist.ps1>' -Wait -JobId '<job-id>'",
    workdir: "<project-root>",
    timeout_ms: 2147483647
  });
  text(result);
} finally {
  clearTimeout(heartbeat);
}
```

The `functions.exec` pragma prevents its normal early yield, and the matching shell timeout keeps the waiter attached for the maximum broadly safe signed-32-bit timer window (about 24.8 days). This is an observation window, not an agent runtime limit: the Scheduled Task has no execution limit and durable job state survives the waiter, parent, and app.

The 55-second heartbeat is emitted by the still-running tool call. It provides host-visible progress without returning control to the model, reading job state, or spending another inference turn. Do not replace it with repeated `-Status`, `-List`, shell-cell waits, sleeps, or short `-Wait` invocations.

Normally the wrapper returns only when `result.json` is published and `-Wait` reports `completed`, `failed`, or `interrupted`. If the host itself terminates the tool call, the app closes, or the machine restarts, reattach once to the same `job_id` with the same wrapper. Never create a replacement agent merely because observation was interrupted.

## Retention and cleanup

After the wrapper returns, record the job ID, terminal state, session ID, and relevant outcome/error in the current workflow's `progress.md`. Do not clean the job at agent completion, review completion, or final-review `PASS`; its inactive Scheduled Task definition and durable directory are intentionally retained for diagnosis and efficient follow-up.

After the user explicitly confirms workflow closure and no work remains, take job IDs only from that workflow's ledger. Verify each is terminal, then run:

```powershell
scripts/invoke-specialist.ps1 -Cleanup -JobId <recorded-job-id>
```

Record the returned `state`, `previous_state`, and `cleaned_at`. If a scoped job is active, passively wait for it instead of cleaning or terminating it. Never derive a bulk-deletion scope from `-List`, and never delete `.orchestrator/jobs` manually.
