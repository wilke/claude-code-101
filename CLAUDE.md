# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**"Files, not chats"** — a hands-on workshop teaching Claude Code to mathematicians (nonlinear / discrete / PDE-constrained optimization). It is a **content repository**, not an application: a slide deck, three parallel exercise tracks, capstone project briefs, and companion docs. There is no server to run and no repo-level test suite — "building" means regenerating the decks, and "verifying" means viewing them.

## Git workflow: always use a feature branch (hard rule)

**Never commit or push directly to `main`.** For every change — including generated files, docs, slides, and exercises:

1. `git fetch origin && git checkout -b <type>/<slug> origin/main` (types: `feat/`, `fix/`, `docs/`, `chore/`)
2. Commit on the branch, then `git push -u origin <branch>`
3. Open a PR (`gh pr create --fill`); merge only via the PR.

Gotcha: `gh pr edit` fails on this repo with a *"Projects (classic) is being deprecated"* GraphQL error. Edit a PR's title/body via the REST API instead:
`gh api -X PATCH repos/wilke/claude-code-101/pulls/<N> -f title=… -f body=…`.

## The slide deck is GENERATED — edit markdown, never the HTML

`docs/slides/*.md` is the **single source of truth** for the main deck. Two generators render that one source through a shared parser, so a content change means editing the markdown and rebuilding:

- **`scripts/slides_md.py`** — the shared markdown parser (produces a typed block model). Both generators import it.
- **`scripts/build_html.py`** → **`slides.html`** — the Argonne-themed browser deck. It is generated **but committed** (GitHub Pages serves it; `index.html` redirects to it). Regenerate after any markdown edit — do **not** hand-edit `slides.html`, changes are overwritten.
- **`scripts/build_pptx.py`** → **`slides-argonne.pptx`** — a PowerPoint on the Argonne template (via `python-pptx`). Git-ignored (branded binary); ship it to the user directly.
- `archive/slides-classic.html` — the retired serif-themed deck, kept for reference only (not a build input).

Build via the Makefile:

```bash
make html          # slides.html from docs/slides/*.md
make pptx          # slides-argonne.pptx
make slides        # both
make preview       # serve at http://localhost:8117/slides.html
make contact-sheet # 50-slide QA grid PNG (needs LibreOffice + poppler)
```

Dependencies: `pip install python-pptx pillow`. Both generators need the Argonne `.potx` template — auto-discovered at `templates/Argonne_16x9_template.potx` or `~/Downloads/Argonne_16x9 Presentation Template.potx`, else pass `--template PATH` or set `ARGONNE_TEMPLATE`. `templates/*.potx` and `*.pptx` are git-ignored (Argonne-branded binaries).

### Slide source format & the block model

Each slide is an HTML-comment header plus clean markdown; see `docs/slides/INDEX.md` for the authoritative spec and the file→slide map. Shape:

```
<!--slide n=8 layout=content kicker="Session basics"-->
# Title
_optional lede_
… bullets / numbered / fenced code / pipe tables / > callouts / :::columns …
```

- `layout` ∈ `title | section | content | closing`, mapping to the Argonne template's *Title Slide* / *Section Break* / *Title and Subtitle* / (closing rendered as a section divider).
- The **HTML deck** treats each slide as a fixed 1180×664 canvas: a script scales the whole deck to fill the viewport (text scales with it), shrinks any dense slide's content to fit (`.fit` wrapper), and supports full-screen (`f` key / ⛶ button). The **PPTX** renders static equivalents and shrinks dense slides by scaling fonts.
- **Adding or changing a block type requires touching all three files**: parse it in `slides_md.py`, then render it in `build_html.py` (HTML) and `build_pptx.py` (PPTX shapes). Keep them in lockstep or the two decks diverge.

## Verifying a deck visually

`qlmanage` and `soffice --convert-to png` only rasterize the **first** slide. Use the bundled **`office-render`** skill (LibreOffice headless → PDF → poppler → PNG) to render arbitrary slides:

```bash
bash .claude/skills/office-render/scripts/render.sh slides-argonne.pptx --pages 5,16,34 --dpi 150
bash .claude/skills/office-render/scripts/render.sh slides-argonne.pptx --contact-sheet
```

Requires `brew install --cask libreoffice && brew install poppler`. For the HTML deck, `make preview` and open it; the active slide lives in the URL hash (`#34`), and `show(n)` / `.slide.active` are usable from the console.

## Other structure worth knowing

- **Exercises** — three parallel tracks (`exercises-opt/`, `exercises-pde/`, `exercises-lin_alg/`), each with the same numbered progression `01-claude-md` … `04-memory`; only the optimization track adds `06-capstone`. Each folder is opened on its own (`cd … && claude`) with steps in its `README.md`. A track's `SOLUTION.md` is deliberately kept **out of** the directory where `claude` runs so the model can't read ahead — preserve that when editing exercises. Exercise Python deps: `numpy scipy matplotlib pytest`.
- **Capstones** — `capstones/<Name>/README.md` are open-ended project briefs; `capstones/README.md` is the shared index + per-project setup instructions. The capstone slide is generated from that list.
- **`versions/`** — frozen snapshots of tagged deck releases (`v0.9.0`, `v0.9.1`) with an `index.html` picker; the current deck is served from the repo root.
- **`slides-supplemental/`** — the intro deck and per-track supplement decks. These are **hand-authored** standalone HTML (NOT generated from the markdown pipeline).
- **Companion docs** referenced by the deck: `WORKFLOW.md`, `LITERATURE.md`, `docs/native-claude-code-mapping.md` (how the workshop's four-file architecture maps to Claude Code's built-ins), and `docs/logbook-to-adrs.md` (how `LOGBOOK.md` scales: one file → a `logbook/` directory → a `decisions/` directory of ADRs). Note: the durable-knowledge file is `LOGBOOK.md` — renamed from `MEMORY.md` to avoid colliding with Claude Code's native auto-memory `MEMORY.md`.
- **`scratchpad.md`** is a git-ignored working-memory notebook.
