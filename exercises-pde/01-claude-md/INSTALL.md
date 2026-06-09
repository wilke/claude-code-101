# Exercise 01- PDE — install instructions

This exercise runs inside a Docker container so you don't have to build Firedrake from source. **Install Docker first, then pull and run the official Firedrake Jupyter image with this folder bind-mounted in.** Total install time on a fresh machine: ~5–15 minutes (most of it is the image pull).

This is the only supported path. Native Firedrake installs are possible but slow (a source build takes 30+ minutes and requires a working PETSc/MPI toolchain), and we don't want that to be anyone's first contact with the workshop.

---

## Step 1 — Install Docker

Pick the installer for your OS:

- **macOS** — [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/) (Apple Silicon or Intel).
- **Windows** — [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/) (uses WSL 2; the installer enables it for you).
- **Linux** — [Docker Engine](https://docs.docker.com/engine/install/) (pick your distro from the list).

Verify after install:

```
docker --version
docker run --rm hello-world
```

The `hello-world` run prints a short success message. If it fails, Docker isn't ready yet — on macOS/Windows, make sure Docker Desktop is actually running (the whale icon should be in your menu bar / system tray).

---

## Step 2 — Pull and run the Firedrake Jupyter image

The official image is `firedrakeproject/firedrake`. It bundles a complete Firedrake install . Pull it once:

```
docker pull firedrakeproject/firedrake:latest
```

This is a large image (~3 GB compressed). Pull it on a decent connection before the workshop, not during.

Then, **from inside this exercise folder**, run the container with your folder bind-mounted in and Jupyter's port forwarded to your host:

```
cd /path/to/exercises-pde/01-claude-md
docker run -it --rm \
    -v "$PWD":/home/firedrake/work \
    -w /home/firedrake/work \
    firedrakeproject/firedrake:latest
```

What this does:
- `-v "$PWD":/home/firedrake/work` — bind-mounts your current folder into the container at `/home/firedrake/work`. **Edits made on either side appear immediately on the other.** This is how Claude Code (running on your host) and Firedrake (running in the container) share files.
- `-w /home/firedrake/work` — starts us in the mounted folder, no need to change directories.


To stop the container, press `Ctrl-C` in the terminal you started it in. The `--rm` flag means the container is removed automatically; only the image stays cached.

---

## Step 3 — Verify the install

Type:
```
vi verify.py
```
*--you can also use any other editor you would like to. Just make sure you have a test .py file--*

**Then type the letter `i` for input.** Copy the following into your terminal.

```
import firedrake as fd
mesh = fd.UnitSquareMesh(8, 8)
V = fd.FunctionSpace(mesh, "CG", 1)
print("Number of DOFs:", V.dim())
```

**Hit `esc`, then type `:wq`**

Finally, run your verification test:

```
python3 verify.py
``` 

You should see a Firedrake version string and the number of **degrees of freedom (DOFs)** (81 for an 8×8 mesh with P1 elements). No errors.

Then, **from the host (not the container)**, edit a file in this folder — open `INSTALL.md` in any editor and save it. Confirm the change is visible inside the container by running, in a Jupyter terminal:

```
ls -la INSTALL.md
```

The `mtime` should reflect your save. This confirms the bind-mount is round-tripping correctly, which is what makes the rest of the exercise possible.

---

## Where Claude Code runs

**Run Claude Code on your host, not inside the container.** Two reasons:

1. The `claude` first-time auth flow opens a browser. That's awkward inside a container.
2. Claude Code is happiest when it can read and write files directly. With a host install plus the bind-mount above, edits Claude makes on the host are immediately visible to commands run inside the container.

Pattern: `claude` on the host edits the Python files; you re-run in Docker container to see the changes.
