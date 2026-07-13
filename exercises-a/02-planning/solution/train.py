"""train.py — leak-free baseline classifier for `outcome`.

Reference solution for Exercise 02 (track A). Demonstrates the spine of the track:
clean (row-level) -> stratified split -> preprocessing INSIDE a Pipeline ->
stratified CV -> held-out test -> ROC figure. Every fitted step (impute, scale,
one-hot, estimator) lives inside the Pipeline, so cross-validation re-fits it per
fold and no test information leaks into training.

Run:
    python train.py --in experiment.csv --figdir figures
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless backend; never plt.show()
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import RocCurveDisplay, f1_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

OUTLIER_TEMP = 200.0
LEAKY_COLS = ["outcome_label"]  # NEVER a feature — restates the target
ID_COLS = ["sample_id"]
NUM_FEATURES = ["temperature_C", "concentration"]
CAT_FEATURES = ["batch", "treatment_group"]
RANDOM_STATE = 0
N_SPLITS = 5


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Row-level, fit-free cleaning — safe to run before the split.

    These are deterministic per-row transforms with no learned parameters.
    Imputation and scaling are deliberately NOT here: they fit state and must
    live inside the Pipeline, after the split.
    """
    df = df.drop_duplicates().copy()
    df["treatment_group"] = (
        df["treatment_group"].str.strip().str.lower().replace({"ctrl": "control"})
    )
    df["concentration"] = (
        df["concentration"].astype(str).str.extract(r"([-+]?\d*\.?\d+)").astype(float)
    )
    df.loc[df["temperature_C"] > OUTLIER_TEMP, "temperature_C"] = np.nan
    return df


def build_pipeline() -> Pipeline:
    """Preprocessing + estimator as ONE Pipeline, so it re-fits per CV fold."""
    pre = ColumnTransformer(
        [
            (
                "num",
                Pipeline(
                    [
                        ("impute", SimpleImputer(strategy="median")),
                        ("scale", StandardScaler()),
                    ]
                ),
                NUM_FEATURES,
            ),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_FEATURES),
        ]
    )
    return Pipeline(
        [
            ("pre", pre),
            (
                "clf",
                LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
            ),
        ]
    )


def split_xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    y = df["outcome"].astype(int)
    drop = ["outcome", *LEAKY_COLS, *ID_COLS]
    X = df.drop(columns=[c for c in drop if c in df.columns])
    assert "outcome_label" not in X.columns, "LEAK: outcome_label must not be a feature"
    return X, y


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", default="experiment.csv")
    ap.add_argument("--figdir", default="figures")
    args = ap.parse_args()

    df = clean(pd.read_csv(args.inp))
    X, y = split_xy(df)
    print(f"rows={len(X)}  positive rate={y.mean():.3f}  (class balance)")

    # Stratified hold-out test, kept untouched until the very end.
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    pipe = build_pipeline()

    # Stratified CV on the training portion — Pipeline re-fits each fold.
    cv = StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_STATE)
    scoring = ["accuracy", "f1", "roc_auc"]
    scores = cross_validate(pipe, X_tr, y_tr, cv=cv, scoring=scoring)
    print(f"\nStratified {N_SPLITS}-fold CV (LogisticRegression):")
    for m in scoring:
        s = scores[f"test_{m}"]
        per_fold = ", ".join(f"{v:.3f}" for v in s)
        print(f"  {m:9s} {s.mean():.3f} ± {s.std():.3f}   [{per_fold}]")

    # Fit on full training set, evaluate ONCE on the held-out test.
    pipe.fit(X_tr, y_tr)
    proba = pipe.predict_proba(X_te)[:, 1]
    pred = (proba >= 0.5).astype(int)
    print("\nHeld-out test (never seen during CV):")
    print(f"  F1      {f1_score(y_te, pred):.3f}")
    print(f"  ROC-AUC {roc_auc_score(y_te, proba):.3f}")

    figdir = Path(args.figdir)
    figdir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 5))
    RocCurveDisplay.from_predictions(y_te, proba, ax=ax, name="LogReg")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="chance")
    ax.set_title("ROC — held-out test")
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = figdir / "roc_curve.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
