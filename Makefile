# Build the workshop slide decks.
#
# Single source of truth (edit these):
#   docs/slides/*.md             – markdown ground truth for BOTH decks
#
# Generated outputs:
#   slides.html                  – Argonne-themed browser deck (served by GitHub Pages)
#   slides-argonne.pptx          – Argonne PowerPoint (git-ignored)
#
# (archive/slides-classic.html is the retired serif deck, kept for reference only.)
#
# Both generators need the Argonne template; they auto-find it at
# templates/Argonne_16x9_template.potx or ~/Downloads/, or pass ARGONNE_TEMPLATE=…

PY ?= python3
PORT ?= 8117

.DEFAULT_GOAL := help
.PHONY: all slides html pptx contact-sheet preview clean help

all: slides                ## build both decks (HTML + PowerPoint)
slides: html pptx

html:                      ## build slides.html (Argonne theme) from docs/slides/*.md
	$(PY) scripts/build_html.py

pptx:                      ## build slides-argonne.pptx from docs/slides/*.md
	$(PY) scripts/build_pptx.py

contact-sheet: pptx        ## render a 50-slide QA contact sheet (needs LibreOffice + poppler)
	bash .claude/skills/office-render/scripts/render.sh slides-argonne.pptx \
	    --contact-sheet --dpi 96 --out /tmp/contact
	@echo "contact sheet -> /tmp/contact/contact-sheet.png"

preview:                   ## serve the repo at http://localhost:$(PORT) (open /slides.html)
	@echo "serving http://localhost:$(PORT)/slides.html  (Ctrl-C to stop)"
	$(PY) -m http.server $(PORT)

clean:                     ## remove the generated PowerPoint (slides.html is committed)
	rm -f slides-argonne.pptx

help:                      ## list targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \
	  | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n",$$1,$$2}'
