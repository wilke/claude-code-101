<!--slide n=40 layout=content kicker="Literature"-->
# Literature: the fifth artifact
_Literature reading is daily work for computational mathematicians — and the highest-leverage place Claude as a co-scientist beats Claude as a programmer. Treat it as first class._

|  | Claude does well | Claude does badly |
|---|---|---|
| PDFs | Extract text, equations, tables (built-in `pdf` skill) | Decide what a result *really means* — that's still you |
| Notation | Translate between Nocedal–Wright / Conn–Gould–Toint / Boyd–Vandenberghe | Catch subtle distinctions (B- vs. M- vs. S-stationarity) without your verification |
| Citations | Resolve fragments via an `arxiv` / `semantic-scholar` lookup | Emit citations from memory — these are often **plausible-looking and wrong** |

Add `literature/` alongside `plans/`: one file per paper, named by BibTeX key. MEMORY.md decisions cite both.

```
project/
├── CLAUDE.md
├── MEMORY.md          # cites plans/ AND literature/
├── STATUS.md
├── plans/
└── literature/
    ├── wachter-biegler-2006.md
    ├── nocedal-wright-12.md
    └── INDEX.md       # contents page once it grows past ~10
```

> CLAUDE.md hard rule: `never emit a citation from memory. Resolve via a literature search, or quote the local PDF, or mark [citation needed]`. One line; the single biggest defense against hallucinated bibliographies.


<!--slide n=41 layout=content kicker="Literature"-->
# When the corpus outgrows context: RAG
Your group's PDFs, lab wiki, and shared notes don't fit in one Claude session. **Retrieval-Augmented Generation** (RAG) is the standard answer: index the corpus into a vector database; for each question, retrieve the most relevant chunks; feed only those into the model.

- You stop relying on what Claude was trained on, and start relying on what you actually have.
- Citations come back as document IDs you can verify, not paraphrases of training data.
- The corpus grows without inflating your context window.

**Concrete example: `moodlehq/wiki-rag`.** Experimental RAG that ingests any MediaWiki site via API, indexes into Milvus with hybrid (vector + keyword) retrieval and fusion reranking, exposes an *OpenAI-compatible API*, and ships a Docker image.

```
     Your lab MediaWiki  →  wiki-rag (Milvus + LangGraph)
                              │  exposes /v1/chat/completions
                              ▼
                            Custom tool wrapper
                              │  tool: query_lab_wiki(question)
                              ▼
                          Claude Code session
```

Pattern: any RAG that speaks the OpenAI API can become a Claude Code tool in ten lines. Now Claude has searchable access to your group's institutional knowledge — and so does every collaborator who runs the workshop's setup.
