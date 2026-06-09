---
name: paper-summary
origin: workshop
description: |
  Produce a structured summary of an academic paper from its PDF, in
  the workshop's literature/<bibkey>.md format. Use when the user has
  a new paper to add to the project's literature/ directory, asks
  "what does this paper say?", or asks for a structured intake of a
  PDF for the lab. Always pair with a verified BibTeX entry; never
  emit citations from memory.
---

# Paper-summary skill

Use this skill when:

- The user provides a PDF of a paper and asks for a summary.
- The user is adding a new entry to `literature/`.
- The user asks for a structured intake or a 1-page brief of a paper.

## How to invoke

1. Read the PDF using the built-in `pdf` skill. Extract text, abstract, section headings, and any display equations relevant to the contribution.
2. **Verify the citation.** Use an `arxiv` or `semantic-scholar` MCP if available. If neither is available, fall back to extracting the title/authors/year from the PDF metadata or first page; mark the BibTeX as `unverified` until the user confirms.
3. Fill the template below. Use literal quotes from the PDF for *Pull-quotes*; paraphrase drops the qualifier that matters.
4. Save to `literature/<bibkey>.md` where `<bibkey>` is `firstauthor-year` (e.g., `wachter-biegler-2006`).
5. If a project `MEMORY.md` exists and the paper is being added because of an active decision, ask the user whether to add a citation in the relevant `MEMORY.md` section.

## Template

The output file must have this structure exactly. Sections marked with † are required; others may be omitted with a `*not applicable*` note.

```markdown
# <Paper Title>

**Authors:** <names>
**Year:** <yyyy>
**Venue:** <journal/conference/preprint>
**BibTeX key:** <firstauthor-year>
**DOI / arXiv ID:** <link>
**Verified via:** <arxiv|semantic-scholar|local PDF metadata|unverified>

## Contribution (one paragraph) †

What does this paper claim, in plain language. One paragraph; no equations.

## Main result †

The headline theorem or method. State precisely; quote the assumptions verbatim.

## Assumptions †

The conditions under which the main result holds. Quote where possible.

## Method / proof sketch

The core technique. Optional but useful.

## Limitations

What the paper does NOT claim. Often in the conclusion or future-work section.

## Fit to our problem †

Why we read this paper. What we will use from it. What we won't.

## Pull-quotes

Up to five literal quotes (page numbers in parentheses) for sentences we
might want to cite or refute. Each quote in quotation marks.

## BibTeX

```bibtex
@article{<bibkey>,
  author  = {...},
  title   = {...},
  journal = {...},
  year    = {...},
  doi     = {...},
}
```
```

## Constraints

- **Never emit a citation from memory.** If the citation cannot be verified, the BibTeX block must be marked `unverified` and the user must be told.
- **Pull-quotes must be literal.** No paraphrasing. Page numbers required. If the source has no page numbers (preprint, web), use section IDs.
- **Fit to our problem must reference the project's `MEMORY.md` or `plans/` if relevant.** A paper read for no reason is a paper that won't be cited.
- **Don't summarize what you can't verify.** If the PDF text extraction is partial (scanned PDF, OCR errors), say so explicitly and stop.

## Example output

See `examples/example-output.md` for a complete worked summary in the right shape.
