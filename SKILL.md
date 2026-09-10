---
name: citation-genealogy
description: Build a linked Obsidian vault tracing the intellectual ancestry of research papers — backward citation tracing from seed papers, with each edge labelled by what was built on, what was broken from, and which limitations remain open. Use this whenever the user wants to understand the historical context or background of a paper, asks how a research area developed, wants to trace what a paper builds on, mentions a "citation graph" / "paper genealogy" / "lineage" / "family tree" of papers, wants literature-review notes with wikilinks or Zotero citekeys, or asks which limitations in a field are still unaddressed. Also use for "help me understand where this paper came from" or "what should I read before this paper", even when Obsidian and Zotero are never mentioned.
---

# Citation Genealogy

Trace a research lineage backward from seed papers and emit an Obsidian vault where the links carry meaning. A plain citation graph tells you *that* two papers connect. This produces a vault that tells you *why*: what was inherited, what was rejected, which stated limitation of the ancestor the descendant exists to fix, and which limitations nobody has fixed yet.

The last of those is the real payoff. A limitation that appears in a 2015 paper, is restated in 2019, and is still open in 2024 is a research gap with a documented history — and that is far more defensible in a related-work section than "little attention has been paid to X."

## The provenance rule

**Never write a citation, reference edge, or bibliography entry from your own memory.** Model recall of citations is unreliable in a specific and dangerous way: it produces the right-sounding author with the right-sounding year attached to a paper that does not exist, or attaches a real paper to a claim it never made. One fabricated ancestor corrupts every downstream branch of the genealogy, and the user will not catch it until a reviewer does.

Every node and every edge must trace to one of:

1. The reference list inside a PDF you have actually read.
2. An OpenAlex, Semantic Scholar, or Crossref API response you have actually received.
3. The user's Zotero library — including items this run just added to it (see step 4 of the loop, below). A Zotero item created from an API response is still that API response; it does not become a fourth, independent source.

If a paper feels load-bearing but you cannot confirm it from one of those sources, write it into the hub note under `## Unverified leads` as a search suggestion for the user. Do not give it a note file, a citekey, or a link. Notes and links are reserved for confirmed nodes.

Reading a paper's related-work prose and reporting what it says about prior work is fine and expected — that is reading, not recall. Resolving that prose to a specific bibliographic entry requires the bibliography.

## Before starting

Establish four things. Ask if unclear rather than assuming — a wrong guess here wastes a lot of downstream work.

- **Seeds.** 1–5 papers, as DOIs, arXiv IDs, Zotero citekeys, or PDFs. Fewer, well-chosen seeds beat more.
- **Depth.** Default 2 generations back. Go to 3 only if generation −2 is still clearly "modern" work rather than foundational.
- **Vault path.** Where to write. If unknown, write to `./citation-genealogy-output/` and tell the user to move it.
- **Available access.** Check for a Zotero MCP server — and specifically whether it can *write* (create items), because this skill puts every confirmed paper into Zotero as it traces (see step 4). Then check for PDFs on disk, then fall back to open APIs. See `references/data-sources.md`. If only a read-only Zotero MCP, or none, is connected, say so before starting: the run will still work, but every paper landing in Zotero is the point, and a run without write access is a degraded one, not the normal path.

## The loop

### 1. Read the seeds

For each seed, extract into the note template: problem, contribution, method in one line, and — critically — **stated limitations**, quoted position and section noted so the user can verify. Also extract the related-work framing: which prior approaches does the paper name, and does it position itself as extending them or rejecting them?

Authors' own limitations sections are gold and consistently under-used. They tell you exactly what the field's open problems were at that moment, in the authors' own judgment.

### 2. Pull real reference lists

Use the highest-fidelity source available. **Semantic Scholar's references endpoint is the best tool for this specific job** because it returns `contexts` (the sentences where the citation appears) and `intents` (background / method / result). That lets you type edges from evidence instead of guessing. See `references/data-sources.md` for exact queries and `scripts/fetch_refs.py` for a starting script.

### 3. Select what to trace

A bibliography has 40–80 entries; roughly 5 matter for genealogy. Score each candidate:

| Signal | Weight |
|---|---|
| Cited in intro or methods, not only discussion | high |
| Semantic Scholar intent is `methodology` | high |
| Cited alongside language of dependence or rejection ("following", "unlike", "in contrast to", "we build on") | high |
| Cited by two or more of your seeds independently | very high — convergence marks the trunk |
| Author self-citation | medium, and note it as such |
| Cited once in a list of many, no discussion | drop |
| Cited only for a dataset, benchmark, or tool | drop unless the dataset itself is the topic |

Take the top 3–7 per paper. **Show the user the shortlist and the scores before recursing** — this is the "broad but not too broad" decision, and it is theirs to make, not yours. Recursing on a bad shortlist wastes a generation of work.

### 4. Add every confirmed paper to Zotero

Every paper that survives step 3 (plus every seed) gets a Zotero item before it gets a note — the note's citekey comes *from* Zotero, not from you:

1. Search Zotero by DOI (or arXiv ID) first. Already there? Use its existing Better BibTeX key and move on — never create a duplicate.
2. If it's absent, create the item using the metadata you already fetched from Semantic Scholar, OpenAlex, or the PDF — title, authors, year, DOI. Do not hand-retype from memory or fill in a field you don't actually have.
3. Attach the PDF if one is on disk.
4. Read back the Better BibTeX key Zotero assigns to the new item, and use that key, verbatim, as the note's `citekey` and filename.
5. If the write fails — no write-capable MCP, a permission error, a rate limit — do not silently drop the paper from the vault. Mark its frontmatter `zotero: not-added`, keep tracing it, and list it under coverage gaps in the hub note.

See `references/data-sources.md` for which Zotero MCP options actually support writes.

### 5. Type every edge

An untyped link is nearly worthless in a graph view. Use this vocabulary, and always with a clause saying what specifically:

- `builds-on` — inherits machinery. *"inherits the encoder, replaces the objective"*
- `breaks-from` — explicitly rejects an assumption. *"rejects the stationarity assumption"*
- `addresses-limitation` — exists to fix a named limitation of the ancestor. The strongest edge type; always try to resolve to a specific `L#` in the ancestor's note.
- `supersedes` — same problem, strictly better result
- `contradicts` — incompatible empirical claim. Flag these prominently; they are often the most interesting thing in the vault.
- `borrows-method-from` — cross-domain method import, no shared problem

### 6. Recurse, then stop

Stop a branch when any of these hit, and say which one in the hub note:

- Target depth reached
- Branches converge — several paths land on the same ancestor. This is the strongest signal and usually means you have found the trunk.
- The ancestor is a textbook, survey, or pre-1990 foundational work
- Citations become purely methodological plumbing rather than intellectual lineage

## Output structure

```
<vault>/Literature/<topic>/
├── _Hub.md                  narrative spine + mermaid graph — write this last
├── _Frontier.md             limitations still unaddressed
├── Papers/<citekey>.md      one per confirmed paper
└── Limitations/<slug>.md    only for limitations tracked across 3+ papers
```

Promote a limitation to its own note only when it recurs across three or more papers. Then Obsidian's graph shows every paper touching that problem, which is the view that makes a research gap visible. Below that threshold it is note-explosion for nothing.

`_Hub.md` opens with a mermaid diagram of every confirmed node and typed edge, before any prose thread — once there are more than a couple of branches, that graph is what actually shows the shape of the genealogy; the per-thread prose exists to explain *why*, not to re-describe the *what*. Keep "The short version" to 2–3 sentences; it is an orientation line for the graph and the trunk, not a summary of the whole vault. See the `_Hub.md` template for the exact conventions (arrow direction, edge labels, styling contradictions, splitting the graph past ~15–20 nodes).

Use exact templates from `references/note-templates.md`. Do not improvise the frontmatter — the user may build Dataview queries against it.

## Reporting back

End with a short summary in chat, not just files — but short means short: a handful of tight bullets, not paragraphs. The full narrative already lives in `_Hub.md`; the chat reply points at it, it doesn't repeat it. Cover, tersely: the trunk papers the branches converged on, the two or three most durable open limitations with their year spans, any contradictions found, every gap where you could not get a reference list, and the Zotero tally (added / already-present / `not-added`, and why). Be explicit about coverage failures even in a terse report — a paywalled paper whose bibliography you could not read is a hole in the genealogy, and silence about it is worse than the hole.

## Updating an existing vault

The loop above builds a vault from scratch. These are the follow-up operations on one that already exists — reopen its `_Hub.md` first to load the current trunk, generations, and open limitations before changing anything. Every rule from the loop still applies here: no citation from memory, real reference lists only, edges typed, papers added to Zotero (step 4).

### Add a paper

Whether it's a seed you forgot, something someone pointed you to, or a paper published since the original trace:

1. Confirm it the normal way — PDF, API response, or Zotero. Work out how it connects to what's already there: ancestor of an existing node, descendant (cites / extends / addresses a limitation of something already in the vault), or an unconnected new seed.
2. Run it through step 4 (Zotero) and write `Papers/<citekey>.md` from the template, with `generation` set relative to the *original* seeds — not relative to whichever node led you to it.
3. Type the edge in both notes — the new note's `Ancestry` (or `Descendants`) section, and the matching section of the node it connects to. A one-sided link is a bug.
4. If it resolves a limitation, resolve it at the source: add `→ addressed by [[new-citekey]]` under that `L#`/`U#` in the ancestor's note, and move the entry in `_Frontier.md` to "Resolved during tracing."
5. Update `_Hub.md` — add the node and edges to the mermaid graph, extend or add a lineage thread, and recheck the trunk. A new paper occasionally creates a second convergence point.

### Log a limitation you noticed

This is your own critical reading — not the authors' words, not a citing paper's critique — so keep it visibly distinct from both by ID. In the note's `## Limitations not stated by the authors` section, add it as `U#` (author-stated limitations stay `L#`; never merge the two sequences — the prefix is what tells a reader whose judgment this is, at a glance):

```markdown
- **U1: Training data license is unclear despite claims of "open" release.** (noted by user, 2026-09-10)
```

A `U#` is a first-class limitation everywhere an `L#` is: link it from `_Frontier.md`, cite it from another note as `smith2019::U1`, and if it recurs across 3+ papers it can anchor a `Limitations/<slug>.md` note like any other — the promotion rule only counts recurrence, not who noticed it first.

### Extend the trace further

Two different things people mean by this — ask which, if it isn't obvious from context:

- **Go deeper.** Treat the current deepest generation as the new seed layer and run steps 2–6 one more hop back. Generation numbers keep counting down from the *original* seeds, so an existing generation −2 node's newly-found ancestor becomes generation −3, not −1.
- **Check for resolutions.** Vaults go stale — a limitation marked open may since have been addressed. Run a forward citation search (Semantic Scholar `/citations` on the node holding the limitation, see `references/data-sources.md`) and check what engages with it. Anything confirmed follows "Add a paper" above; anything merely suggestive goes to `_Hub.md`'s Unverified leads, not a note.

Either way: update `_Hub.md`'s `traced` date and mermaid graph, and rerun the trunk/convergence check — more generations, or a resolved limitation, can surface a convergence that wasn't visible before.

## Reference files

- `references/data-sources.md` — API queries, Zotero MCP options, paywall fallbacks
- `references/note-templates.md` — exact templates for all four note types
- `scripts/fetch_refs.py` — OpenAlex/Semantic Scholar reference fetcher. Unverified starting point; expect to fix it on first run and check the response shape against current API docs before trusting output.
