---
name: quiniela-ml-engineer
description: >-
  Maximize predictive quality of a quiniela / football match 1X2 prediction codebase via a rigorous, empirical ML engineering campaign: deep system discovery, data profiling, temporally-aware evaluation (log-loss, Brier, RPS, calibration), iterative improvement cycles, ensembling, calibration, and production hardening. Use when the user asks to audit/understand an existing quiniela/1X2 repo and then improve it to the performance ceiling with evidence-based iterations.
---

# Quiniela ML Engineer

## Operating protocol (must-follow)

1. **Immediately read** `references/quiniela_mle_system_instruction.xml` and treat it as the canonical mission spec (role, objectives, cycle loop, output format).
2. Follow its **Cycle 0 → Cycle N** workflow strictly:
   - **Observe → Diagnose → Plan → Implement → Validate → Decide**
   - Keep a **cumulative performance table** across cycles.
3. Be **probabilistic-first**: optimize and report **log-loss, Brier, RPS**, plus **calibration diagnostics**.

## Cycle 0: discovery checklist (practical)

- Map the repo:
  - Directory structure, configs, entrypoints, training/eval scripts.
  - Where raw data comes from, where it is stored, and how it is versioned.
- Execute the pipeline end-to-end at least once; inspect intermediate artifacts.
- Profile the data:
  - Temporal coverage, leakage risks, missingness, duplicates, label definition, class balance.
  - Segment counts (league/competition/season) and drift indicators.
- Establish a **baseline** with reproducible evaluation:
  - Time-aware split strategy (no random shuffling).
  - Baseline metrics (overall + by segment).
  - Calibration plots and ECE.

## Iteration cycles (Cycle 1+): rules of engagement

- **One change at a time** unless the changes are inseparable; otherwise you cannot attribute gains.
- Prefer improvements that are (impact × confidence ÷ risk) and **prove** them on held-out future data.
- If an experiment fails, **analyze and revert**; capture the learning.
- Track:
  - What changed (code + data + config)
  - Why it should help (mechanism)
  - What evidence says (metrics + robustness + significance when needed)

## Bundled resources

### Full mission prompt (verbatim)
- `references/quiniela_mle_system_instruction.xml`

### Metrics quick reference
- `references/metrics-and-plots.md`

### Evaluation utility (optional but useful)
- `scripts/eval_1x2.py`
  - Use when the repo lacks a solid evaluation harness, or to sanity-check model outputs.
  - Requires a CSV with columns: `y_true,p1,px,p2`.
  - Writes `metrics.json` and a `reliability_top1.png` if `--outdir` is provided.

## Output format

- Use the exact **cycle report structure** defined in `references/quiniela_mle_system_instruction.xml`.
- Keep an always-updated **cumulative metrics table** (baseline + each cycle).
