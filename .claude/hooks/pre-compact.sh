#!/usr/bin/env bash
# PreCompact hook — block context compaction until PROJECT.md reflects current work.
#
# Status gate: blocks only when PROJECT.md is missing or stale. If PROJECT.md was
# modified within the last FRESH_MINUTES minutes it is treated as up to date and
# compaction proceeds — this prevents the unconditional re-block loop that would
# otherwise wedge auto-compaction. After Claude updates PROJECT.md on a block, the
# next compaction attempt sees a fresh timestamp and is allowed.
#
# Registration in settings.json under hooks.PreCompact:
#   { "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs pre-compact" }] }
#
# Exit 0: PROJECT.md fresh — allow. Exit 2: missing or stale — block; STDERR fed back to Claude.

set -euo pipefail

FRESH_MINUTES=10

cat /dev/stdin > /dev/null

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
PROJECT_MD="$PROJECT_DIR/PROJECT.md"
if [ -n "$PROJECT_DIR" ] && [ -f "$PROJECT_MD" ]; then
    if [ -n "$(find "$PROJECT_MD" -mmin -"$FRESH_MINUTES" 2>/dev/null)" ]; then
        exit 0
    fi
fi

cat >&2 <<'EOF'
Before compaction: open PROJECT.md and update or create a 'Current work' section with:
  1. Current goal — one sentence.
  2. Last 3-5 completed items — include file paths.
  3. Next immediate action.
Keep the section under 200 words. Once you save PROJECT.md, compaction proceeds automatically.
EOF
exit 2
