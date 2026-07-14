"""summary.py — a one-figure overview of the cleaned experiment data.

Reads experiment_clean.csv (produced by clean.py) and saves a bar chart of mean
yield per treatment group to figures/. Never calls plt.show() — figures are saved,
not popped up (a house rule from CLAUDE.md).

    python summary.py                     # reads experiment_clean.csv
    python summary.py --in experiment_clean.csv
"""
from __future__ import annotations

import argparse
import os

import matplotlib

matplotlib.use("Agg")  # headless: save files, never open a window
import matplotlib.pyplot as plt
import pandas as pd

GROUP_ORDER = ["control", "low", "high"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--in", dest="inp", default="experiment_clean.csv")
    ap.add_argument("--figdir", default="figures")
    args = ap.parse_args()

    df = pd.read_csv(args.inp)
    means = (
        df.groupby("treatment_group")["yield"]
        .mean()
        .reindex(GROUP_ORDER)
    )

    os.makedirs(args.figdir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.bar(means.index, means.values, color=["#888", "#4a90d9", "#0a7d46"])
    ax.set_xlabel("treatment group")
    ax.set_ylabel("mean yield")
    ax.set_title("Mean yield by treatment group")
    fig.tight_layout()
    out = os.path.join(args.figdir, "yield_by_group.png")
    fig.savefig(out, dpi=130)
    plt.close(fig)

    print("mean yield by group:\n", means.to_string())
    print(f"saved {out}")


if __name__ == "__main__":
    main()
