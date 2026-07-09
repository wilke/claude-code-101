#!/usr/bin/env python3
"""Build slides-argonne.html — the workshop deck restyled to the Argonne
16x9 template (white base slide with the blue left bar, Arial, Argonne-blue
titles, gold section eyebrows, DOE + Argonne logos).

It reuses the CONTENT and navigation JS of slides.html verbatim and only swaps
the stylesheet + inlines the two Argonne logos (extracted from the template).
Content stays in sync with slides.html / docs/slides/.

Usage:
    python scripts/build_html.py [--template PATH] [--src slides.html] [--out slides-argonne.html]
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
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
  #deck {{
    position: relative;
    width: min(96vw, 1180px);
    aspect-ratio: 16 / 9;
    max-height: 92vh;
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
  /* content-slide kicker → Argonne blue strip */
  .slide > h3 {{
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
  @media (max-width: 800px) {{
    .slide {{ padding: 30px 26px 56px 34px; }}
    .slide h1 {{ font-size: 30px; }}
    .slide h2 {{ font-size: 23px; }}
    .slide p, .slide li {{ font-size: 16px; }}
    .two-col {{ grid-template-columns: 1fr; }}
    .footer::before {{ width: 130px; }}
    .footer::after {{ width: 78px; }}
  }}
"""


FIT_JS = r"""<script>
/* Shrink-to-fit: wrap each slide's content and scale it down so a dense slide
   never clips at 16:9 (or on a small laptop). Only scales down, never up. */
(function () {
  var deck = document.getElementById('deck');
  if (!deck) return;

  // wrap every slide's non-footer content in a .fit container
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

  // run fit after every slide change, and on resize (window / TV / fullscreen)
  if (typeof window.show === 'function') {
    var _show = window.show;
    window.show = function (n) { _show(n); fitActive(); };
  }
  var raf = null;
  window.addEventListener('resize', function () {
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(fitActive);
  });
  fitActive();
})();
</script>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", default=None)
    ap.add_argument("--src", default=str(REPO / "slides.html"))
    ap.add_argument("--out", default=str(REPO / "slides-argonne.html"))
    args = ap.parse_args()

    potx = Path(args.template) if args.template else find_template()
    if not potx or not potx.exists():
        raise SystemExit("Argonne template not found. Pass --template or place it at "
                         "templates/Argonne_16x9_template.potx")

    doe = data_uri(potx, DOE_LOGO)
    arg = data_uri(potx, ARGONNE_LOGO)

    html = Path(args.src).read_text(encoding="utf-8")

    # swap the stylesheet
    css = argonne_css(doe, arg)
    html = re.sub(r"<style>.*?</style>", f"<style>{css}</style>", html, count=1, flags=re.S)

    # retitle + drop the aspect-ratio hint comment; note the theme
    html = html.replace(
        "<title>Files, not chats — Claude Code for mathematicians</title>",
        "<title>Files, not chats — Claude Code for mathematicians (Argonne theme)</title>",
    )
    # the source deck is authored at 16:10; Argonne template is 16:9 (shorter), so
    # dense slides can overflow. Inject a shrink-to-fit pass so every slide's
    # content scales down to fit at any viewport size (TV or small laptop).
    html = html.replace("</body>", FIT_JS + "\n</body>", 1)

    Path(args.out).write_text(html, encoding="utf-8")
    print(f"Wrote {args.out}  (Argonne-themed reskin of {Path(args.src).name})")


if __name__ == "__main__":
    main()
