#!/usr/bin/env python3
"""Shared parser for the slide ground truth in docs/slides/*.md.

Both generators build from this one source:
  - build_html.py  -> slides.html          (Argonne-themed browser deck)
  - build_pptx.py  -> slides-argonne.pptx  (Argonne PowerPoint)

Slide format (see docs/slides/INDEX.md):
  <!--slide n=8 layout=content kicker="Session basics"-->
  # Title
  _optional lede_
  body: bullets, `1.` numbered, fenced code, | tables |, > callouts,
        :::columns / ### col headings
"""
from __future__ import annotations

import re
from pathlib import Path

META_RE = re.compile(r"<!--slide\s+(.*?)-->", re.S)
ATTR_RE = re.compile(r'(\w+)=(?:"([^"]*)"|(\S+))')
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
TOKEN_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def parse_attrs(raw: str) -> dict:
    out = {}
    for m in ATTR_RE.finditer(raw):
        out[m.group(1)] = m.group(2) if m.group(2) is not None else m.group(3)
    return out


def split_slides(text: str):
    """Yield (attrs, body_lines) for each slide in a markdown file."""
    parts = META_RE.split(text)
    # parts = [pre, attrs1, body1, attrs2, body2, ...]
    it = iter(parts[1:])
    for attrs_raw, body in zip(it, it):
        yield parse_attrs(attrs_raw), body.splitlines()


def is_emph_line(line: str) -> bool:
    s = line.strip()
    return len(s) >= 2 and s.startswith("_") and s.endswith("_")


def parse_table(rows: list[str]):
    def cells(r):
        return [c.strip() for c in r.strip().strip("|").split("|")]
    parsed = [cells(r) for r in rows]
    # drop the |---|---| separator row
    parsed = [r for r in parsed if not all(set(c) <= set("-: ") for c in r)]
    return parsed


def parse_body(lines: list[str]) -> dict:
    """Return {title, lede, blocks}. blocks is a list of typed dicts."""
    title = None
    lede = None
    blocks = []
    i = 0
    n = len(lines)

    while i < n and not lines[i].strip():
        i += 1
    if i < n and lines[i].startswith("# "):
        title = lines[i][2:].strip()
        i += 1
    while i < n and not lines[i].strip():
        i += 1
    if i < n and is_emph_line(lines[i]):
        lede = lines[i].strip()[1:-1].strip()
        i += 1

    para: list[str] = []

    def flush_para():
        nonlocal para
        if para:
            blocks.append({"type": "para", "text": " ".join(para).strip()})
            para = []

    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            flush_para()
            i += 1
            continue
        if s.startswith("```"):
            flush_para()
            i += 1
            code = []
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # closing fence
            blocks.append({"type": "code", "lines": code})
            continue
        if s == ":::columns":
            flush_para()
            i += 1
            cols = []
            cur = None
            while i < n and lines[i].strip() != ":::":
                cs = lines[i].strip()
                if cs.startswith("### "):
                    cur = {"heading": cs[4:].strip(), "items": []}
                    cols.append(cur)
                elif cs.startswith("- ") and cur is not None:
                    cur["items"].append(cs[2:].strip())
                elif cs and cur is not None:
                    cur["items"].append(cs)
                i += 1
            i += 1  # closing :::
            blocks.append({"type": "columns", "cols": cols})
            continue
        if s.startswith("|"):
            flush_para()
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(lines[i].strip())
                i += 1
            blocks.append({"type": "table", "rows": parse_table(rows)})
            continue
        if s.startswith("> "):
            flush_para()
            buf = []
            while i < n and lines[i].strip().startswith("> "):
                buf.append(lines[i].strip()[2:])
                i += 1
            blocks.append({"type": "callout", "text": " ".join(buf).strip()})
            continue
        if re.match(r"^\s*- ", line):
            flush_para()
            items = []
            while i < n and re.match(r"^\s*- ", lines[i]):
                indent = len(lines[i]) - len(lines[i].lstrip())
                items.append({"level": 1 if indent >= 4 else 0,
                              "text": lines[i].strip()[2:].strip()})
                i += 1
            blocks.append({"type": "bullets", "items": items})
            continue
        if re.match(r"^\s*\d+\. ", line):
            flush_para()
            items = []
            while i < n and re.match(r"^\s*\d+\. ", lines[i]):
                items.append(re.sub(r"^\s*\d+\.\s*", "", lines[i]).strip())
                i += 1
            blocks.append({"type": "numbered", "items": items})
            continue
        para.append(s)
        i += 1
    flush_para()
    return {"title": title, "lede": lede, "blocks": blocks}


def strip_inline(text: str) -> str:
    """Plain-text version of an inline string (drop **, `, [](), _emphasis_)."""
    text = LINK_RE.sub(r"\1", text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", r"\1", text)
    return text


def column_is_links(col: dict) -> bool:
    """A column whose items are (mostly) markdown links renders as link lists."""
    items = col.get("items", [])
    if not items:
        return False
    linky = sum(1 for it in items if it.strip().startswith("["))
    return linky >= max(1, len(items) // 2)


def load_all_slides(slides_dir: Path):
    """Return [(attrs, data)] for every slide, ordered by the `n=` attribute."""
    slides = []
    for f in sorted(Path(slides_dir).glob("[0-9][0-9]-*.md")):
        for attrs, body in split_slides(f.read_text(encoding="utf-8")):
            slides.append((attrs, parse_body(body)))
    slides.sort(key=lambda s: int(s[0].get("n", 0)))
    return slides
