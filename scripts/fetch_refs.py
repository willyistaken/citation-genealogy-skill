#!/usr/bin/env python3
"""Fetch a paper's reference list from Semantic Scholar or OpenAlex.

Starting point, not a finished tool. It was written without network access to
either API, so verify the response shape on first run before trusting output.
If a field is missing, check current API docs rather than guessing.

Usage:
    python fetch_refs.py 10.1038/nature14539
    python fetch_refs.py 10.1038/nature14539 --source openalex --mailto you@example.com
    python fetch_refs.py arXiv:1706.03762 --json refs.json

Prints a ranked table. Ranking is a rough prior on which references are
load-bearing; it is NOT a substitute for reading citation contexts. Always show
the shortlist to the user before recursing.
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

S2 = "https://api.semanticscholar.org/graph/v1"
OA = "https://api.openalex.org"

# Phrases that signal intellectual dependence or rejection rather than
# a passing mention. Matched against citation context sentences.
LINEAGE_CUES = [
    "we build on", "building on", "we follow", "following", "we extend",
    "extends", "based on", "adapted from", "unlike", "in contrast to",
    "differs from", "we depart from", "rather than", "fails to",
    "limitation of", "shortcoming",
]


def get(url, tries=3):
    """GET and parse JSON, backing off on rate limits."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "citation-genealogy/0.1"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < tries - 1:
                wait = 3 * (attempt + 1)
                print(f"  rate limited, waiting {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"HTTP {e.code} for {url}", file=sys.stderr)
            return None
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as e:
            print(f"Request failed: {e}", file=sys.stderr)
            return None
    return None


def normalize_id(raw):
    """Turn a user-supplied identifier into an S2 paper ID."""
    raw = raw.strip()
    low = raw.lower()
    if low.startswith("arxiv:"):
        return "ARXIV:" + raw.split(":", 1)[1]
    if low.startswith("doi:"):
        return "DOI:" + raw.split(":", 1)[1]
    if raw.startswith("10."):
        return "DOI:" + raw
    return raw


def from_semantic_scholar(paper_id):
    fields = "title,year,authors,externalIds,citationCount,contexts,intents,isInfluential"
    url = f"{S2}/paper/{urllib.parse.quote(paper_id)}/references?fields={fields}&limit=100"
    data = get(url)
    if not data or "data" not in data:
        return None

    out = []
    for item in data.get("data", []):
        cited = item.get("citedPaper") or {}
        if not cited.get("title"):
            continue  # unresolvable stub
        ids = cited.get("externalIds") or {}
        out.append({
            "title": cited["title"],
            "year": cited.get("year"),
            "authors": [a.get("name", "") for a in (cited.get("authors") or [])][:3],
            "doi": ids.get("DOI"),
            "arxiv": ids.get("ArXiv"),
            "citation_count": cited.get("citationCount"),
            "intents": item.get("intents") or [],
            "contexts": item.get("contexts") or [],
            "influential": bool(item.get("isInfluential")),
            "source": "semantic-scholar",
        })
    return out


def from_openalex(doi, mailto=None):
    suffix = f"?mailto={mailto}" if mailto else ""
    root = get(f"{OA}/works/doi:{doi}{suffix}")
    if not root:
        return None
    ref_ids = [u.rstrip("/").split("/")[-1] for u in root.get("referenced_works", [])]
    if not ref_ids:
        print("No referenced_works — the publisher may not have deposited references.",
              file=sys.stderr)
        return []

    select = "id,doi,display_name,publication_year,authorships,cited_by_count"
    out = []
    for i in range(0, len(ref_ids), 50):
        chunk = "|".join(ref_ids[i:i + 50])
        params = {"filter": f"ids.openalex:{chunk}", "per-page": "50", "select": select}
        if mailto:
            params["mailto"] = mailto
        page = get(f"{OA}/works?{urllib.parse.urlencode(params)}")
        if not page:
            continue
        for w in page.get("results", []):
            authors = [
                (a.get("author") or {}).get("display_name", "")
                for a in (w.get("authorships") or [])
            ][:3]
            out.append({
                "title": w.get("display_name"),
                "year": w.get("publication_year"),
                "authors": authors,
                "doi": (w.get("doi") or "").replace("https://doi.org/", "") or None,
                "arxiv": None,
                "citation_count": w.get("cited_by_count"),
                "intents": [],
                "contexts": [],
                "influential": False,
                "source": "openalex",
            })
        time.sleep(0.2)
    return out


def score(ref):
    """Rough prior on genealogical load-bearing-ness. Heuristic, not truth."""
    s = 0.0
    reasons = []

    if "methodology" in ref["intents"]:
        s += 3
        reasons.append("method")
    if "background" in ref["intents"]:
        s += 1
        reasons.append("background")
    if ref["influential"]:
        s += 2
        reasons.append("s2-influential")

    blob = " ".join(ref["contexts"]).lower()
    hits = [c for c in LINEAGE_CUES if c in blob]
    if hits:
        s += 2
        reasons.append(f"cue:{hits[0]}")

    # Multiple citation contexts means it is discussed, not just listed.
    if len(ref["contexts"]) >= 3:
        s += 1.5
        reasons.append("discussed-repeatedly")

    # Well-cited older work is more likely foundational.
    cc = ref.get("citation_count") or 0
    if cc > 1000:
        s += 1
        reasons.append("highly-cited")

    ref["score"] = s
    ref["reasons"] = reasons
    return s


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("paper", help="DOI, arXiv:ID, or Semantic Scholar ID")
    p.add_argument("--source", choices=["semantic-scholar", "openalex", "auto"],
                   default="auto")
    p.add_argument("--mailto", help="Email for the OpenAlex polite pool (recommended)")
    p.add_argument("--json", help="Also write full results here")
    p.add_argument("--top", type=int, default=15, help="Rows to print (default 15)")
    args = p.parse_args()

    refs = None
    if args.source in ("auto", "semantic-scholar"):
        refs = from_semantic_scholar(normalize_id(args.paper))
        if refs:
            print(f"Semantic Scholar: {len(refs)} references\n", file=sys.stderr)

    if not refs and args.source in ("auto", "openalex"):
        doi = args.paper.split(":", 1)[-1] if args.paper.lower().startswith("doi:") else args.paper
        if not doi.startswith("10."):
            print("OpenAlex lookup needs a DOI.", file=sys.stderr)
            return 1
        refs = from_openalex(doi, args.mailto)
        if refs:
            print(f"OpenAlex: {len(refs)} references (no contexts — scores are weak)\n",
                  file=sys.stderr)

    if not refs:
        print("No references retrieved. Fall back to the PDF bibliography.", file=sys.stderr)
        return 1

    refs.sort(key=score, reverse=True)

    print(f"{'#':<4}{'score':<7}{'year':<6}{'title':<58}why")
    print("-" * 100)
    for i, r in enumerate(refs[:args.top], 1):
        title = (r["title"] or "")[:56]
        why = ",".join(r["reasons"]) or "-"
        print(f"{i:<4}{r['score']:<7.1f}{str(r['year'] or '?'):<6}{title:<58}{why}")

    print("\nScores are a prior, not a verdict. Read the contexts before recursing.",
          file=sys.stderr)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(refs, f, indent=2)
        print(f"Wrote {args.json}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
