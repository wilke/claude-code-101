# Capstone — install instructions

Three install paths. **For the workshop, pick path A or B.** Path C is for long-running research where reproducibility matters more than first-contact friction.

| Path | Time to first command | PETSc backend? | When to pick |
|---|---|---|---|
| A. Native pip (numpy only) | ~2 min | No (numpy fallback) | You want to skim the capstone; PETSc is overkill. |
| B. Native conda (recommended) | ~5 min | Yes (prebuilt) | You want the full PETSc/TAO experience without a compiler adventure. |
| C. Docker container | ~10 min | Yes (image-baked) | Long-term reproducibility, multi-machine consistency, or a workshop instructor handing out a fixed environment. |

All paths support all the workshop conventions (CLAUDE.md, plans/, MEMORY.md, STATUS.md, the kkt-checker skill). The only difference is whether the PETSc/TAO backend is available.

---

## Path A — native pip, numpy backend

Smallest install. Runs everything in the capstone except `--backend petsc`.

```
cd exercises/06-capstone
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

Verify:

```
python poisson_inverse.py --check-grad           # adjoint vs. finite diff
python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-5
pytest -q                                         # tests pass
```

You should see the gradient check rel-error around `1e-10` and a JSON summary written under `runs/`.

---

## Path B — native conda, full PETSc backend (recommended)

Uses conda-forge's prebuilt PETSc and petsc4py. No compiler, no MPI install, no source build.

Prerequisite: a conda flavour. Any one of these works:

- [Miniforge](https://github.com/conda-forge/miniforge) (recommended — community-maintained, conda-forge by default)
- Miniconda with the conda-forge channel added
- Mambaforge (Miniforge with `mamba` for faster solves)

Then:

```
cd exercises/06-capstone
conda env create -f environment.yml         # or: mamba env create -f environment.yml
conda activate claude-capstone
```

Verify (numpy backend first, then PETSc):

```
python poisson_inverse.py --check-grad
python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-5

python -c "from petsc4py import PETSc; print('PETSc', PETSc.Sys.getVersion())"
# Expected: a version tuple like (3, 20, 4) and no errors.

pytest -q
```

If `from petsc4py import PETSc` fails, you almost certainly created the env outside the `conda-forge` channel. Re-run:

```
conda env remove -n claude-capstone
conda env create -f environment.yml --override-channels -c conda-forge
```

---

## Path C — Docker container

For when you want the whole environment baked in and reproducible across machines. Best fit: workshop instructors who don't want to debug PETSc installs in front of an audience, and researchers who need long-term reproducibility.

The repo doesn't ship a workshop-specific image — the standard PETSc images are good enough. Pull one:

```
docker pull pflotran/pflotran:latest
# or pull anything else that bundles petsc4py; substitute below.
```

Run an interactive shell with the workshop folder mounted:

```
cd /path/to/Claude Code Tutorial or Hackathon
docker run -it --rm \
    -v "$PWD":/workspace \
    -w /workspace/exercises/06-capstone \
    pflotran/pflotran:latest \
    bash
```

Inside the container:

```
pip install -r requirements.txt   # adds pytest etc. to the image's Python
python poisson_inverse.py --check-grad
python poisson_inverse.py --backend numpy --grid 33 --alpha 1e-5
pytest -q
```

### Where Claude Code runs

**Run Claude Code on the host, not inside the container.** Two reasons:

1. The `claude` first-time auth flow opens a browser. That's awkward inside a container. Workarounds exist (paste a token, use `--print`) but they're extra friction for a workshop.
2. Claude Code is happiest when it can read and write files directly. With a host install plus `-v $PWD:/workspace`, edits Claude makes on the host are immediately visible to commands run in the container.

Pattern: `claude` on the host edits code; commands that need PETSc run inside the container. You can tell Claude this in CLAUDE.md:

```markdown
## Commands
- Numerical runs go inside the container:
    docker compose run --rm capstone python poisson_inverse.py [...]
- Tests run inside the container:
    docker compose run --rm capstone pytest -q
- Plotting and small numpy-only checks can run on the host.
```

Optional: a `docker-compose.yml` makes the above one-liner work. Sketch:

```yaml
services:
  capstone:
    image: pflotran/pflotran:latest
    working_dir: /workspace/exercises/06-capstone
    volumes:
      - ./:/workspace
```

---

## Recommendation for the workshop

If you have ~15 minutes before the workshop and want to do the full capstone: **Path B**.
If you have 2 minutes and want to skim: **Path A**.
If you're an instructor running the workshop on a fresh laptop and want the install to be a non-event: **Path C**, with the image pulled in advance.

If `pip install petsc petsc4py` is what your fingers want to type, it does work on Linux and macOS — it just builds PETSc from source (10–30 min) and asks for a C compiler, BLAS/LAPACK, and MPI to be present. Skip it for the workshop. For long-term use, Path B and Path C are both lower-effort.
