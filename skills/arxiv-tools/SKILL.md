---
name: arxiv-tools
description: >
  This skill should be used when the user asks to "search for papers",
  "get paper info", "download LaTeX source", "generate BibTeX citation",
  "find citing papers", or provides an arXiv ID or arXiv URL.
---

# arXiv Paper Search and Analysis

Six subcommands available: search (find papers), info (metadata), tex (download full text), infotex (info + tex combined), bib (BibTeX), cited (reverse citation lookup).

## How to run

Script dependencies are declared in inline metadata at the top of the file — you are responsible for installing them yourself.

## Subcommands

### search — find papers

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" search "keywords"
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" search "keywords" --max 10
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" search "keywords" --source s2|openalex|arxiv
```

S2-specific filter parameters:

```bash
--year 2024                    # single year
--year 2020-2024               # year range
--fields-of-study "Computer Science,Physics"
--pub-types "JournalArticle,Conference"
--min-citations 50
--venue "NeurIPS"
--open-access                  # open-access only
```

S2 bulk search (up to 1000 results, supports sorting and pagination):

```bash
--bulk --sort "citationCount:desc"
--bulk --token <token from previous page>   # pagination
```

### info — get paper metadata (does not download tex)

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" info <arXiv ID>
```

Prints the metadata (title, authors, date, categories, PDF URL, abstract).

### tex — download full paper source

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" tex <arXiv ID>
```

Downloads the tex source and returns the directory path and structure, preserving full LaTeX formatting and figures. If the source is unavailable, falls back to PDF download and text extraction.

### infotex — info + tex combined

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" infotex <arXiv ID>
```

Runs `info` then `tex` in sequence on a single paper. Use this when you want both the at-a-glance context and the full text in one shot.

### bib — generate BibTeX citation

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" bib <arXiv ID>
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" bib <arXiv ID> -o references.bib  # append to file
```

### cited — reverse citation lookup

Find which papers cite a given paper.

```bash
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" cited <arXiv ID>
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" cited <arXiv ID> --max 50
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" cited <arXiv ID> --offset 20         # pagination
uv run "${CLAUDE_PLUGIN_ROOT}/skills/arxiv-tools/arxiv_tool.py" cited <arXiv ID> --source s2|openalex
```

## Data source fallback

| Subcommand | Fallback order |
|------------|---------------|
| search | S2 → OpenAlex → arXiv |
| cited | S2 → OpenAlex |
| info / bib | local cache → OpenAlex → S2 → arXiv |
| tex | local cache → arXiv |
| infotex | info fallback, then tex fallback (runs sequentially) |

- search/cited prefer S2: more complete citation data
- info/bib prefer OpenAlex: most lenient rate limit (0.1s/req vs S2 2s vs arXiv 5s)
