# Exercise 04 — Bootstrap MEMORY.md from notebook entries (10 min)

**Goal.** Use Claude Code to turn loose lab notebook/plans entries into a structured `MEMORY.md`. The synthesis is the pretext; **the file is the artifact** — how the next session inherits what this one learned.

> **`MEMORY.md` isn't limited to `.md`.** Claude can read almost any file — `.py` source, `.tex` notes, plans — so you can distill an entire multi-format project into one memory file, not just a set of markdown notebooks.

**Background** These are actual plans from a project that is briefly described next (skip to **Exercise Steps** to start the exercise). The project tried to implement an ADMM filter method for topology optimization.

## What's here (abbreviated)
```
  04-memory/
  ├── README.md
  ├── SOLUTION.md
  ├── plans/
  │   ├── 2026-05-08-filter.md
  │   ├...
  │   └── 2026-06-03-movie.md
  ├── src/
  │   ├── FilterADMM.py
  │   ├...
  │   └── reciprocal_approx.py
  └── tex/
      ├── algorithm.tex
      ├── proximal_gradient_note.tex
      ├── RASC-MeetingNotes.tex
      └── reciprocal_algorithm.tex
```

## ADMM Topology Optimization

Solves the compliance minimization problem with Total Variation regularization:

```
min  F(x) + α · TV(x)
s.t. sum(x) ≤ Budget,   x ∈ [ε, 1]^n
```

`F(x)` is the structural compliance of a 2D cantilever beam (computed via finite element analysis), and `TV(x)` is a graph total variation regularizer that promotes spatial smoothness of the density field. The design variable `x` represents element densities using the SIMP material model.

## Exercise Steps
1. Move the necessary files into your sandbox.

2. Ask:

   ```
   read everything under plans/, src/, and tex/ and produce MEMORY.md
   with the sections: Decisions, Parameters, Dead Ends, Open Questions.
   Each entry should cite the file it came from.
   ```

   (Note that Claude reads the `.py` source and `.tex` notes alongside the `.md` plans — the whole project, not just the markdown.)

3. **Review and trim.** It will be too long. For each line, ask: *would a future-me on a different session actually consult this?* Cut everything that's just "what happened that day." Edit ruthlessly — the trimmed file is what your next session reads on load.

4. Create a `CLAUDE.md` file.

5. Now, with the new `MEMORY.md` and `CLAUDE.md` in place, ask:

   ```
   given MEMORY.md and CLAUDE.md, what would be the most informative 
   next experiment to run? Justify in two sentences.
   ```

   The answer should reference at least one specific entry.

6. End the session with the two-minute ritual:

   ```
   summarize what we did in this session, append it as a dated entry to
   MEMORY.md (under Decisions or Open Questions, whichever fits, noting
   that MEMORY.md was edited and CLAUDE.md created), and overwrite
   STATUS.md with where we are now.
   ```

   The MEMORY.md append should name a concrete decision or question, not the activity. STATUS.md should be tight enough that the next session can pick up from it without reading anything else first.

## Critical-reading checklist

| Look for | Why it matters |
|----------|----------------|
| Did every entry cite its source file (`plans/`, `src/`, or `tex/`)? | An entry you can't trace back is one you can't revise. |
| Did Claude actually trim, or is `MEMORY.md` longer than the source files? | Synthesis without trimming is just retyping. |
| Did Dead Ends keep the *reason* a path was abandoned, not just the verdict? | A verdict alone doesn't stop a re-attempt. |
| Did the next-experiment answer cite a specific entry? | If it doesn't, it could've been written without the file. |
| Did the end-of-session append name a decision, not the activity? | "We discussed MEMORY.md" decays to nothing. |
| Did Claude surface conflicts between plan files, or smooth them over? | A hidden conflict destroys the most important information. |

## Discussion prompts

- What goes in CLAUDE.md vs MEMORY.md? (Hint: stable conventions vs evolving facts.)
- How would you index a MEMORY.md that grows past 200 lines?
- What is the point of the LaTeX files?

## Stretch (if time permits)

**1. Split MEMORY.md into a directory:** `memory/decisions.md`, `memory/parameters.md`, `memory/dead-ends.md`, plus a `memory/INDEX.md`. Ask Claude to maintain the index automatically when it appends new entries.

**2. Run the project.** Everything above works from *reading* the files; if you want to see the code actually run, set up an environment and drive `FilterADMM`.

Runtime dependencies (also listed in `requirements.txt`):

| Package | Used by |
|---------|---------|
| `numpy` | all modules |
| `scipy` | `reciprocal_approx.py` (Brent root-finding), `compliance.py` (sparse linear algebra), `graph_tv.py` (sparse incidence matrix), `projection.py` |
| `matplotlib` | `generate_notebook.py` only (notebook plots) |

Work in a virtual environment so the exercise's packages stay isolated from your
system Python and don't clash with other projects. Create and activate it
**before you start `claude`** — Claude runs Python itself, so it uses whichever
environment is active. Use conda or pip + venv, whichever you prefer. **On
Windows, conda or the ANL compute nodes are recommended** — native venv
activation differs (`.venv\Scripts\activate`). Feel free to run on your own
machine if that doesn't worry you.

conda:

```bash
conda create -n RASC python=3.11 -y
conda activate RASC
pip install -r requirements.txt
```

pip + venv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

After setup, all subsequent commands assume the env is active (re-activate it in each new shell).

`FilterADMM.py` is the recommended driver for this problem. It implements the
double-loop ADMM-Filter algorithm of `RASC-MeetingNotes.tex` §3.5 with
adaptive `ρ`. On the 30×10 default it converges in ~14 outer iterations,
where the fixed-`ρ` baseline `admm.py` does not converge in 30 iterations.

Self-test on the 30×10 default (fastest sanity check):

```bash
cd src/
conda activate RASC
python3 FilterADMM.py
```

**3. Try a larger mesh and fix it.** The 120×40 mesh will fail to converge — can you diagnose and fix it (this could be a capstone! *If you do this as a capstone, then make sure to add Dominic Yang as a co-author!*)?

```bash
cd src/
python3 FilterADMM.py --help                              # list options
python3 FilterADMM.py --nelx 60 --nely 20                 # larger mesh
python3 FilterADMM.py --nelx 120 --nely 40                # fails — diagnose and fix
```
