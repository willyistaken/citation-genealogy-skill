#!/usr/bin/env bash
# Install citation-genealogy into Claude Code.
# Usage: ./install.sh [--project]
#   (default)   install to ~/.claude/skills   (all projects)
#   --project   install to ./.claude/skills   (this project only)

set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="citation-genealogy"

case "${1:-}" in
  --project) DEST="./.claude/skills" ;;
  "")        DEST="$HOME/.claude/skills" ;;
  *)         echo "Usage: $0 [--project]" >&2; exit 1 ;;
esac

mkdir -p "$DEST"
rm -rf "${DEST:?}/$NAME"
cp -r "$SRC" "$DEST/$NAME"
rm -f "$DEST/$NAME/install.sh"

echo "Installed to $DEST/$NAME"
echo "Restart Claude Code, then run /skills to verify."
