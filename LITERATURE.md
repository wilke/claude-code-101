# Addendum — Literature research with Claude Code

For mathematicians, literature reading isn't a side activity; it's the daily work. This addendum extends the workshop materials with patterns, prompts, skills, and a small exercise specifically for literature work — including how to plug in a Retrieval-Augmented Generation (RAG) system like `moodlehq/wiki-rag` so Claude can reach beyond its training data.

This file is the deeper companion to:

- the *Literature: the fifth artifact* and *RAG* slides in Part 4 of the deck,
- the §4d *Literature research* section of `WORKFLOW.md`,
- the `paper-summary` skill in `exercises/03-skills/skills/paper-summary/`.

## 1. Why literature research is central — and risky — for this audience

Optimization research lives in a paper-dense field. The literature on interior-point methods alone spans 50+ years and is fragmented across multiple notation conventions. A new project's first month is often as much *reading* as *coding*. Anything that genuinely accelerates the reading-to-decision loop has outsized value.

Claude Code helps in three ways:

1. **PDF intake.** Pulling text, equations, and section structure out of a paper is dull, error-prone, and exactly what the built-in `pdf` skill plus a `paper-summary` skill turns into a 30-second task.
2. **Notation translation.** Fluent translation between Nocedal–Wright, Conn–Gould–Toint, Boyd–Vandenberghe, Bertsekas, and the conventions of any specific paper. This is normally one of the highest-friction parts of reading across subfields.
3. **Code↔paper cross-referencing.** Tying the line search in your `driver.py` back to its source paper section, every time. Pays back when you write the paper.

Three failure modes are equally specific:

1. **Hallucinated citations.** Models will invent plausible references when they don't know. The DOIs look real. The author names are correct *for some other paper*. This is the most damaging failure mode for a researcher because the output is exactly what you wanted, just fictional.
2. **Misattribution.** Crediting a method to a survey rather than the original; the second author rather than the first.
3. **Training-cutoff blindness.** Recent papers are invisible. The model will answer confidently anyway.

The architecture below is structured to use the upside while neutralizing the downside. The single most important rule is that **citations are never emitted from memory** — they're resolved by an MCP that talks to a real database (arXiv, Semantic Scholar) or quoted from a local PDF. Anything else is `[citation needed]`.

## 2. The five-file architecture

The four-file architecture from `WORKFLOW.md` extends to literature as follows:

```
project/
├── CLAUDE.md           # conventions; includes the literature verification rule
├── LOGBOOK.md           # cites both plans/ and literature/
├── STATUS.md           # current state
├── plans/              # forward-looking plans
└── literature/         # one paper per file, named by BibTeX key
    ├── INDEX.md        # contents page (helpful past ~10 entries)
    ├── wachter-biegler-2006.md
    ├── nocedal-wright-12.md
    └── conn-gould-toint-2000.md
```

Each `literature/<bibkey>.md` follows the template in `exercises/03-skills/skills/paper-summary/SKILL.md` (and the worked example in `examples/example-output.md`). The template enforces consistency so the directory is searchable.

`LOGBOOK.md` decisions cite both `plans/` and `literature/`:

```markdown
## Decisions
- **2026-04-08 — Filter line search.**
  Outcome of plans/2026-04-08-filter-linesearch.md.
  Source: literature/wachter-biegler-2006.md §4.2.
  Test: tests/test_filter.py::test_hs071_converges.
```

## 3. The CLAUDE.md verification rule

Add this section to your project's CLAUDE.md. It is the single highest-leverage change for literature work.

```markdown
## Literature
- Never emit a citation from memory. For every paper claim:
  1. Resolve the citation via the arxiv or semantic-scholar MCP.
  2. Quote the relevant passage from the local PDF if available.
  3. If neither is possible, mark the claim as `[citation needed]`.
- Treat any citation lacking (1) or (2) as unverified.
- When summarizing a paper, prefer literal quotes from the PDF over
  paraphrase. Paraphrase drops the qualifier that matters.
- New paper intake: use the paper-summary skill. Output goes to
  literature/<bibkey>.md. Do not invent the BibTeX key.
```

## 4. Skills for literature work

Three are useful. The first ships with the workshop.

### `paper-summary` (ships in `exercises/03-skills/skills/paper-summary/`)

Given a PDF, produce a structured `literature/<bibkey>.md` with contribution, main result, assumptions, limitations, fit-to-our-problem, literal pull-quotes, and a verified BibTeX entry. The SKILL.md enforces literal quoting and refuses to invent citations.

### `citation-resolver` (sketch — implement when you have an arXiv/Semantic Scholar MCP)

```yaml
---
name: citation-resolver
origin: workshop
description: |
  Resolve a paper citation fragment (author-year, title fragment, "the
  Wächter-Biegler filter") into a verified BibTeX entry. ALWAYS uses
  the arxiv or semantic-scholar MCP to verify; never emits a citation
  from memory. Use whenever the user references a paper informally and
  needs the actual reference, or before adding a citation to a paper
  draft or LOGBOOK.md.
---

# Citation resolver

1. Parse the fragment into candidate (author, year, keywords).
2. Query semantic-scholar MCP first (broader coverage); fall back to arxiv MCP.
3. Return the top match with full BibTeX, DOI, and a one-line abstract.
4. If no high-confidence match, return [citation needed] and propose
   alternative search terms. Do not guess.
```

### `tex-equation-extractor` (sketch)

```yaml
---
name: tex-equation-extractor
origin: workshop
description: |
  Extract display-math equations from a paper PDF and return them as
  numbered LaTeX. Use when the user wants to lift derivations into
  their own derivations.tex without retyping. Operates on a PDF path.
---

# TeX equation extractor

1. Read the PDF (built-in pdf skill).
2. Locate display-math sections (often labeled (1), (2), ... or
   numbered by the paper).
3. Return as LaTeX, preserving the paper's original numbering as a
   comment (so the user can cross-reference).
```

## 5. Prompt cookbook for literature work

Copy these into your sessions; tweak filenames.

```
# New paper intake — single PDF in papers-inbox/
> read papers-inbox/wachter-biegler-2006.pdf with the paper-summary
  skill. Save to literature/wachter-biegler-2006.md. Verify the
  citation via the semantic-scholar MCP before saving.

# Bulk intake — handle a folder of PDFs
> for each PDF in papers-inbox/, run the paper-summary skill, save to
  literature/<bibkey>.md, and produce a one-line summary in literature/
  INDEX.md. Skip any that already exist in literature/.

# Cross-reference a method in code to its source paper
> in driver.py:142, the comment mentions the Wächter-Biegler filter.
  Resolve that reference using the citation-resolver skill, then add
  a precise pointer to the paper section (e.g., §4.2) above the code.

# Verify a draft section's citations before submission
> read paper-draft.tex. For every \cite{...}, confirm the bibkey
  exists in references.bib and that the corresponding entry in
  literature/<bibkey>.md exists and matches the in-text claim. List
  any unverified citations.

# Audit LOGBOOK.md for unsourced claims
> scan LOGBOOK.md for parameter folklore or decisions that don't cite
  a literature/ entry. List them; suggest which paper would be the
  right citation if known. Mark unknowns as [citation needed].

# End-of-session habit
> are there any [citation needed] markers in files modified in this
  session? List them so I can resolve them next time.

# Set up the literature/ directory in a fresh project
> create a literature/ directory next to plans/. Add literature/INDEX.md
  as a template with a one-line description of how the directory works
  and a placeholder for the contents list.
```

## 6. RAG primer — when literature outgrows your context window

The four-file architecture and a `literature/` directory work beautifully up to a few hundred summaries. Past that, retrieving "everything we've read about saddle-point smoothing" by grep gets unreliable, and the corpus of full-text PDFs definitely doesn't fit in context.

**Retrieval-Augmented Generation** is the standard answer. The shape is simple:

1. **Index.** Chunk every document into 200–500 word passages. Compute an embedding for each chunk; store in a vector database. Keep an inverted index of keywords for hybrid search.
2. **Retrieve.** For a query, embed it; return the top-K most similar chunks, optionally re-ranked.
3. **Generate.** Send the chunks plus the query to the model. The model answers using only what was retrieved, with explicit document IDs.

Three properties matter for a researcher:

- **Citations are document IDs**, not paraphrases of training data. Verifiable.
- **The corpus grows independently of context.** Add 1000 papers; nothing about your prompts changes.
- **The training cutoff stops mattering** for whatever you've indexed.

When you'd reach for it: a group MediaWiki of operational notes; a Notion or Confluence; a folder of >50 PDFs; a shared lab notebook archive.

## 7. `moodlehq/wiki-rag` — a concrete deployment

`moodlehq/wiki-rag` ([github.com/moodlehq/wiki-rag](https://github.com/moodlehq/wiki-rag)) is an experimental RAG specialized for **MediaWiki** sites. It's worth knowing about because:

- **MediaWiki is common in research groups and university IT.** If your lab's documentation lives in MediaWiki, this is the path of least resistance.
- **Hybrid retrieval done right.** Vector search via Milvus + BM25-style keyword search + fusion reranking — the configuration the literature recommends for technical content where exact-term matches matter.
- **OpenAI-compatible API.** Exposes `/v1/models` and `/v1/chat/completions`. Anything that speaks the OpenAI API can plug in, including a thin MCP wrapper.
- **Open source and Docker-runnable.** No SaaS dependency.

If your group's knowledge isn't in MediaWiki, the architecture transfers — see §9 below for the wrapper pattern that makes any OpenAI-compatible RAG into an MCP tool.

### Quick deploy sketch

Per the project's docs (verify the current commands at the repo before running):

```bash
git clone https://github.com/moodlehq/wiki-rag
cd wiki-rag
# Configure the target MediaWiki site, embedding model, and Milvus
# connection in the provided .env file.
docker compose up
# wiki-rag is now serving on http://localhost:8000/v1/chat/completions
```

You point it at the MediaWiki API endpoint (e.g., `https://wiki.example.org/api.php`); it ingests pages via the API and indexes them into Milvus.

## 8. Wrapping a RAG system as an MCP tool

This is the bridge between *any* RAG with an OpenAI-compatible API and Claude Code. About 30 lines.

```python
"""wiki_rag_mcp.py — expose a wiki-rag instance as an MCP tool.

Register with:
    claude mcp add lab-wiki --command python --args "$(pwd)/wiki_rag_mcp.py"
"""
from __future__ import annotations
import asyncio, os, json
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

WIKI_RAG_URL = os.environ.get("WIKI_RAG_URL", "http://localhost:8000")
server = Server("lab-wiki")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="query_lab_wiki",
            description=(
                "Query the lab's MediaWiki via wiki-rag. Returns a "
                "natural-language answer plus source-document IDs."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name != "query_lab_wiki":
        raise ValueError(f"Unknown tool: {name}")
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.post(
            f"{WIKI_RAG_URL}/v1/chat/completions",
            json={
                "model": "wiki-rag",
                "messages": [{"role": "user", "content": arguments["question"]}],
            },
        )
        r.raise_for_status()
        data = r.json()
    return [TextContent(type="text", text=data["choices"][0]["message"]["content"])]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
```

Once registered, every Claude Code session in the project can call `query_lab_wiki(question)` like any other tool. The retrieved passages come with source IDs you can spot-check.

The same wrapper works for any RAG with an OpenAI-compatible endpoint — swap the URL and you're done. This is the value of OpenAI-compatibility as a de-facto standard.

## 9. End-to-end workflow for a mathematician

A concrete week-in-the-life:

1. **Monday.** Skim arXiv via the arXiv MCP; pull three candidate papers into `papers-inbox/`.
2. Run the `paper-summary` skill on each. Edit the resulting `literature/*.md` files; verify pull-quotes against the PDFs.
3. **Tuesday.** Reading session. Use the `tex-equation-extractor` skill to lift one promising derivation into `docs/derivations.tex`.
4. **Wednesday.** Coding session. The decision to adopt method X gets a `LOGBOOK.md` entry citing both `plans/2026-XX-method-X.md` and `literature/<paper>.md`.
5. **Thursday.** A question comes up: "what does the field say about saddle-point smoothing for inverse problems?" Ask the `query_lab_wiki` MCP (backed by wiki-rag indexing the group's MediaWiki) for an answer with source IDs. Cross-check the most-cited source against `literature/`.
6. **Friday.** End-of-week habit: ask Claude to *list every `[citation needed]` marker across all files*. Resolve them or close them as out-of-scope.

## 10. Exercise — extend the workshop with one paper

A 20-minute exercise to consolidate the literature workflow. Suitable as homework after the main workshop or as a stretch goal during the capstone.

### Setup

Choose a single paper relevant to the capstone — for example, Wächter & Biegler (2006) on IPOPT, or Hinze, Pinnau, Ulbrich, Ulbrich (2009) on PDE-constrained optimization. Download the PDF.

### Steps

1. **Install the `paper-summary` skill** in your project's `.claude/skills/`:
   ```bash
   mkdir -p .claude/skills
   cp -R exercises/03-skills/skills/paper-summary .claude/skills/
   ```

2. **Add the verification rule to CLAUDE.md.** Copy the block from §3 of this addendum.

3. **Create `literature/`** at your project root:
   ```bash
   mkdir literature
   echo '# Literature index\n\nOne entry per paper.\n' > literature/INDEX.md
   ```

4. **Run the skill** in a Claude Code session:
   ```
   > read papers-inbox/wachter-biegler-2006.pdf with the paper-summary
     skill. Save to literature/wachter-biegler-2006.md. Verify the
     citation via whatever MCP is available; if none, mark unverified.
   ```

5. **Edit ruthlessly.** The first draft of any AI-produced summary is too long. Target one screen.

6. **Cite from LOGBOOK.md.** Pick one decision in your LOGBOOK.md (or the capstone's LOGBOOK.md) and add a citation to the new `literature/<bibkey>.md` file.

7. **Stretch — wire wiki-rag.** If you have a MediaWiki you can experiment with (or stand one up locally), deploy `moodlehq/wiki-rag` per its README, then register the MCP wrapper from §8. Now ask Claude an open question about that wiki's content and verify the source IDs.

### Discussion prompts

- Where did the paper-summary skill help most? Where did it produce wrong-shaped output?
- What's the failure mode when the citation can't be verified? Did Claude follow the rule, or did it slip and emit a guess?
- For an unfamiliar paper outside your subfield, would the literal pull-quotes have changed your understanding versus the paraphrased summary? Which is more honest?

## References

- `moodlehq/wiki-rag` — [github.com/moodlehq/wiki-rag](https://github.com/moodlehq/wiki-rag)
- Model Context Protocol — [modelcontextprotocol.io](https://modelcontextprotocol.io)
- arXiv API — [info.arxiv.org/help/api](https://info.arxiv.org/help/api)
- Semantic Scholar API — [api.semanticscholar.org](https://api.semanticscholar.org)
- Milvus (vector DB used by wiki-rag) — [milvus.io](https://milvus.io)

Sources:

- [moodlehq/wiki-rag on GitHub](https://github.com/moodlehq/wiki-rag)
- [moodlehq/wiki-rag DeepWiki](https://deepwiki.com/moodlehq/wiki-rag)
