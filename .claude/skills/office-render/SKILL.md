---
name: office-render
description: >-
  Render slides or pages of Office documents (.pptx, .ppt, .odp, .docx, .doc,
  .odt, .xlsx) to PNG images for visual inspection, using LibreOffice headless
  plus poppler. Use this WHENEVER you need to actually SEE what a PowerPoint,
  slide deck, or Word/Excel document looks like — verifying a generated or edited
  .pptx, previewing specific slides, checking layout/overflow/branding, comparing
  before/after, or turning a deck into thumbnails. Reach for this instead of
  `qlmanage` (which only renders the first slide) any time the task involves
  eyeballing more than page one of an Office file.
---

# Office render

Rasterize any page/slide of a LibreOffice-openable document to PNG so it can be
viewed with the Read tool. The pipeline is **LibreOffice → PDF → poppler → PNG**,
which is the only reliable way to get *every* slide (`soffice --convert-to png`
and macOS `qlmanage` both emit the first slide only).

## When to use

- You generated or edited a `.pptx` and need to confirm it looks right.
- You need specific slides (e.g. "show me slides 5, 16, 34") as images.
- You want to check overflow, alignment, colors, fonts, or logos on a deck.
- Any "let me see the deck / render the slides / make thumbnails" request.

## Prerequisites (one-time install)

The skill shells out to two tools. If either is missing, `render.sh` exits with
code 3 and prints the install command. Install them once:

```bash
# macOS
brew install --cask libreoffice   # the OOXML renderer (soffice)
brew install poppler              # pdftoppm / pdftocairo — splits PDF into PNGs

# Debian/Ubuntu
sudo apt-get install -y libreoffice poppler-utils
```

## Usage

Run the bundled script, then Read the PNG paths it prints.

```bash
bash .claude/skills/office-render/scripts/render.sh INPUT [--pages LIST] [--dpi N] [--out DIR]
```

- `INPUT` — the document (`.pptx`, `.docx`, `.xlsx`, `.odp`, …).
- `--pages LIST` — 1-based, comma list and/or ranges: `5` · `5,16,34` · `1-10` · `1-3,20`.
  Omit to render **all** pages.
- `--dpi N` — resolution (default `150`; use `200`+ for fine text, `100` for quick thumbnails).
- `--out DIR` — output directory (default: a fresh temp dir; the path is printed to stderr).

The script prints one PNG path per rendered page on stdout. Read those paths to view them.

### Examples

```bash
# All slides of a deck at 150 dpi
bash .claude/skills/office-render/scripts/render.sh slides-argonne.pptx

# Just a few slides, higher resolution, into /tmp/ql
bash .claude/skills/office-render/scripts/render.sh slides-argonne.pptx \
  --pages 1,5,16,34,50 --dpi 200 --out /tmp/ql
```

Typical loop when verifying a generated deck:

1. Build/edit the `.pptx`.
2. `render.sh deck.pptx --pages <the ones you changed>`.
3. Read the printed PNGs; fix issues; repeat.

## Notes

- LibreOffice is invoked with an isolated `-env:UserInstallation` profile, so it
  works even if a LibreOffice window is already open.
- First run can be slow (LibreOffice cold start, several seconds); later runs are faster.
- Rendering fidelity is LibreOffice's, not PowerPoint's — very close for typical
  decks, but exotic effects/transitions may differ. For pixel-exact PowerPoint
  output, open the file in PowerPoint.
