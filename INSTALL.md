# Install

```bash
./install.sh            # personal — ~/.claude/skills, all projects
./install.sh --project  # this project only — ./.claude/skills, committable
```

Or manually:

```bash
mkdir -p ~/.claude/skills && cp -r citation-genealogy ~/.claude/skills/
```

Then restart Claude Code and run `/skills` to verify it registered.

## Requirements

- Python 3.9+ (stdlib only) if you'll use `scripts/fetch_refs.py`
- Optional: a Zotero MCP server — read-write (e.g. `54yyyu/zotero-mcp`) if you want papers auto-added to Zotero, read-only otherwise. See `references/data-sources.md`.

## Uninstall

```bash
rm -rf ~/.claude/skills/citation-genealogy       # personal
rm -rf ./.claude/skills/citation-genealogy       # project
```
