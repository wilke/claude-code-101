"""Optional: pull a *real* open snapshot of international match results.

NOT on any exercise's critical path. The committed `matches.csv` (a seeded synthetic
snapshot — see DATA_SOURCE.md) is authoritative so the exercises run offline and
identically for everyone. Use this only if you want the real, current results (e.g.
to add the 2026 final once it's played).

The canonical open source is the CC0 "International football results" compilation:
    https://github.com/martj42/international_results  (results.csv)

Usage:
    python refresh_data.py --out matches.csv

If the network is unavailable, this script prints how to fetch the file by hand and
leaves the committed snapshot untouched. After a successful pull, update the
"Provenance" line in DATA_SOURCE.md with the URL, license (CC0), and today's date.
"""

from __future__ import annotations

import argparse
import sys
from urllib.request import urlopen

RESULTS_URL = (
    "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default="matches.csv")
    ap.add_argument("--url", default=RESULTS_URL)
    args = ap.parse_args()

    try:
        with urlopen(args.url, timeout=30) as resp:  # noqa: S310 (documented URL)
            data = resp.read()
    except Exception as exc:  # offline / blocked / moved
        print(f"could not fetch {args.url!r}: {exc}", file=sys.stderr)
        print(
            "\nThe committed synthetic snapshot is unchanged. To refresh by hand:\n"
            f"  1. Download {args.url}\n"
            "  2. Keep only these columns: date, home_team, away_team, home_score,\n"
            "     away_score, tournament, neutral\n"
            "  3. Save as matches.csv and update DATA_SOURCE.md's Provenance line.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    with open(args.out, "wb") as fh:
        fh.write(data)
    print(f"wrote {args.out} from {args.url}")
    print("Now update DATA_SOURCE.md: set Provenance to this URL, license CC0, today's date.")


if __name__ == "__main__":
    main()
