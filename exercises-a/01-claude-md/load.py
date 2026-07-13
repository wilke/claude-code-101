"""Tiny starter: read experiment.csv and print its shape.

This deliberately does NOT clean, split, or model anything — it exists only so
`/init` has a little code to read. The whole point of Exercise 01 is that a stub
like this tells `/init` almost nothing about the modeling task: which column is the
target, which column leaks it, or that fitting must happen after the split. That
contract is yours to write into CLAUDE.md.

Run:
    python load.py
"""

from pathlib import Path

import pandas as pd


def load(path: str = "experiment.csv") -> pd.DataFrame:
    """Load the experiment table as a DataFrame."""
    return pd.read_csv(Path(path))


if __name__ == "__main__":
    df = load()
    print(f"{df.shape[0]} rows x {df.shape[1]} columns")
    print("columns:", list(df.columns))
