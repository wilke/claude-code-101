"""clean.py — turn the messy experiment.csv into a tidy experiment_clean.csv.

Implements the plan in plan.md. Every cleaning step prints what it changed so the
before/after is auditable. Run from a directory containing experiment.csv:

    python clean.py                       # writes experiment_clean.csv
    python clean.py --in experiment.csv --out experiment_clean.csv
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

OUTLIER_TEMP = 200.0  # any temperature above this (e.g. 9999) is a data-entry error


def load_and_profile(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print("== before ==")
    print("shape:", df.shape)
    print("dtypes:\n", df.dtypes.to_string())
    print("missing per column:\n", df.isna().sum().to_string())
    print("duplicate rows:", int(df.duplicated().sum()))
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 2. drop full-row duplicates
    n_before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    print(f"\ndropped {n_before - len(df)} duplicate rows")

    # 3. normalize treatment_group -> {control, low, high}
    df["treatment_group"] = (
        df["treatment_group"].str.strip().str.lower().replace({"ctrl": "control"})
    )
    groups = set(df["treatment_group"].unique())
    assert groups <= {"control", "low", "high"}, f"unexpected groups: {groups}"
    print("treatment groups after normalize:", sorted(groups))

    # 4. parse concentration "1.5 mg/mL" -> float mg/mL; blanks -> NaN
    df["concentration"] = (
        df["concentration"].astype(str).str.extract(r"([-+]?\d*\.?\d+)").astype(float)
    )

    # 5. quarantine the impossible 9999 temperature (decision (a) in plan.md)
    n_outlier = int((df["temperature_C"] > OUTLIER_TEMP).sum())
    df.loc[df["temperature_C"] > OUTLIER_TEMP, "temperature_C"] = np.nan
    print(f"quarantined {n_outlier} temperature outlier(s) (> {OUTLIER_TEMP} C) -> NaN")

    return df


def report(df: pd.DataFrame) -> None:
    print("\n== after ==")
    print("shape:", df.shape)
    print("dtypes:\n", df.dtypes.to_string())
    print("missing per column:\n", df.isna().sum().to_string())
    print("\nper-treatment_group means:")
    print(df.groupby("treatment_group")[["yield", "temperature_C"]].mean().to_string())

    # 8. sanity checks
    assert df.duplicated().sum() == 0, "duplicates remain"
    assert set(df["treatment_group"]) <= {"control", "low", "high"}
    assert df["concentration"].dtype.kind == "f"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", default="experiment.csv")
    ap.add_argument("--out", default="experiment_clean.csv")
    args = ap.parse_args()

    df = load_and_profile(args.inp)
    df = clean(df)
    report(df)
    df.to_csv(args.out, index=False)
    print(f"\nwrote {args.out}: {len(df)} rows")


if __name__ == "__main__":
    main()
