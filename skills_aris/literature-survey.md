# Literature Survey

## Multi-source coverage

Use multiple sources in priority order. All are optional — if not configured, skip silently and fall back to the next. Never fail because a source is not configured. Zotero / Obsidian tool names vary by user's MCP config — try common patterns and adapt.

| Priority | Source | What it provides |
|----------|--------|-----------------|
| 1 | Zotero (MCP) | Collections, tags, annotations, PDF highlights, BibTeX |
| 2 | Obsidian (MCP) | Research notes, paper summaries, tagged references, wikilinks |
| 3 | Local PDFs | Raw PDF content (first 3 pages) |
| 4 | Web search | arXiv, Google Scholar, Semantic Scholar |
| 5 | Semantic Scholar API | Published venue papers (IEEE, ACM, Springer) with citation counts, venue info, TLDR |
| 6 | DeepXiv CLI | Progressive paper retrieval: search → brief → head → section |
| 7 | Exa | AI-powered broad web search with content extraction; blogs/docs/news beyond arXiv |
| 8 | Gemini (MCP/CLI) | AI-driven broad discovery — decomposes topics into sub-problems, aliases, variants |
| 9 | OpenAlex | Open citation graph + institutional affiliations + funding data + cross-discipline metadata |

## Why each explicit source

- **Semantic Scholar**: many IEEE / ACM journal papers are NOT on arXiv; S2 fills that gap with citation counts and venue metadata.
- **DeepXiv**: when a broad search should be followed by staged reading instead of full-paper loading.
- **Exa**: AI-powered search across blogs, docs, news, company pages — fills the gap between academic databases and generic WebSearch.
- **Gemini**: AI-driven discovery beyond keyword matching — decomposes topics into sub-problems, aliases, variants; surfaces papers traditional APIs miss. Do not trust Gemini-reported citation counts — use S2 for authoritative numbers.
- **OpenAlex**: fully open citation graph (no API key), institutional + funding metadata, cross-discipline coverage.

## Scan local first

Before searching online, scan the user's local library (Zotero, Obsidian, `papers/`, `literature/`):

- Locate library; filter by relevance via filename + first-page content.
- For each relevant local PDF, read first 3 pages; extract title / authors / year / core contribution / relevance.
- Flag directly-related vs tangentially-related.
- De-duplicate against Zotero / Obsidian.
- Compile into "papers you already have" — external search fills the gaps.

Zotero annotations and Obsidian notes are gold — they represent the user's **processed understanding**, more valuable than raw paper content.

## External search

- Focus on **top venues in the last 2 years** and **arXiv preprints in the last 6 months** unless studying foundational work.
- Use **5+ different query formulations** per topic; a single query doesn't sample the landscape.
- De-duplicate against Zotero, Obsidian, and local library.

When asking Gemini for broad discovery, instruct it to:

- Search from MULTIPLE angles — decompose into sub-problems, aliases, neighboring tasks, common benchmark variants.
- Prefer genuinely relevant papers, not keyword-adjacent ones.
- Include top venues, journals, surveys, recent preprints, papers with code.
- Focus on papers from 2022 onward unless older foundational work is necessary.
- Per paper, return: Title, Authors, Year, Venue, arXiv ID, DOI, Code URL, one-sentence Summary. Aim for at least 15 papers.

## Reference paper mode

When the user provides a reference paper as context ("improve on this paper" / "find related to this"), narrow the search: look for related and competing work to the reference paper, not the full landscape. Downstream idea generation should produce ideas that build on or improve the reference paper.

## What to look for inside each paper

- **Future Work sections** — these often name the open problems the authors themselves see.
- **Recurring limitations** mentioned by multiple papers — high-density gap signals.
- **Read abstracts and introductions** of the top 10-15 papers; for any potentially overlapping paper, also read the related work section.

## Structural gap patterns

When mapping the landscape for ideation, look for these five patterns:

- Methods that work in **domain A** but haven't been tried in **domain B**.
- **Contradictory findings** between papers (opportunity for resolution).
- **Assumptions that everyone makes** but nobody has tested.
- **Scaling regimes** that haven't been explored.
- **Diagnostic questions** that nobody has asked.

## Per-paper analysis

For each relevant paper extract:

- **Problem**: what gap does it address?
- **Method**: core technical contribution (1-2 sentences).
- **Results**: key numbers / claims.
- **Relevance**: how does it relate to our work?
- **Source**: where we found it (Zotero / Obsidian / local / web) — helps the user know what they already have vs what's new.

## Synthesis

- Group papers by approach / theme.
- Identify consensus vs disagreements in the field.
- Find gaps that our work could fill.
- If Obsidian notes exist, incorporate the user's own insights into the synthesis.

## Honesty

- Always include paper citations (authors, year, venue).
- Distinguish peer-reviewed from preprints.
- Be honest about each paper's limitations.
- Note if a paper directly competes with or supports our approach.
