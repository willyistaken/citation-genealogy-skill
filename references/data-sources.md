# Data sources

Ordered by fidelity. Prefer earlier sources; fall back only as needed, and record which source each edge came from.

## 1. The PDF's own bibliography

Highest fidelity, because the reference list is the ground truth and the surrounding prose tells you *why* the citation is there. Requires the PDF.

Extract text, then locate the bibliography and the in-text citation contexts. Match in-text markers back to entries so you know which section each reference was cited in — that section is your main selection signal.

Worth the effort for seeds. Too slow for every node at depth 2; use APIs there.

## 2. Semantic Scholar Graph API

**The best API for this task**, because it returns citation *contexts* and *intents* — you can type edges from evidence rather than inference.

```
GET https://api.semanticscholar.org/graph/v1/paper/DOI:10.1038/nature14539/references
    ?fields=title,year,authors,externalIds,citationCount,contexts,intents,isInfluential
    &limit=100
```

- `contexts` — the actual sentences where the citation appears. Feed these into edge typing.
- `intents` — `background`, `methodology`, or `result`. A `methodology` intent is a strong genealogy signal.
- `isInfluential` — the API's own guess at load-bearing citations. Useful as a tiebreaker, not as the primary filter; it is opaque and sometimes wrong.

Paper IDs accept `DOI:`, `ARXIV:`, `CorpusId:`, or a bare S2 hash. Forward direction is `/citations` instead of `/references` — useful for step 4 of the loop, finding who addressed a limitation.

No key needed at low volume; rate limits are tight, so batch and sleep. A key raises them.

## 3. OpenAlex

Best coverage and the most permissive limits. No contexts, so weaker for edge typing, but excellent for structure and convergence detection.

```
GET https://api.openalex.org/works/doi:10.1038/nature14539
```

`referenced_works` is an array of OpenAlex IDs. Batch-resolve them:

```
GET https://api.openalex.org/works?filter=ids.openalex:W123|W456|W789&per-page=50
```

Add `?mailto=your@email.com` for the polite pool and much better reliability. Use `select=id,doi,display_name,publication_year,authorships,cited_by_count` to keep responses small.

Verify field names against current docs before relying on them — the schema has changed across versions.

## 4. Crossref

Metadata and DOI resolution. `reference` lists exist but only when the publisher deposited them, which is inconsistent. Good for cleaning up bibliographic details, weak for graph building.

## 5. Zotero

Two roles: reading what's already in the library (PDFs, annotations — a direct signal of what the user already thinks matters), and, per this skill's workflow, *writing* every confirmed paper into the library as it's traced. The first role works with any Zotero MCP; the second needs a write-capable one.

No official Anthropic connector exists. Community options, all local-first:

- `zotero-fulltext` — lightweight, local API, fulltext on demand, low token use. **Read-only** — cannot do the add-to-Zotero step in the loop.
- `54yyyu/zotero-mcp` — feature-rich, **read-write**, optional semantic search, heavier deps. The one to use if you want papers added automatically.
- `richardjlyon/zotero-mcp` — built for the Zotero↔Obsidian gap; supports HTTP + OAuth so it also works from Claude.ai web. Check its current docs for write support before relying on it for the add step.

These are volunteer projects with overlapping scope and uneven maintenance. Check the repo is alive before depending on it.

Better BibTeX is worth installing regardless — it gives stable citekeys, which are what the notes key on, and which this skill reads back after creating an item.

### Adding a confirmed paper to Zotero

1. Search first, by DOI or arXiv ID. If the paper is already in the library, use its existing Better BibTeX key and stop here — never create a duplicate item.
2. If it's absent, create the item from metadata already fetched from Semantic Scholar, OpenAlex, or the PDF — title, authors, year, DOI. Never hand-retype from memory, and never invent a field you don't have.
3. Attach the PDF if one is on disk.
4. Read back the Better BibTeX key the new item gets assigned; that key becomes the note's `citekey` and filename.
5. If the create call fails (no write access, permission error, rate limit), don't drop the paper from the vault — set `zotero: not-added` in its frontmatter, keep tracing it with a citekey you derive yourself (`lastname+year`), and record it as a coverage gap in the hub note.

## Paywalls

You will hit papers you cannot read. Options in order: check for an author preprint (arXiv, institutional repository, lab page); use the abstract plus Semantic Scholar contexts from *citing* papers, which often summarise the limitation better than the original does; ask the user, who may have institutional access.

**Never fill a gap by inference.** Mark the node `access: metadata-only` and say so in the hub note. A genealogy with declared holes is usable. One with invented content is not.
