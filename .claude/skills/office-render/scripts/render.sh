#!/usr/bin/env bash
# Render slides/pages of an Office document to PNG images via LibreOffice + poppler.
#
# Usage:
#   render.sh INPUT [--pages LIST] [--dpi N] [--out DIR]
#
#   INPUT        .pptx .ppt .odp .docx .doc .odt .xlsx (anything LibreOffice opens)
#   --pages LIST comma list and/or ranges, 1-based: "5", "5,16,34", "1-10", "1-3,20"
#                (default: all pages)
#   --dpi N      raster resolution (default: 150)
#   --out DIR    output directory (default: a temp dir, path printed at the end)
#
# Prints one PNG path per rendered page. Exit 3 if a dependency is missing.
set -euo pipefail

die() { echo "render.sh: $*" >&2; exit 1; }

# ---- dependencies ---------------------------------------------------------
find_soffice() {
  if command -v soffice >/dev/null 2>&1; then command -v soffice; return; fi
  for p in \
    "/Applications/LibreOffice.app/Contents/MacOS/soffice" \
    "/usr/bin/soffice" "/usr/local/bin/soffice" "/opt/homebrew/bin/soffice"; do
    [ -x "$p" ] && { echo "$p"; return; }
  done
  return 1
}

SOFFICE="$(find_soffice || true)"
if [ -z "${SOFFICE:-}" ]; then
  cat >&2 <<'EOF'
render.sh: LibreOffice ('soffice') not found — it is the OOXML renderer.
Install it:
  macOS:  brew install --cask libreoffice
  Debian: sudo apt-get install -y libreoffice
EOF
  exit 3
fi
if ! command -v pdftoppm >/dev/null 2>&1; then
  cat >&2 <<'EOF'
render.sh: 'pdftoppm' (poppler) not found — needed to split the PDF into per-page PNGs.
Install it:
  macOS:  brew install poppler
  Debian: sudo apt-get install -y poppler-utils
EOF
  exit 3
fi

# ---- args -----------------------------------------------------------------
INPUT=""; PAGES=""; DPI=150; OUTDIR=""
while [ $# -gt 0 ]; do
  case "$1" in
    --pages) PAGES="$2"; shift 2 ;;
    --dpi)   DPI="$2"; shift 2 ;;
    --out)   OUTDIR="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    -*) die "unknown option: $1" ;;
    *) [ -z "$INPUT" ] && INPUT="$1" || die "unexpected argument: $1"; shift ;;
  esac
done
[ -n "$INPUT" ] || die "no input file (usage: render.sh INPUT [--pages LIST] [--dpi N] [--out DIR])"
[ -f "$INPUT" ] || die "input not found: $INPUT"
[ -n "$OUTDIR" ] || OUTDIR="$(mktemp -d "${TMPDIR:-/tmp}/office-render.XXXXXX")"
mkdir -p "$OUTDIR"

base="$(basename "$INPUT")"; stem="${base%.*}"
work="$(mktemp -d "${TMPDIR:-/tmp}/office-render-work.XXXXXX")"
trap 'rm -rf "$work"' EXIT

# ---- convert to PDF (isolated profile so it works even if LO is open) -----
"$SOFFICE" --headless --norestore \
  "-env:UserInstallation=file://$work/loprofile" \
  --convert-to pdf --outdir "$work" "$INPUT" >/dev/null 2>&1 || die "LibreOffice conversion failed"
pdf="$work/$stem.pdf"
[ -f "$pdf" ] || die "expected PDF not produced: $pdf"

npages="$(pdftoppm -png -r 10 "$pdf" "$work/probe" >/dev/null 2>&1; ls "$work"/probe-*.png 2>/dev/null | wc -l | tr -d ' ')"

emit() { # render a single 1-based page number
  local p="$1"
  pdftoppm -png -r "$DPI" -f "$p" -l "$p" "$pdf" "$OUTDIR/$stem" >/dev/null 2>&1 || return 0
  ls "$OUTDIR/$stem"-*"$p".png 2>/dev/null | tail -1
}

if [ -z "$PAGES" ]; then
  pdftoppm -png -r "$DPI" "$pdf" "$OUTDIR/$stem" >/dev/null 2>&1
  ls "$OUTDIR/$stem"-*.png 2>/dev/null | sort
else
  IFS=',' read -ra toks <<< "$PAGES"
  for tok in "${toks[@]}"; do
    tok="$(echo "$tok" | tr -d ' ')"
    if [[ "$tok" == *-* ]]; then
      a="${tok%-*}"; b="${tok#*-}"
      for ((p=a; p<=b; p++)); do emit "$p"; done
    else
      emit "$tok"
    fi
  done
fi

echo "render.sh: rendered from $base (${npages:-?} pages) -> $OUTDIR" >&2
