# citation-genealogy

A Claude skill that traces the intellectual ancestry of research papers backward from seed papers and writes a linked Obsidian vault where each edge says *why* two papers connect — what was inherited, what was rejected, and which limitations are still open.

## Install

See `INSTALL.md` (`./install.sh` or `./install.sh --project`).

## Use

Just describe the task — the skill triggers on intent, you don't invoke it by name:

```
Trace the background of 10.1145/3292500 two generations back
and write notes into ~/vault/Literature/
```

```
I have three PDFs in ./papers/. Build me a genealogy and tell me
which limitations nobody has solved.
```

## Zotero

Not required to run — the skill works from DOIs and PDFs alone. But if a write-capable Zotero MCP server is connected (e.g. `54yyyu/zotero-mcp`), the skill adds *every confirmed paper* to your Zotero library as it traces, deduplicating by DOI and using the Better BibTeX key Zotero assigns as the paper's citekey. A read-only MCP still gets you library/PDF/annotation reads, just not the auto-add. Without any Zotero MCP, papers are traced normally but flagged `zotero: not-added` in their notes. All options are local-first community projects; see `references/data-sources.md`.

## The script

`scripts/fetch_refs.py` needs only Python 3.9+ and stdlib. It was written without network access to the citation APIs, so the scoring logic is tested but the API response parsing is not. Expect to fix a field name on first run:

```bash
python3 scripts/fetch_refs.py 10.1038/nature14539 --top 20
python3 scripts/fetch_refs.py 10.1038/nature14539 --source openalex --mailto you@example.com
```

Using `--mailto` with OpenAlex puts you in the polite pool and is much more reliable.

## The one rule

The skill forbids writing any citation from model memory. Every node traces to a PDF bibliography, an API response, or your Zotero library. Unconfirmed papers land in the hub note under "Unverified leads" as search suggestions — never as linked notes.

This is the constraint that makes the output trustworthy. If you edit the skill, keep it.
