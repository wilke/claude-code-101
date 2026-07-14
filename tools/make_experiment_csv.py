#!/usr/bin/env python3
"""Generate the shared, deliberately-messy `experiment.csv` for the a0/a tracks.

This script is the *hidden generator*: it knows the clean structure of the data,
so it must live OUTSIDE any directory where a student runs `claude` (the workshop
rule is "Claude should see the problem, never the solution"). Run it once and copy
the resulting CSV into the exercise folders that ship data.

The table is a synthetic "generic lab experiment" with real signal in `yield`
(continuous) and `outcome` (binary, ~30% positive so class imbalance is a live
issue for track A), plus six injected data-quality problems:

  1. missing values          -> a few blank `temperature_C` and `concentration`
  2. inconsistent categories  -> control/Control/CTRL/" control ", plus case noise
  3. a numeric outlier        -> one `temperature_C == 9999` (data-entry error)
  4. unit-suffixed numbers    -> `concentration` stored as "1.5 mg/mL" strings
  5. duplicate rows           -> a few repeated `sample_id` rows
  6. a leaky column           -> `outcome_label` trivially restates `outcome`

Usage:
    python tools/make_experiment_csv.py [--out experiment.csv] [--n 400] [--seed 42]
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

# Reproducible on purpose: the committed CSV must be identical for every learner.
SEED = 42
N_BASE = 400

CONTROL_SPELLINGS = ["control", "Control", "CTRL", " control "]
LOW_SPELLINGS = ["low", "Low", "LOW"]
HIGH_SPELLINGS = ["high", "High", "HIGH"]

# Effect of each (clean) treatment group on yield / on the outcome latent.
TREATMENT_YIELD = {"control": 0.0, "low": 4.0, "high": 8.0}
TREATMENT_LOGIT = {"control": -0.4, "low": 0.2, "high": 1.1}


def _spell(rng: np.random.Generator, group: str) -> str:
    """Render a clean group label with realistic, inconsistent spelling."""
    if group == "control":
        return rng.choice(CONTROL_SPELLINGS)
    if group == "low":
        return rng.choice(LOW_SPELLINGS)
    return rng.choice(HIGH_SPELLINGS)


def build(n: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    sample_id = np.arange(1000, 1000 + n)
    batch = rng.choice([f"B{i}" for i in range(1, 7)], size=n)
    group = rng.choice(["control", "low", "high"], size=n, p=[0.5, 0.3, 0.2])

    # Clean latent numerics with genuine structure.
    temperature = rng.normal(37.0, 2.5, size=n)
    concentration = rng.uniform(0.5, 3.0, size=n)

    treat_yield = np.array([TREATMENT_YIELD[g] for g in group])
    treat_logit = np.array([TREATMENT_LOGIT[g] for g in group])

    # yield: continuous regression target, driven by temp, concentration, group.
    yield_ = (
        50.0
        + 1.8 * (temperature - 37.0)
        + 6.0 * concentration
        + treat_yield
        + rng.normal(0.0, 3.5, size=n)
    )

    # outcome: binary target from a logistic latent; threshold tuned to ~30% positive.
    logit = (
        -1.5
        + 0.55 * (temperature - 37.0)
        + 0.9 * (concentration - 1.75)
        + treat_logit
        + rng.normal(0.0, 0.8, size=n)
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    outcome = (rng.uniform(size=n) < prob).astype(int)

    df = pd.DataFrame(
        {
            "sample_id": sample_id,
            "batch": batch,
            "treatment_group": [_spell(rng, g) for g in group],
            "temperature_C": np.round(temperature, 2),
            # store concentration as unit-suffixed strings ("1.5 mg/mL")
            "concentration": [f"{c:.1f} mg/mL" for c in concentration],
            "yield": np.round(yield_, 2),
            "outcome": outcome,
            "outcome_label": np.where(outcome == 1, "success", "failure"),
        }
    )

    # ---- inject the remaining data-quality problems -------------------------
    # (2b) a little case noise on a handful of low/high labels already handled
    #      by _spell; nothing more needed here.

    # (1) missing temperature_C  (blank cells)
    miss_temp = rng.choice(n, size=6, replace=False)
    df.loc[miss_temp, "temperature_C"] = np.nan

    # (1) missing concentration (blank string)
    miss_conc = rng.choice(n, size=5, replace=False)
    df.loc[miss_conc, "concentration"] = ""

    # (3) one outlier temperature: a fat-fingered 9999
    df.loc[rng.choice(n, size=1), "temperature_C"] = 9999.0

    # (5) duplicate rows: repeat a few whole rows (same sample_id)
    dup_rows = df.iloc[rng.choice(n, size=3, replace=False)].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)

    # shuffle so the duplicates and outlier aren't at obvious positions
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="experiment.csv")
    ap.add_argument("--n", type=int, default=N_BASE)
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args()

    df = build(args.n, args.seed)
    df.to_csv(args.out, index=False)

    pos = int(df["outcome"].sum())
    print(f"wrote {args.out}: {len(df)} rows (incl. duplicates), {df.shape[1]} cols")
    print(f"  outcome positives: {pos}/{len(df)} = {pos / len(df):.1%}")
    print(f"  duplicate sample_id rows: {int(df.duplicated('sample_id').sum())}")


if __name__ == "__main__":
    main()
