#!/usr/bin/env bash
# SessionStart (compact) hook — re-inject PROJECT.md into Claude's context after compaction.
#
# Registration in settings.json under hooks.SessionStart, matcher "compact":
#   { "matcher": "compact", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs post-compact" }] }
#
# Exit 0 always. On SessionStart, stdout from exit 0 is added to Claude's context;
# no output (PROJECT.md absent or empty) means the session continues normally.

set -euo pipefail
cat /dev/stdin > /dev/null

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
[ -z "$PROJECT_DIR" ] && exit 0

PROJECT_MD="$PROJECT_DIR/PROJECT.md"
[ -f "$PROJECT_MD" ] || exit 0
[ -s "$PROJECT_MD" ] || exit 0

echo "=== PROJECT.md reloaded after context compaction ==="
cat "$PROJECT_MD"
exit 0
