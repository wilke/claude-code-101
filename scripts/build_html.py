#!/usr/bin/env python3
"""Build slides.html — the workshop browser deck on the Argonne 16x9 template
(white base slide with the blue left bar, Arial, Argonne-blue titles, gold
section eyebrows, DOE + Argonne logos, scale-to-fill + full-screen).

Rendered from the SAME source as the PowerPoint: the markdown ground truth in
docs/slides/*.md (parsed by slides_md.py). This is the single source of truth —
edit the markdown, then rebuild both decks with `make`.

Usage:
    python scripts/build_html.py [--template PATH] [--slides DIR] [--out OUT.html]
    # defaults: --slides docs/slides  --out slides.html
"""
from __future__ import annotations

import argparse
import base64
import html as htmllib
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slides_md import (  # noqa: E402  shared markdown parser (single source of truth)
    column_is_links, load_all_slides,
)

REPO = Path(__file__).resolve().parent.parent
SLIDES_DIR = REPO / "docs" / "slides"
TEMPLATE_CANDIDATES = [
    os.environ.get("ARGONNE_TEMPLATE", ""),
    str(REPO / "templates" / "Argonne_16x9_template.potx"),
    str(Path.home() / "Downloads" / "Argonne_16x9 Presentation Template.potx"),
]
# media file names inside the template package
ARGONNE_LOGO = "ppt/media/image1.png"   # Argonne wordmark (bottom-right)
DOE_LOGO = "ppt/media/image2.png"       # DOE seal + tagline (bottom-left)


def find_template() -> Path | None:
    for c in TEMPLATE_CANDIDATES:
        if c and Path(c).exists():
            return Path(c)
    return None


def data_uri(potx: Path, member: str) -> str:
    with zipfile.ZipFile(potx) as z:
        raw = z.read(member)
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def argonne_css(doe_uri: str, argonne_uri: str) -> str:
    return f"""
  :root {{
    --bg: #ffffff;
    --ink: #1c1c1c;
    --muted: #5b5b5b;
    --accent: #00609c;        /* Argonne dark blue */
    --accent-bright: #0082ca; /* Argonne primary blue */
    --gold: #f8b200;
    --accent-soft: #dbe7f2;   /* light blue: callout bg / light text on blue */
    --rule: #cdd8e2;
    --code-bg: #eef2f6;
    --code-ink: #1c1c1c;
    --bar: #00609c;
    --serif: Arial, "Helvetica Neue", Helvetica, sans-serif;
    --sans: Arial, "Helvetica Neue", Helvetica, sans-serif;
    --mono: "Consolas", "SF Mono", "Cascadia Mono", Menlo, monospace;
    --divider: linear-gradient(135deg, #0082ca 0%, #00609c 55%, #004a7a 100%);
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ height: 100%; margin: 0; padding: 0; background: #e9edf1; color: var(--ink); font-family: var(--serif); }}
  body {{ display: flex; align-items: center; justify-content: center; overflow: hidden; }}
  body.presenting {{ background: #0d1117; }}  /* dark backdrop in full-screen */
  /* Fixed 16:9 design canvas; a script scales the whole deck to fill the
     viewport (windowed or full-screen), so text scales with it — no gray cap. */
  #deck {{
    position: relative;
    width: 1180px;
    height: 664px;
    flex: 0 0 auto;
    transform-origin: center center;
    background: var(--bg);
    box-shadow: 0 2px 14px rgba(0,0,0,0.18);
    overflow: hidden;
  }}
  /* the Argonne blue left bar — present on every slide */
  #deck::before {{
    content: "";
    position: absolute; left: 0; top: 0; bottom: 0; width: 15px;
    background: var(--bar); z-index: 6; pointer-events: none;
  }}
  .slide {{
    position: absolute; inset: 0;
    padding: 46px 64px 70px 72px;
    display: none; flex-direction: column; overflow: hidden;
  }}
  .slide.active {{ display: flex; }}
  /* content wrapper that the fit-to-slide script scales down on dense slides */
  .slide > .fit {{ display: flex; flex-direction: column; width: 100%; transform-origin: top left; }}
  .slide > .fit > pre, .slide > .fit > table.matrix {{ flex-shrink: 0; }}
  .slide h1 {{
    font-family: var(--serif); font-weight: 700;
    font-size: 40px; line-height: 1.12; letter-spacing: -0.005em;
    margin: 0 0 10px; color: var(--accent);
  }}
  .slide h2 {{ font-family: var(--serif); font-weight: 700; font-size: 30px; line-height: 1.2; margin: 0 0 6px; color: var(--accent); }}
  /* content-slide kicker → Argonne blue strip (h3 lives inside .fit after wrapping) */
  .slide h3 {{
    display: inline-block; align-self: flex-start;
    font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.11em;
    font-size: 12px; font-weight: 700; color: #fff;
    background: var(--accent); padding: 6px 13px; border-radius: 2px;
    margin: 0 0 16px;
  }}
  .slide p, .slide li {{ font-size: 20px; line-height: 1.42; }}
  .slide ul, .slide ol {{ padding-left: 1.2em; margin: 0.4em 0 0.6em; }}
  .slide li {{ margin: 0.25em 0; }}
  .slide li::marker {{ color: var(--accent-bright); }}
  .slide code {{ font-family: var(--mono); font-size: 0.9em; background: var(--code-bg); padding: 1px 6px; border-radius: 3px; }}
  .slide pre {{
    font-family: var(--mono); background: var(--code-bg); color: var(--code-ink);
    padding: 16px 20px; border-radius: 4px; font-size: 15px; line-height: 1.45;
    overflow: auto; margin: 8px 0; border-left: 4px solid var(--accent-bright);
  }}
  .slide pre code {{ background: transparent; padding: 0; font-size: inherit; }}
  .slide .lede {{ font-size: 23px; color: var(--muted); margin-top: 0; }}
  .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 28px; margin-top: 8px; }}
  .two-col .col h4 {{ font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.1em; font-size: 11px; color: var(--accent); margin: 0 0 8px; }}
  .callout {{
    border-left: 4px solid var(--accent-bright); background: var(--accent-soft);
    padding: 12px 16px; margin: 12px 0; font-size: 18px; line-height: 1.45; color: #143a5a;
  }}
  .exlinks {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px 28px; margin: 16px 0 4px; }}
  .exlinks .col h4 {{ font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.1em; font-size: 11px; color: var(--accent); margin: 0 0 8px; }}
  .exlinks a {{ display: block; font-family: var(--mono); font-size: 14px; line-height: 1.5; color: var(--accent-bright); text-decoration: none; border-bottom: 1px solid transparent; width: fit-content; }}
  .exlinks a:hover {{ border-bottom-color: var(--accent-bright); }}
  /* section / exercise dividers → Argonne blue */
  .section-divider {{ background: var(--divider); color: #fff; }}
  .section-divider h1 {{ color: #fff; font-size: 60px; }}
  .section-divider .kicker {{ font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.18em; font-size: 13px; color: var(--gold); font-weight: 700; }}
  .section-divider .lede {{ color: #eaf2f8; }}
  .section-divider .exlinks {{ max-width: 860px; margin-top: 20px; }}
  .section-divider .exlinks .col h4 {{ color: var(--gold); }}
  .section-divider .exlinks a {{ color: #eaf2f8; }}
  .section-divider .exlinks a:hover {{ border-bottom-color: #eaf2f8; }}
  /* capstone showcase: all titles in the left column, rotating description on the right */
  .caps-rotator {{ display: grid; grid-template-columns: 0.85fr 1.15fr; gap: 14px 46px; margin-top: 22px; align-items: start; }}
  .caps-list {{ display: flex; flex-direction: column; gap: 7px; }}
  .caps-item {{ font-family: var(--sans); font-size: 19px; font-weight: 600; line-height: 1.25; color: var(--muted); cursor: pointer; transition: color 0.3s; }}
  .caps-item.active {{ color: var(--accent); }}
  .section-divider .caps-item {{ color: #a9c7e0; }}
  .section-divider .caps-item.active {{ color: var(--gold); }}
  .caps-desc-panel {{ position: relative; min-height: 150px; }}
  .caps-desc-page {{ position: absolute; inset: 0; opacity: 0; transition: opacity 0.5s ease; pointer-events: none; }}
  .caps-desc-page.show {{ opacity: 1; pointer-events: auto; }}
  .caps-desc-name {{ font-family: var(--sans); font-weight: 700; font-size: 24px; color: var(--accent); margin-bottom: 8px; }}
  .caps-desc-text {{ font-size: 21px; line-height: 1.45; color: var(--muted); }}
  .section-divider .caps-desc-name {{ color: #fff; }}
  .section-divider .caps-desc-text {{ color: #eaf2f8; }}
  /* title slide → white base with blue bar, blue title, gold eyebrow */
  .title-slide {{ justify-content: center; background: var(--bg); }}
  .title-slide .kicker {{ font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.18em; font-size: 13px; color: var(--gold); font-weight: 700; margin-bottom: 18px; }}
  .title-slide h1 {{ font-size: 62px; line-height: 1.04; max-width: 18ch; color: var(--accent); }}
  .title-slide .sub {{ font-size: 22px; color: var(--muted); margin-top: 18px; max-width: 58ch; }}
  /* footer band + logos (DOE left, Argonne right) on every slide */
  .footer {{
    position: absolute; bottom: 14px; left: 72px; right: 40px;
    display: flex; justify-content: space-between; align-items: center;
    font-family: var(--sans); font-size: 11px; color: var(--muted);
    letter-spacing: 0.08em; text-transform: uppercase; pointer-events: none; gap: 16px;
  }}
  .footer::before {{
    content: ""; flex: 0 0 auto; width: 188px; height: 30px;
    background: url("{doe_uri}") no-repeat left center / contain;
  }}
  .footer::after {{
    content: ""; flex: 0 0 auto; width: 104px; height: 30px;
    background: url("{argonne_uri}") no-repeat right center / contain;
  }}
  .section-divider .footer, .section-divider .footer .counter {{ color: #cfe0ee; }}
  /* logo chips stay legible on the blue dividers */
  .section-divider .footer::before, .section-divider .footer::after {{
    background-color: rgba(255,255,255,0.94); border-radius: 4px; padding: 3px 7px;
    background-origin: content-box;
  }}
  .footer .progress {{ flex: 1 1 auto; height: 2px; background: var(--rule); margin: 0 6px; align-self: center; position: relative; }}
  .section-divider .footer .progress {{ background: rgba(255,255,255,0.35); }}
  .footer .progress > div {{ position: absolute; inset: 0 auto 0 0; background: var(--accent-bright); width: 0%; transition: width 200ms ease; }}
  .section-divider .footer .progress > div {{ background: var(--gold); }}
  .footer .counter, .footer > span:first-of-type {{ flex: 0 0 auto; }}
  .nav {{ position: fixed; bottom: 14px; right: 18px; display: flex; gap: 6px; align-items: center; z-index: 10; }}
  .nav button {{ font-family: var(--sans); font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; padding: 6px 10px; background: #fff; color: var(--ink); border: 1px solid var(--rule); cursor: pointer; }}
  .nav button:hover {{ background: var(--accent-soft); }}
  .nav button.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .nav input.jump-to {{ font-family: var(--mono); font-size: 12px; width: 56px; padding: 5px 8px; border: 1px solid var(--rule); background: #fff; color: var(--ink); text-align: center; }}
  .nav input.jump-to:focus {{ outline: 2px solid var(--accent); outline-offset: -2px; }}
  .nav .nav-label {{ font-family: var(--sans); font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.08em; margin-right: 2px; }}
  #help-overlay {{ position: fixed; inset: 0; background: rgba(0,48,87,0.9); color: #fff; display: none; align-items: center; justify-content: center; z-index: 100; font-family: var(--sans); }}
  #help-overlay.show {{ display: flex; }}
  #help-overlay .panel {{ background: #003057; border: 1px solid var(--accent-bright); padding: 28px 36px; max-width: 520px; color: #fff; }}
  #help-overlay h2 {{ font-family: var(--serif); margin: 0 0 14px; color: var(--gold); }}
  #help-overlay table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  #help-overlay td {{ padding: 4px 0; vertical-align: top; }}
  #help-overlay td:first-child {{ color: var(--gold); padding-right: 16px; white-space: nowrap; font-family: var(--mono); }}
  #help-overlay .close-hint {{ margin-top: 14px; font-size: 11px; color: var(--accent-soft); text-transform: uppercase; letter-spacing: 0.1em; }}
  .badge {{ display: inline-block; font-family: var(--sans); text-transform: uppercase; letter-spacing: 0.12em; font-size: 10px; color: #fff; background: var(--accent); padding: 2px 8px; border-radius: 2px; vertical-align: middle; margin-right: 8px; }}
  table.matrix {{ border-collapse: collapse; width: 100%; margin-top: 8px; font-size: 17px; }}
  table.matrix th, table.matrix td {{ border: 1px solid var(--rule); padding: 8px 12px; text-align: left; vertical-align: top; }}
  table.matrix th {{ background: var(--accent); color: #fff; font-family: var(--sans); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; border-color: var(--accent); }}
  table.matrix tr:nth-child(even) td {{ background: #f4f7fa; }}
  .small {{ font-size: 16px; color: var(--muted); }}
  .kbd {{ font-family: var(--mono); font-size: 13px; background: #fff; border: 1px solid var(--rule); border-bottom-width: 2px; padding: 1px 6px; border-radius: 3px; }}
  /* No responsive breakpoints needed: the deck is a fixed 1180x664 canvas
     scaled to fit any viewport, so proportions hold on phone, laptop, and TV. */
"""


FIT_JS = r"""<script>
/* Presentation scaling for the Argonne deck:
   1. deck-fit  — scale the whole 1180x664 canvas to fill the viewport (windowed
      or full-screen) so it goes edge-to-edge with proportional text.
   2. slide-fit — inside the canvas, scale a dense slide's content down so it
      never clips at 16:9. Only ever scales down.
   3. full screen — a ⛶ button and the `f` key toggle the Fullscreen API. */
(function () {
  var deck = document.getElementById('deck');
  if (!deck) return;
  var DES_W = 1180, DES_H = 664;

  // --- wrap every slide's non-footer content so we can scale it ---
  deck.querySelectorAll('.slide').forEach(function (s) {
    if (s.querySelector(':scope > .fit')) return;
    var footer = s.querySelector(':scope > .footer');
    var fit = document.createElement('div');
    fit.className = 'fit';
    Array.prototype.slice.call(s.childNodes).forEach(function (n) {
      if (n !== footer) fit.appendChild(n);
    });
    s.insertBefore(fit, footer || null);
  });

  function fitSlide(s) {
    var fit = s.querySelector(':scope > .fit');
    if (!fit) return;
    fit.style.transform = '';
    var cs = getComputedStyle(s);
    var availH = s.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom);
    var availW = s.clientWidth - parseFloat(cs.paddingLeft) - parseFloat(cs.paddingRight);
    var h = fit.scrollHeight, w = fit.scrollWidth;
    if (!h || !w) return;
    var k = Math.min(1, availH / h, availW / w);
    if (k < 1) fit.style.transform = 'scale(' + k + ')';
  }
  function fitActive() {
    var a = deck.querySelector('.slide.active');
    if (a) fitSlide(a);
  }

  // --- scale the whole canvas to fill the viewport ---
  function fitDeck() {
    // fill the viewport edge-to-edge (16:9 is preserved; the limiting axis wins)
    var k = Math.min(window.innerWidth / DES_W, window.innerHeight / DES_H);
    deck.style.transform = 'scale(' + k + ')';
  }
  function fitAll() { fitDeck(); fitActive(); }

  // --- full screen ---
  function toggleFull() {
    if (document.fullscreenElement) {
      if (document.exitFullscreen) document.exitFullscreen();
    } else {
      var el = document.documentElement;
      if (el.requestFullscreen) el.requestFullscreen();
      else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    }
  }
  var fsBtn = null;
  var nav = document.querySelector('.nav');
  if (nav) {
    fsBtn = document.createElement('button');
    fsBtn.textContent = '⛶ Full';
    fsBtn.setAttribute('aria-label', 'Toggle full screen (f)');
    fsBtn.addEventListener('click', toggleFull);
    nav.insertBefore(fsBtn, document.getElementById('help-btn') || null);
  }
  document.addEventListener('fullscreenchange', function () {
    var full = !!document.fullscreenElement;
    document.body.classList.toggle('presenting', full);
    if (fsBtn) fsBtn.textContent = full ? '⛶ Exit' : '⛶ Full';
    fitAll();
  });
  document.addEventListener('keydown', function (e) {
    if (e.target && e.target.tagName === 'INPUT') return;
    if (e.key === 'f' || e.key === 'F') { toggleFull(); e.preventDefault(); }
  });

  // --- hook slide changes + resize ---
  if (typeof window.show === 'function') {
    var _show = window.show;
    window.show = function (n) { _show(n); fitActive(); };
  }
  var raf = null;
  window.addEventListener('resize', function () {
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(fitAll);
  });
  fitAll();
})();
</script>"""


# ---------------------------------------------------------------------------
# Markdown block model -> HTML
# ---------------------------------------------------------------------------
INLINE_RE = re.compile(
    r"\*\*(.+?)\*\*"                    # 1 bold
    r"|`([^`]+)`"                       # 2 code
    r"|\[([^\]]+)\]\(([^)]+)\)"         # 3 link text  4 link url
    r"|(?<!\w)_([^_]+)_(?!\w)"          # 5 italic (underscore)
    r"|(?<![\w*])\*([^*]+)\*(?![\w*])"  # 6 italic (asterisk)
)


def esc(s, quote=False):
    return htmllib.escape(str(s), quote)


def render_inline(text: str) -> str:
    out, pos = [], 0
    for m in INLINE_RE.finditer(text):
        out.append(esc(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<b>" + esc(m.group(1)) + "</b>")
        elif m.group(2) is not None:
            out.append("<code>" + esc(m.group(2)) + "</code>")
        elif m.group(3) is not None:
            out.append(f'<a href="{esc(m.group(4), True)}" target="_blank" '
                       f'rel="noopener">{esc(m.group(3))}</a>')
        elif m.group(5) is not None:
            out.append("<i>" + esc(m.group(5)) + "</i>")
        elif m.group(6) is not None:
            out.append("<i>" + esc(m.group(6)) + "</i>")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def render_bullets(items) -> str:
    out, i, n = ["<ul>"], 0, len(items)
    while i < n:
        text = render_inline(items[i]["text"])
        j = i + 1
        subs = []
        while j < n and items[j]["level"] == 1:
            subs.append(items[j]); j += 1
        if subs:
            out.append("<li>" + text + "<ul>"
                       + "".join("<li>" + render_inline(s["text"]) + "</li>" for s in subs)
                       + "</ul></li>")
        else:
            out.append("<li>" + text + "</li>")
        i = j
    out.append("</ul>")
    return "".join(out)


def render_table(rows) -> str:
    out = ['<table class="matrix">']
    for ri, row in enumerate(rows):
        tag = "th" if ri == 0 else "td"
        out.append("<tr>" + "".join(f"<{tag}>{render_inline(c)}</{tag}>" for c in row) + "</tr>")
    out.append("</table>")
    return "".join(out)


def render_columns(cols) -> str:
    if cols and all(column_is_links(c) for c in cols):
        out = ['<div class="exlinks">']
        for c in cols:
            out.append('<div class="col"><h4>' + esc(c["heading"]) + "</h4>")
            out += [render_inline(it) for it in c["items"]]
            out.append("</div>")
        out.append("</div>")
        return "".join(out)
    out = ['<div class="two-col">']
    for c in cols:
        out.append('<div class="col"><h4>' + esc(c["heading"]) + "</h4><ul>")
        out += ["<li>" + render_inline(it) + "</li>" for it in c["items"]]
        out.append("</ul></div>")
    out.append("</div>")
    return "".join(out)


def render_block(b) -> str:
    t = b["type"]
    if t == "para":
        return "<p>" + render_inline(b["text"]) + "</p>"
    if t == "bullets":
        return render_bullets(b["items"])
    if t == "numbered":
        return "<ol>" + "".join("<li>" + render_inline(it) + "</li>" for it in b["items"]) + "</ol>"
    if t == "code":
        return "<pre><code>" + "\n".join(esc(ln) for ln in b["lines"]) + "</code></pre>"
    if t == "callout":
        return '<div class="callout">' + render_inline(b["text"]) + "</div>"
    if t == "table":
        return render_table(b["rows"])
    if t == "columns":
        return render_columns(b["cols"])
    if t == "capstones":
        return render_capstones(b["items"])
    return ""


def render_capstones(items) -> str:
    # left: every title (the active one highlights); right: its description, rotating
    out = ['<div class="caps-rotator" data-interval="3200">', '<div class="caps-list">']
    for k, it in enumerate(items):
        out.append(f'<div class="caps-item{" active" if k == 0 else ""}" data-i="{k}">'
                   f'{render_inline(it["name"])}</div>')
    out.append('</div><div class="caps-desc-panel">')
    for k, it in enumerate(items):
        out.append(f'<div class="caps-desc-page{" show" if k == 0 else ""}">'
                   f'<div class="caps-desc-name">{render_inline(it["name"])}</div>'
                   f'<div class="caps-desc-text">{render_inline(it["desc"])}</div></div>')
    out.append("</div></div>")
    return "".join(out)


FOOTER = ('<div class="footer"><span>Workshop · v1</span>'
          '<div class="progress"><div></div></div><span class="counter"></span></div>')


def render_slide(attrs, data) -> str:
    layout = attrs.get("layout", "content")
    kicker = attrs.get("kicker", "")
    title = data.get("title") or ""
    lede = data.get("lede")
    out = []

    if layout == "title":
        out.append('<section class="slide title-slide">')
        if kicker:
            out.append(f'<div class="kicker">{esc(kicker)}</div>')
        out.append(f"<h1>{render_inline(title)}</h1>")
        if lede:
            out.append('<p class="sub" style="font-size:26px;color:var(--ink);'
                       f'margin-top:6px;margin-bottom:14px;">{render_inline(lede)}</p>')
        for b in data["blocks"]:
            if b["type"] == "para" and b["text"].startswith("Contributors:"):
                names = b["text"].split(":", 1)[1].strip()
                out.append('<p class="sub" style="font-size:16px;margin-top:22px;">'
                           '<span style="text-transform:uppercase;letter-spacing:0.14em;'
                           'font-size:12px;color:var(--accent);font-weight:700;">Contributors</span>'
                           f"<br>{render_inline(names)}</p>")
            elif b["type"] == "para":
                out.append(f'<p class="sub">{render_inline(b["text"])}</p>')
            else:
                out.append(render_block(b))
    elif layout in ("section", "closing"):
        out.append('<section class="slide section-divider">')
        if kicker:
            out.append(f'<div class="kicker">{esc(kicker)}</div>')
        out.append(f"<h1>{render_inline(title)}</h1>")
        if lede:
            out.append(f'<p class="lede">{render_inline(lede)}</p>')
        for b in data["blocks"]:
            out.append(render_block(b))
    else:  # content
        out.append('<section class="slide">')
        if kicker:
            out.append(f"<h3>{esc(kicker)}</h3>")
        out.append(f"<h1>{render_inline(title)}</h1>")
        if lede:
            out.append(f'<p class="lede">{render_inline(lede)}</p>')
        for b in data["blocks"]:
            out.append(render_block(b))

    out.append(FOOTER)
    out.append("</section>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Page chrome (nav controls + help overlay + navigation script)
# ---------------------------------------------------------------------------
NAV_MARKUP = """<div class="nav">
  <span class="nav-label">go to</span>
  <input type="number" id="jump-to" class="jump-to" min="1" placeholder="#" aria-label="Jump to slide number">
  <button id="prev" aria-label="Previous slide">← Prev</button>
  <button id="next" aria-label="Next slide">Next →</button>
  <button id="auto-toggle" aria-label="Toggle auto-advance">▶ Auto</button>
  <button id="help-btn" aria-label="Help" title="Keyboard shortcuts (?)">?</button>
</div>

<div id="help-overlay" role="dialog" aria-modal="true" aria-label="Keyboard shortcuts">
  <div class="panel">
    <h2>Keyboard shortcuts</h2>
    <table>
      <tr><td>← → Space</td><td>Previous / next slide</td></tr>
      <tr><td>Home / End</td><td>First / last slide</td></tr>
      <tr><td>(digits) Enter</td><td>Jump to slide N</td></tr>
      <tr><td>g</td><td>Focus the "go to" input</td></tr>
      <tr><td>t</td><td>Toggle auto-advance (5 s)</td></tr>
      <tr><td>T</td><td>Set custom auto-advance interval</td></tr>
      <tr><td>f</td><td>Toggle full screen</td></tr>
      <tr><td>?</td><td>Show this help</td></tr>
      <tr><td>Esc</td><td>Close help / cancel jump</td></tr>
    </table>
    <div class="close-hint">Press any key to dismiss</div>
  </div>
</div>"""

NAV_JS = """<script>
  const slides = Array.from(document.querySelectorAll('.slide'));
  let i = 0, timer = null, intervalMs = 5000, digitBuffer = '', digitTimeout = null;

  function show(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    const active = slides[i];
    const counter = active.querySelector('.counter');
    if (counter) counter.textContent = (i + 1) + ' / ' + slides.length;
    const bar = active.querySelector('.progress > div');
    if (bar) bar.style.width = (((i + 1) / slides.length) * 100) + '%';
    history.replaceState(null, '', '#' + (i + 1));
    const jumpInput = document.getElementById('jump-to');
    if (jumpInput && document.activeElement !== jumpInput) jumpInput.value = i + 1;
    if (timer && i >= slides.length - 1) stopTimer();
  }
  function startTimer() {
    if (timer) return;
    timer = setInterval(() => { if (i < slides.length - 1) show(i + 1); else stopTimer(); }, intervalMs);
    const btn = document.getElementById('auto-toggle');
    btn.textContent = '⏸ Stop (' + (intervalMs / 1000) + 's)';
    btn.classList.add('active');
  }
  function stopTimer() {
    if (timer) { clearInterval(timer); timer = null; }
    const btn = document.getElementById('auto-toggle');
    btn.textContent = '▶ Auto';
    btn.classList.remove('active');
  }
  function toggleTimer() { timer ? stopTimer() : startTimer(); }
  function showHelp() { document.getElementById('help-overlay').classList.add('show'); }
  function hideHelp() { document.getElementById('help-overlay').classList.remove('show'); }
  function flushDigitBuffer() {
    if (!digitBuffer) return;
    const n = parseInt(digitBuffer, 10);
    if (isFinite(n) && n > 0) show(n - 1);
    digitBuffer = '';
    if (digitTimeout) { clearTimeout(digitTimeout); digitTimeout = null; }
  }
  document.getElementById('prev').addEventListener('click', () => { stopTimer(); show(i - 1); });
  document.getElementById('next').addEventListener('click', () => { stopTimer(); show(i + 1); });
  document.getElementById('auto-toggle').addEventListener('click', toggleTimer);
  document.getElementById('help-btn').addEventListener('click', showHelp);
  document.getElementById('help-overlay').addEventListener('click', hideHelp);
  const jumpInput = document.getElementById('jump-to');
  jumpInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const n = parseInt(jumpInput.value, 10);
      if (isFinite(n) && n > 0) { stopTimer(); show(n - 1); jumpInput.blur(); }
      e.preventDefault();
    } else if (e.key === 'Escape') { jumpInput.value = i + 1; jumpInput.blur(); }
  });
  document.addEventListener('keydown', (e) => {
    if (e.target === jumpInput) return;
    const overlay = document.getElementById('help-overlay');
    if (overlay.classList.contains('show')) { hideHelp(); e.preventDefault(); return; }
    if (/^[0-9]$/.test(e.key)) {
      digitBuffer += e.key;
      if (digitTimeout) clearTimeout(digitTimeout);
      digitTimeout = setTimeout(() => { digitBuffer = ''; }, 1500);
      e.preventDefault(); return;
    }
    if (e.key === 'Enter') { flushDigitBuffer(); e.preventDefault(); return; }
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') { stopTimer(); show(i + 1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { stopTimer(); show(i - 1); e.preventDefault(); }
    else if (e.key === 'Home') { stopTimer(); show(0); }
    else if (e.key === 'End') { stopTimer(); show(slides.length - 1); }
    else if (e.key === 't') { toggleTimer(); e.preventDefault(); }
    else if (e.key === 'T') {
      const v = prompt('Auto-advance interval in seconds:', String(intervalMs / 1000));
      const secs = parseFloat(v);
      if (isFinite(secs) && secs > 0) { intervalMs = Math.round(secs * 1000); if (timer) { stopTimer(); startTimer(); } }
    }
    else if (e.key === 'g') { jumpInput.focus(); jumpInput.select(); e.preventDefault(); }
    else if (e.key === '?') { showHelp(); e.preventDefault(); }
    else if (e.key === 'Escape') { stopTimer(); digitBuffer = ''; }
    else { digitBuffer = ''; }
  });
  const initial = parseInt((location.hash || '#1').slice(1), 10);
  show(isFinite(initial) && initial > 0 ? initial - 1 : 0);
</script>"""

ROTATOR_JS = """<script>
  /* Capstone showcase: highlight each title in turn and crossfade its description.
     Clicking a title jumps to it and restarts the rotation. */
  document.querySelectorAll('.caps-rotator').forEach(function (r) {
    var items = Array.prototype.slice.call(r.querySelectorAll('.caps-item'));
    var pages = Array.prototype.slice.call(r.querySelectorAll('.caps-desc-page'));
    if (pages.length < 2) return;
    var idx = 0, timer = null;
    var interval = parseInt(r.getAttribute('data-interval') || '3200', 10);
    function go(n) {
      if (items[idx]) items[idx].classList.remove('active');
      if (pages[idx]) pages[idx].classList.remove('show');
      idx = (n + pages.length) % pages.length;
      if (items[idx]) items[idx].classList.add('active');
      if (pages[idx]) pages[idx].classList.add('show');
    }
    function start() { timer = setInterval(function () { go(idx + 1); }, interval); }
    items.forEach(function (it, k) {
      it.addEventListener('click', function () { clearInterval(timer); go(k); start(); });
    });
    start();
  });
</script>"""


def render_document(slides, css: str) -> str:
    sections = "\n".join(render_slide(attrs, data) for attrs, data in slides)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Files, not chats — Claude Code for mathematicians</title>
<style>{css}</style>
</head>
<body>
<div id="deck">
{sections}
</div>
{NAV_MARKUP}
{NAV_JS}
{FIT_JS}
{ROTATOR_JS}
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=None)
    ap.add_argument("--slides", default=str(SLIDES_DIR))
    ap.add_argument("--out", default=str(REPO / "slides.html"))
    args = ap.parse_args()

    potx = Path(args.template) if args.template else find_template()
    if not potx or not potx.exists():
        raise SystemExit("Argonne template not found. Pass --template or place it at "
                         "templates/Argonne_16x9_template.potx")

    doe = data_uri(potx, DOE_LOGO)
    arg = data_uri(potx, ARGONNE_LOGO)
    css = argonne_css(doe, arg)

    slides = load_all_slides(Path(args.slides))
    doc = render_document(slides, css)
    Path(args.out).write_text(doc, encoding="utf-8")
    print(f"Wrote {args.out}  (Argonne theme, {len(slides)} slides from {Path(args.slides).name}/)")


if __name__ == "__main__":
    main()
