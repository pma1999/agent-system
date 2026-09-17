#!/usr/bin/env python3
"""Claude Code status line — two-line, cached, resilient."""
import json, sys, os, subprocess, time

def c(code, text):
    return f"\033[{code}m{text}\033[0m" if text else ""

DIM, CYAN = lambda t: c("2", t), lambda t: c("36", t)
GREEN, YEL, RED, BOLD = (
    lambda t: c("32", t), lambda t: c("33", t),
    lambda t: c("31;1", t), lambda t: c("1", t),
)

_cache = {}

def git_info(cwd, session_id):
    now = time.time()
    key = session_id + cwd
    if key in _cache and now - _cache[key][0] < 5:
        return _cache[key][1]
    branch = ""
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "branch", "--show-current"],
            capture_output=True, text=True, stderr=subprocess.DEVNULL, timeout=3)
        branch = r.stdout.strip()
    except Exception:
        pass
    if not branch:
        _cache[key] = (now, None)
        return None
    staged = modified = 0
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "diff", "--name-only", "--cached"],
            capture_output=True, text=True, stderr=subprocess.DEVNULL, timeout=3)
        staged = len([l for l in r.stdout.strip().splitlines() if l])
    except Exception:
        pass
    try:
        r = subprocess.run(
            ["git", "-C", cwd, "--no-optional-locks", "diff", "--name-only"],
            capture_output=True, text=True, stderr=subprocess.DEVNULL, timeout=3)
        modified = len([l for l in r.stdout.strip().splitlines() if l])
    except Exception:
        pass
    result = (branch, staged, modified)
    _cache[key] = (now, result)
    return result

try:
    raw = sys.stdin.read()
    d = json.loads(raw) if raw.strip() else {}
except Exception:
    d = {}

def g(path, default=None):
    v = d
    for p in path.split("."):
        if isinstance(v, dict):
            v = v.get(p)
        else:
            return default
        if v is None:
            return default
    return v

# ── LINE 1 ──────────────────────────────────────────────
p1 = []

model = g("model.display_name") or g("model.id")
if model:
    p1.append(CYAN(model))

cwd_path = g("workspace.current_dir") or g("cwd") or ""
if cwd_path:
    p1.append(BOLD(os.path.basename(cwd_path)))

session_id = g("session_id", "")
gi = git_info(cwd_path, session_id) if cwd_path else None
if gi:
    branch, staged, modified = gi
    gs = branch
    if staged:
        gs += " " + GREEN(f"+{staged}")
    if modified:
        gs += " " + YEL(f"~{modified}")
    p1.append(gs)

wt = g("worktree.name") or g("workspace.git_worktree")
if wt:
    p1.append(DIM(f"wt:{wt}"))

vm = g("vim.mode")
if vm:
    p1.append(DIM(f"[{vm}]"))

sn = g("session_name")
if sn:
    p1.append(DIM(f'"{sn}"'))

an = g("agent.name")
if an:
    p1.append(DIM(f"@{an}"))

line1 = " | ".join(x for x in p1 if x)

# ── LINE 2 ──────────────────────────────────────────────
p2 = []

used_pct = g("context_window.used_percentage")
has_pct = used_pct is not None and used_pct != ""

if has_pct:
    pct = float(used_pct)
    filled = max(0, min(10, int(round(pct / 10))))
    col = RED if pct >= 90 else (YEL if pct >= 70 else GREEN)
    bar = col("#" * filled) + DIM("-" * (10 - filled))
    p2.append(f"{bar} {pct:3.0f}%")
else:
    p2.append(DIM("---------- ---"))

# cost (rough Sonnet-tier: $3/M in, $15/M out)
it = g("context_window.total_input_tokens") or 0
ot = g("context_window.total_output_tokens") or 0
cost = (it * 3 + ot * 15) / 1_000_000
p2.append(f"${cost:.2f}")

# duration from transcript mtime (best proxy available)
transcript = g("transcript_path")
if transcript:
    try:
        age = time.time() - os.path.getmtime(transcript)
        h, rem = divmod(int(age), 3600)
        m, s = divmod(rem, 60)
        p2.append(f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}")
    except Exception:
        pass

# rate limits
rl = []
for label, path in [("5h", "rate_limits.five_hour.used_percentage"),
                     ("7d", "rate_limits.seven_day.used_percentage")]:
    v = g(path)
    if v is not None and v != "":
        rl.append(f"{label}:{float(v):.0f}%")
if rl:
    p2.append(DIM(" ".join(rl)))

# warnings
if has_pct:
    pct = float(used_pct)
    if pct >= 90:
        p2.append(RED("!CTX"))
    elif pct >= 70:
        p2.append(YEL("!CTX"))

# exceeds 200k
cw_size = g("context_window.context_window_size")
if has_pct and cw_size and int(cw_size) <= 200000:
    it2 = g("context_window.total_input_tokens") or 0
    ot2 = g("context_window.total_output_tokens") or 0
    if it2 + ot2 > 200000:
        p2.append(RED(">200k"))

line2 = " | ".join(x for x in p2 if x)

# ── output ──────────────────────────────────────────────
out = "\n".join(l for l in (line1, line2) if l)
sys.stdout.write(out + "\n")
