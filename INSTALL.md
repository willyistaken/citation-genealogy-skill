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
- Optional: a Zotero MCP server (below) if you want papers auto-added to Zotero.

## Zotero MCP (optional)

Needed only for the auto-add-to-Zotero step (SKILL.md step 4). Without it, the skill still traces the genealogy, just marks each paper `zotero: not-added`.

**`54yyyu/zotero-mcp`** — simplest write-capable option:

```bash
uv tool install zotero-mcp-server   # or: pip install / pipx install zotero-mcp-server
zotero-mcp setup                    # auto-configures Claude Code
```

Needs Zotero 7+ running with *Settings → Advanced → "Allow other applications on this computer to communicate with Zotero"* enabled. For writes, also generate a [Zotero API key](https://www.zotero.org/settings/keys) (`library:write`) and your numeric user ID from that same page — `zotero-mcp setup` prompts for both.

Verify with `/mcp` in Claude Code — `zotero` should show as connected.

Alternatives (tradeoffs in `references/data-sources.md`):
- `richardjlyon/zotero-mcp` — `cargo install zotero-mcp` (needs Rust). Also does Claude.ai web via OAuth 2.1, but that HTTP mode is macOS-only out of the box.
- `zotero-fulltext` — read-only, lighter weight; skip it if you want the auto-add step.

## Uninstall

```bash
rm -rf ~/.claude/skills/citation-genealogy       # personal
rm -rf ./.claude/skills/citation-genealogy       # project
```
