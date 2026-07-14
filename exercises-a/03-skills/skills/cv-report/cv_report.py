"""cv_report — stratified cross-validation report for a classifier.

Two ways to use it:

1. As a library — pass your own estimator/Pipeline and X, y:

       from cv_report import cv_report
       cv_report(pipe, X, y, n_splits=5)

   `pipe` should be a full sklearn Pipeline so preprocessing re-fits per fold
   (that's what keeps the CV honest — no leakage).

2. As a CLI on a CSV — it builds a sensible default leak-free Pipeline
   (median-impute + scale numerics, one-hot categoricals, LogisticRegression):

       python cv_report.py experiment.csv --target outcome \
           --drop outcome_label sample_id

The report is per-fold values plus mean±std for accuracy, F1, and ROC-AUC, with a
one-line class-balance note so an imbalanced target can't hide behind accuracy.
"""

from __future__ import annotations

import argparse
from typing import Iterable, Sequence

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DEFAULT_SCORING = ("accuracy", "f1", "roc_auc")


def cv_report(
    estimator: BaseEstimator,
    X: pd.DataFrame,
    y: Sequence,
    *,
    n_splits: int = 5,
    scoring: Iterable[str] = DEFAULT_SCORING,
    random_state: int = 0,
) -> dict[str, np.ndarray]:
    """Run stratified k-fold CV and print a tidy per-fold + mean±std report.

    Returns the raw score arrays keyed by metric name, so callers can post-process.
    """
    y = np.asarray(y)
    scoring = list(scoring)
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    results = cross_validate(estimator, X, y, cv=cv, scoring=scoring)

    pos_rate = float(np.mean(y))
    print(
        f"class balance: {pos_rate:.1%} positive "
        f"({int(y.sum())}/{len(y)}) — "
        f"{'accuracy alone is misleading' if min(pos_rate, 1 - pos_rate) < 0.4 else 'roughly balanced'}"
    )
    print(f"stratified {n_splits}-fold CV:")
    out: dict[str, np.ndarray] = {}
    for m in scoring:
        s = results[f"test_{m}"]
        out[m] = s
        per_fold = ", ".join(f"{v:.3f}" for v in s)
        print(f"  {m:9s} {s.mean():.3f} ± {s.std():.3f}   [{per_fold}]")
    return out


def _default_pipeline(X: pd.DataFrame) -> Pipeline:
    """A leak-free default: impute+scale numerics, one-hot categoricals, LogReg."""
    num = X.select_dtypes(include="number").columns.tolist()
    cat = [c for c in X.columns if c not in num]
    pre = ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]
                ),
                num,
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), cat),
        ]
    )
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000, random_state=0))])


def _clean_experiment(df: pd.DataFrame) -> pd.DataFrame:
    """Light, fit-free cleaning for the workshop CSV (safe before CV)."""
    df = df.drop_duplicates().copy()
    if "treatment_group" in df:
        df["treatment_group"] = (
            df["treatment_group"].str.strip().str.lower().replace({"ctrl": "control"})
        )
    if "concentration" in df and not pd.api.types.is_numeric_dtype(df["concentration"]):
        df["concentration"] = (
            df["concentration"].astype(str).str.extract(r"([-+]?\d*\.?\d+)").astype(float)
        )
    if "temperature_C" in df:
        df.loc[df["temperature_C"] > 200, "temperature_C"] = np.nan
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description="Stratified CV report for a CSV classifier.")
    ap.add_argument("csv", help="path to a CSV with the target column")
    ap.add_argument("--target", default="outcome", help="target column (default: outcome)")
    ap.add_argument(
        "--drop",
        nargs="*",
        default=["outcome_label", "sample_id"],
        help="columns to exclude from features (default: outcome_label sample_id)",
    )
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--no-clean", action="store_true", help="skip the workshop CSV cleaning")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    if not args.no_clean:
        df = _clean_experiment(df)

    if args.target not in df.columns:
        raise SystemExit(f"target column {args.target!r} not found in {args.csv}")
    drop = [c for c in [args.target, *args.drop] if c in df.columns]
    if any(c in df.columns for c in ("outcome_label",)) and "outcome_label" not in drop:
        print("WARNING: 'outcome_label' is present and NOT dropped — this leaks the target!")
    y = df[args.target].astype(int)
    X = df.drop(columns=drop)

    cv_report(_default_pipeline(X), X, y, n_splits=args.n_splits)


if __name__ == "__main__":
    main()
