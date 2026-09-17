#!/usr/bin/env python3
"""Evaluate probabilistic 1X2 predictions.

Input CSV must contain:
  - y_true: one of {"1","X","2"} or {0,1,2} (mapped to 1,X,2)
  - p1, px, p2: predicted probabilities

Optional columns:
  - date: any pandas-parseable datetime (for temporal slicing)
  - league / competition: grouping

Outputs a JSON summary to stdout and (optionally) writes plots.

Example:
  python3 scripts/eval_1x2.py --csv preds.csv --outdir artifacts/eval
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import asdict, dataclass

import numpy as np


def _soft_import_pandas():
    try:
        import pandas as pd  # type: ignore
    except Exception as e:
        raise SystemExit(
            "pandas is required for this script. Install with: pip install pandas"
        ) from e
    return pd


def _clip_probs(p: np.ndarray, eps: float = 1e-15) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    p = np.clip(p, eps, 1.0 - eps)
    # renormalize rows
    row_sum = p.sum(axis=1, keepdims=True)
    row_sum = np.where(row_sum == 0, 1.0, row_sum)
    return p / row_sum


def _y_to_index(y):
    if isinstance(y, str):
        y = y.strip()
        if y in {"1", "X", "2"}:
            return {"1": 0, "X": 1, "2": 2}[y]
        # allow numeric strings
        if y in {"0", "1", "2"}:
            return int(y)
    if isinstance(y, (int, np.integer)):
        if int(y) in {0, 1, 2}:
            return int(y)
    raise ValueError(f"Unsupported y_true value: {y!r} (expected 1/X/2 or 0/1/2)")


def multiclass_log_loss(p: np.ndarray, y_idx: np.ndarray) -> float:
    p = _clip_probs(p)
    return float(-np.mean(np.log(p[np.arange(len(y_idx)), y_idx])))


def multiclass_brier(p: np.ndarray, y_idx: np.ndarray) -> float:
    p = _clip_probs(p)
    y_oh = np.zeros_like(p)
    y_oh[np.arange(len(y_idx)), y_idx] = 1.0
    return float(np.mean(np.sum((p - y_oh) ** 2, axis=1)))


def rps_1x2(p: np.ndarray, y_idx: np.ndarray) -> float:
    """Ranked Probability Score for ordered categories [1, X, 2].

    Note: 1X2 is not strictly ordinal, but RPS is widely used for 1X2 markets
    with this conventional ordering.
    """

    p = _clip_probs(p)
    n = len(y_idx)
    # cumulative predicted
    cdf_p = np.cumsum(p, axis=1)
    # cumulative observed
    y_oh = np.zeros_like(p)
    y_oh[np.arange(n), y_idx] = 1.0
    cdf_y = np.cumsum(y_oh, axis=1)
    # RPS sums over K-1 thresholds; for K=3 thresholds=2
    rps = np.mean(np.sum((cdf_p[:, :-1] - cdf_y[:, :-1]) ** 2, axis=1))
    return float(rps)


def accuracy(p: np.ndarray, y_idx: np.ndarray) -> float:
    return float(np.mean(np.argmax(p, axis=1) == y_idx))


def ece_top1(p: np.ndarray, y_idx: np.ndarray, n_bins: int = 15) -> float:
    """Multiclass ECE computed on top-1 confidence (common practical choice)."""
    p = _clip_probs(p)
    conf = np.max(p, axis=1)
    pred = np.argmax(p, axis=1)
    correct = (pred == y_idx).astype(float)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (conf > lo) & (conf <= hi) if i > 0 else (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        acc_bin = float(np.mean(correct[mask]))
        conf_bin = float(np.mean(conf[mask]))
        w = float(np.mean(mask))
        ece += w * abs(acc_bin - conf_bin)
    return float(ece)


@dataclass
class Metrics:
    n: int
    log_loss: float
    brier: float
    rps: float
    accuracy: float
    ece_top1: float


def compute_metrics(p: np.ndarray, y_idx: np.ndarray) -> Metrics:
    return Metrics(
        n=int(len(y_idx)),
        log_loss=multiclass_log_loss(p, y_idx),
        brier=multiclass_brier(p, y_idx),
        rps=rps_1x2(p, y_idx),
        accuracy=accuracy(p, y_idx),
        ece_top1=ece_top1(p, y_idx),
    )


def maybe_write_reliability_plot(outdir: str, p: np.ndarray, y_idx: np.ndarray, n_bins: int = 15):
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        return  # plotting optional

    os.makedirs(outdir, exist_ok=True)

    p = _clip_probs(p)
    conf = np.max(p, axis=1)
    pred = np.argmax(p, axis=1)
    correct = (pred == y_idx).astype(float)

    bins = np.linspace(0.0, 1.0, n_bins + 1)
    xs, ys, ws = [], [], []
    for i in range(n_bins):
        lo, hi = bins[i], bins[i + 1]
        mask = (conf > lo) & (conf <= hi) if i > 0 else (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        xs.append(float(np.mean(conf[mask])))
        ys.append(float(np.mean(correct[mask])))
        ws.append(int(np.sum(mask)))

    plt.figure(figsize=(6, 6))
    plt.plot([0, 1], [0, 1], "--", color="gray", linewidth=1)
    plt.scatter(xs, ys, s=[max(20, w) for w in ws], alpha=0.8)
    plt.title("Top-1 Reliability (size ~ count)")
    plt.xlabel("Mean confidence")
    plt.ylabel("Empirical accuracy")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "reliability_top1.png"), dpi=160)
    plt.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True, help="CSV with y_true,p1,px,p2")
    ap.add_argument("--outdir", default=None, help="If set, write plots/artifacts here")
    ap.add_argument("--group", default=None, help="Optional column to group by (e.g., league)")
    ap.add_argument("--date", default=None, help="Optional date column for sorting (e.g., date)")
    args = ap.parse_args()

    pd = _soft_import_pandas()
    df = pd.read_csv(args.csv)

    required = ["y_true", "p1", "px", "p2"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise SystemExit(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    y_idx = np.array([_y_to_index(v) for v in df["y_true"].tolist()], dtype=int)
    p = df[["p1", "px", "p2"]].to_numpy(dtype=float)

    # optional: sort by date (helps temporal diagnostics downstream)
    if args.date and args.date in df.columns:
        d = pd.to_datetime(df[args.date], errors="coerce")
        order = np.argsort(np.where(d.isna(), np.datetime64("2100-01-01"), d.values))
        y_idx = y_idx[order]
        p = p[order]
        df = df.iloc[order].reset_index(drop=True)

    summary = {
        "overall": asdict(compute_metrics(p, y_idx)),
    }

    if args.group and args.group in df.columns:
        by = {}
        for g, sub in df.groupby(args.group):
            y_g = np.array([_y_to_index(v) for v in sub["y_true"].tolist()], dtype=int)
            p_g = sub[["p1", "px", "p2"]].to_numpy(dtype=float)
            by[str(g)] = asdict(compute_metrics(p_g, y_g))
        summary["by_group"] = by

    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)
        with open(os.path.join(args.outdir, "metrics.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        maybe_write_reliability_plot(args.outdir, p, y_idx)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
