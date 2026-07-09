# SciComSkill - Build Scientific Computing Research Skill

Starting from [scicomp-research-skills](https://github.com/a-attia/scicomp-research-skills), a set of agent skills and workflow templates for research in scientific computing -- both research papers (drafts, literature surveys, reviewer responses) and research software (libraries, codes, reproducibility infrastructure). **The goal of this project is to extend and personalize these research skills.**

## Goal

Extend [scicomp-research-skills](https://github.com/a-attia/scicomp-research-skills) by adding a new `verified-literature-search` skill that avoids traditional LLM halucination issues when creating a literature search. Posssible search criteria:
1. Set of topics/keywords, looking for matches in title abstract, useful for background compilation.
2. Search a set of authors for a given expertise, useful for finding speakers for a PI meeting.
3. Other type of searches that you feel could be useful.

Add a harness to the searches, using aspects of verified citation and background tools such as:
* Rob Ross' [ref-checker](https://github.com/rbross-hpc/ref-checker) to verify citations.
* Sven's *half-assed* [scholar-report](https://github.com/leyffer/scholar-report) to get ORCID and search for authors (requires some work, but may be useful).

## Output

The search tools should create a set of artifacts, including:
* bibtex file of references;
* latex file with short summary of literature found; and,
* json files with literature/ORCID found.

## Outcome 

A new set of agent skills that can be customized for MCS.

*Proposed by Ahmed Attia*
