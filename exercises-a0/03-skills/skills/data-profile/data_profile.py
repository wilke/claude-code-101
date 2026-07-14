"""data_profile.py — a quick, opinionated profile of any tabular CSV.

Prints per-column dtype, missingness, cardinality, numeric summaries, and the top
categories for categorical columns — then FLAGS columns that look suspicious
(constant, mostly-missing, likely-ID, or numbers hidden inside unit strings).

    python data_profile.py experiment.csv
    python data_profile.py experiment.csv --max-missing 0.4 --top 5
"""
from __future__ import annotations

import argparse
import re

import pandas as pd

# a number optionally followed by a unit, e.g. "1.5 mg/mL", "37 C", "12%"
_UNIT_NUMBER = re.compile(r"^\s*[-+]?\d*\.?\d+\s*[A-Za-z%/µ]+.*$")


def _fmt(x: object) -> str:
    """Format a numeric summary value, tolerating None / NaN (empty columns)."""
    try:
        return f"{float(x):.3g}"
    except (TypeError, ValueError):
        return "n/a"


def looks_unit_suffixed(s: pd.Series, sample: int = 50) -> bool:
    """True if an object column looks like numbers-with-units stored as strings."""
    vals = s.dropna().astype(str).head(sample)
    if len(vals) == 0:
        return False
    hits = sum(bool(_UNIT_NUMBER.match(v)) for v in vals)
    return hits >= 0.8 * len(vals)


def profile(df: pd.DataFrame, max_missing: float, top: int) -> list[str]:
    n = len(df)
    flags: list[str] = []
    print(f"rows: {n}   columns: {df.shape[1]}")
    print(f"duplicate rows: {int(df.duplicated().sum())}")
    print("-" * 68)

    for col in df.columns:
        s = df[col]
        missing = s.isna().sum()
        miss_frac = missing / n if n else 0.0
        nunique = s.nunique(dropna=True)
        line = (
            f"{col:<18} {str(s.dtype):<9} "
            f"missing={missing:>4} ({miss_frac:5.1%})  unique={nunique}"
        )
        print(line)

        if pd.api.types.is_numeric_dtype(s):
            desc = s.describe()
            print(
                f"    min={_fmt(desc.get('min'))}  mean={_fmt(desc.get('mean'))}  "
                f"max={_fmt(desc.get('max'))}"
            )
        else:
            vc = s.value_counts(dropna=True).head(top)
            print("    top:", ", ".join(f"{k!r}×{v}" for k, v in vc.items()))

        # ---- suspicion flags -------------------------------------------------
        if nunique <= 1:
            flags.append(f"{col}: constant (only {nunique} distinct value)")
        if miss_frac > max_missing:
            flags.append(f"{col}: {miss_frac:.0%} missing (> {max_missing:.0%})")
        if nunique >= 0.95 * n and nunique > 1:
            flags.append(f"{col}: near-unique — likely an ID, not a feature")
        if not pd.api.types.is_numeric_dtype(s) and looks_unit_suffixed(s):
            flags.append(f"{col}: numbers stored as unit strings — parse to float")

    return flags


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("csv")
    ap.add_argument("--max-missing", type=float, default=0.4,
                    help="flag columns missing more than this fraction (default 0.4)")
    ap.add_argument("--top", type=int, default=5,
                    help="how many top categories to show per categorical column")
    args = ap.parse_args()

    df = pd.read_csv(args.csv)
    flags = profile(df, args.max_missing, args.top)

    print("-" * 68)
    if flags:
        print("FLAGS:")
        for f in flags:
            print(f"  ! {f}")
    else:
        print("no columns flagged")


if __name__ == "__main__":
    main()
