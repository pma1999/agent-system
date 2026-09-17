# 1X2 Metrics & Diagnostics (quick reference)

## Core metrics (probabilistic)

- **Log-loss (multiclass)**: `-mean(log(p_true_class))`.
  - Primary metric when optimizing probabilistic quality.

- **Brier score (multiclass)**: `mean(sum_k (p_k - y_k)^2)`.
  - More sensitive to calibration / probability mass shifts.

- **RPS (Ranked Probability Score)** for 1X2 using conventional ordering `[1, X, 2]`.
  - Uses cumulative probabilities; common in football prediction evaluation.

- **ECE (Expected Calibration Error)** (top-1 variant): bin max-probability confidence vs empirical correctness.
  - Pair with **reliability diagrams**.

## Recommended diagnostics (non-exhaustive)

- Calibration: reliability diagrams + ECE; class-conditional calibration curves.
- Temporal stability: metrics by season / rolling windows; detect drift.
- Segment robustness: by league/competition, home/away strength bands, odds bands (if market features exist).
- Error anatomy: confusion matrix on argmax AND probability error decomposition.
- Significance: paired bootstrap on per-match log-loss deltas; report CI.

## Bundled script

- `scripts/eval_1x2.py` evaluates a CSV with columns: `y_true,p1,px,p2` and can write `metrics.json` + `reliability_top1.png`.
