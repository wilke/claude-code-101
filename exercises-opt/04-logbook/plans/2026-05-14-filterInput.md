# Plan: Command-line interface for `FilterADMM.py`

_Executed 2026-05-14. Result: `FilterADMM.py` now accepts seven CLI flags;
default invocation reproduces the previous self-test byte-for-byte.
`RASC-MeetingNotes.tex` §5.3 documents the new flags. See
"Post-implementation notes" at the bottom — implementation matched the plan
without divergences._

## Context

`FilterADMM.py` is the recommended ADMM-Filter driver for the compliance + graph-TV
problem. Today its `__main__` block hard-codes every problem parameter
(`nelx=30, nely=10, penal=3.0, alpha=0.5, budget=0.4*n, …`) — running a
different mesh size or volume fraction means editing the file. We want to
keep the in-file defaults (so `python3 FilterADMM.py` still runs the
30×10 / 40% / α=0.5 self-test unchanged) while exposing the most-tweaked
knobs as command-line flags so the same script can be re-used for
parameter sweeps without code edits.

The user's spec: expose `nelx`, `nely`, `volfrac`, `penal`, `alpha`, `plot`,
`verbose` on the CLI; do **not** expose `budget` directly — it is derived as
`volfrac × nelx × nely`. Defaults must match today's behaviour. Also fix
the banner print so its "30 x 10 / 40%" string reflects the actual values
in use, and add a short paragraph to `RASC-MeetingNotes.tex` §5 documenting
the new invocation.

## Files to modify

1. **`/home/leyffer/software/AIML/Claude/ADMM-MIP/admm_to/FilterADMM.py`** —
   add `import argparse`; rewrite the `__main__` block.
2. **`/home/leyffer/software/AIML/Claude/ADMM-MIP/admm_to/RASC-MeetingNotes.tex`** —
   extend §5.3 "Running the code" with a CLI-options paragraph + example.

`filter_admm_compliance_tv()` itself is **not** edited — only the
`__main__` block is. The function already accepts every parameter we need.

## Change to `FilterADMM.py`

### Add at top of file (with the other imports)

```python
import argparse
```

### Replace the current `__main__` block

The current block hard-codes `nelx, nely, budget = 30, 10, 0.4*n` and a
banner print of `"FilterADMM self-test: 30 x 10 cantilever, 40% volume
fraction"`. Replace with:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ADMM-Filter for compliance + graph-TV topology optimisation. "
                    "Defaults reproduce the 30x10 / 40% / alpha=0.5 self-test."
    )
    parser.add_argument("--nelx",    type=int,   default=30,
                        help="Number of elements in x (default: 30).")
    parser.add_argument("--nely",    type=int,   default=10,
                        help="Number of elements in y (default: 10).")
    parser.add_argument("--volfrac", type=float, default=0.4,
                        help="Volume fraction; budget = volfrac*nelx*nely "
                             "(default: 0.4).")
    parser.add_argument("--penal",   type=float, default=3.0,
                        help="SIMP penalisation exponent (default: 3.0).")
    parser.add_argument("--alpha",   type=float, default=0.5,
                        help="Graph-TV regularisation weight (default: 0.5).")
    parser.add_argument("--plot",    action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Save convergence + per-iter heat-map PDFs to "
                             "images/ (default: --plot).")
    parser.add_argument("--verbose", action=argparse.BooleanOptionalAction,
                        default=True,
                        help="Print per-outer-iteration trajectory "
                             "(default: --verbose).")
    args = parser.parse_args()

    nelx, nely = args.nelx, args.nely
    n          = nelx * nely
    budget     = args.volfrac * n

    print("=" * 72)
    print(f"FilterADMM self-test: {nelx} x {nely} cantilever, "
          f"{args.volfrac * 100:g}% volume fraction")
    print("=" * 72)

    x_opt, info = filter_admm_compliance_tv(
        nelx=nelx, nely=nely,
        penal=args.penal,
        alpha=args.alpha,
        budget=budget,
        rho_init=1.0,
        beta=0.99,
        gamma=1e-5,
        sigma=1e-5,
        U=10.0,
        max_outer=60,
        max_inner=20,
        max_restoration=30,
        eps_opt=1e-2,
        omega_tau=1.0,
        x_lo=1e-4,
        verbose=args.verbose,
        plot=args.plot,
    )

    # ... existing post-run summary block kept unchanged ...
```

The post-run summary block (`Reason / Converged / Outer iterations / …
Filter contents at exit`) and the eta-jump diagnostic are kept verbatim —
they already use `info[…]` and `budget` as locals, both of which remain in
scope.

### Why `BooleanOptionalAction`

Python 3.9+ idiom; the `RASC` env is 3.11 (per `CLAUDE.md`). Gives the
user `--plot` / `--no-plot` and `--verbose` / `--no-verbose` automatically,
with `True` defaults that match the current `__main__`. Keeps existing
behaviour byte-identical when the script is run with no arguments.

### Banner-print formatting

`{args.volfrac * 100:g}` renders `0.4 → 40`, `0.35 → 35`, `0.333 → 33.3`
without trailing zeros, so the banner stays clean for any reasonable
volume fraction.

## Change to `RASC-MeetingNotes.tex`

Extend §5.3 "Running the code" (currently lines ~447–484). Keep the
existing `python3 FilterADMM.py` and side-by-side blocks as-is. Insert,
between the side-by-side block and the "For programmatic use:" block, a
new paragraph documenting the CLI:

```latex
The script accepts command-line overrides for the most commonly tuned
parameters; defaults reproduce the self-test of \S\ref{subsec:result}:

\begin{verbatim}
python3 FilterADMM.py --help                          # list options
python3 FilterADMM.py --nelx 60 --nely 20             # larger mesh,
                                                      #   keep 40% volfrac
python3 FilterADMM.py --volfrac 0.3 --alpha 1.0       # different problem
python3 FilterADMM.py --no-plot --no-verbose          # silent batch run
\end{verbatim}

\noindent
The available flags are \texttt{--nelx} (int, default 30),
\texttt{--nely} (int, default 10),
\texttt{--volfrac} (float, default 0.4; budget is computed as
$\texttt{volfrac}\times\texttt{nelx}\times\texttt{nely}$),
\texttt{--penal} (float, default 3.0),
\texttt{--alpha} (float, default 0.5),
\texttt{--plot}/\texttt{--no-plot} (default \texttt{--plot}),
and \texttt{--verbose}/\texttt{--no-verbose} (default \texttt{--verbose}).
All other parameters of \texttt{filter\_admm\_compliance\_tv} (filter
constants, restoration caps, tolerances) keep their in-file defaults; for
those, use the programmatic interface below.
```

This paragraph is placed where it interrupts the `python3 …`/programmatic
flow naturally, and the sentence "for those, use the programmatic
interface below" hands off cleanly to the existing `from FilterADMM
import …` block.

## Verification

1. **Regression** (defaults unchanged):
   ```bash
   conda activate RASC
   python3 FilterADMM.py
   ```
   Expected: byte-identical run to the previous self-test apart from the
   banner line, which now reads `FilterADMM self-test: 30 x 10
   cantilever, 40% volume fraction` (the literal `30`, `10`, `40` come
   from the defaults rather than from hard-coded strings — output text
   is the same).

2. **CLI sanity**:
   ```bash
   python3 FilterADMM.py --help
   ```
   Expected: argparse help screen lists all seven flags with their
   defaults.

3. **Override path**:
   ```bash
   python3 FilterADMM.py --nelx 20 --nely 8 --volfrac 0.3 --no-plot
   ```
   Expected: banner says `20 x 8 cantilever, 30% volume fraction`; no
   PDFs written to `images/`; trajectory still printed; runs to
   completion.

4. **Bool toggling**:
   ```bash
   python3 FilterADMM.py --no-verbose
   ```
   Expected: banner + summary block still print (those don't honour
   `verbose`), but the per-iteration trajectory lines are suppressed.
   PDFs still written (plot default unchanged).

5. **LaTeX still compiles**:
   ```bash
   pdflatex RASC-MeetingNotes.tex
   ```
   Expected: builds clean, page count grows by ≤ 1.

## Out of scope

- Exposing filter constants `(β, γ, σ, U)` or solver caps on the CLI —
  user spec is the seven flags above only.
- Adding a `--budget` flag — explicitly excluded; budget is always
  derived from `volfrac`.
- Updating `admm.py` or `admm_walkthrough.ipynb` similarly — neither was
  asked for.
- Updating `STATUS.md` / `LOGBOOK.md` — done at end of session per
  project convention, not as part of this plan.

---

## Post-implementation notes (added 2026-05-14 after the run)

The implementation matched the plan exactly — no divergences worth
calling out. All five verification steps passed:

1. **Regression**: defaults reproduce the previous self-test exactly —
   26 outer iters, 3 restorations, `η=1.614e-4`, `ω=6.729e-3`,
   `F=331.34`, sum(x*)=120 (=0.4·300).
2. **`--help`**: argparse renders all seven flags with their defaults
   and the `--plot|--no-plot` / `--verbose|--no-verbose` toggle pairs
   from `BooleanOptionalAction`.
3. **Override**: `--nelx 20 --nely 8 --volfrac 0.3 --no-plot
   --no-verbose` ran to convergence in 17 outer iters; banner reads
   `20 x 8 cantilever, 30% volume fraction`; sum(x*)=48 (=0.3·160)
   confirms the `volfrac → budget` derivation. No PDFs written.
4. **Bool toggling**: `--no-verbose` suppresses the per-iteration
   trajectory lines while keeping the banner + summary block.
5. **LaTeX**: builds clean to 10 pages (was 9, +1 within the plan
   budget). The over/underfull-box warnings in the log are all in
   pre-existing content (lines 237, 314, 418–420, 506–508 — the last
   is the pre-existing `sloppypar` block, untouched).
