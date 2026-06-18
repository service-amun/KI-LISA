#!/usr/bin/env bash
# SessionStart hook — detect project memory files and agent memory files; trigger migration.
#
# Registration in settings.json under hooks.SessionStart:
#   { "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs check-memory" }
#
# Exit 0 always. On SessionStart, stdout from exit 0 is added to Claude's context;
# no output means no memory files were found and the session proceeds normally.

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
[ -z "$PROJECT_DIR" ] && exit 0

# ── Project memory ────────────────────────────────────────────────────────────
# Claude Code encodes the project path by replacing every non-alphanumeric
# character with '-' (e.g. '/home/dev/my_app' -> '-home-dev-my-app').
ENCODED=$(printf '%s' "$PROJECT_DIR" | sed 's/[^A-Za-z0-9]/-/g')
MEM_DIR="$HOME/.claude/projects/$ENCODED/memory"

if [ -d "$MEM_DIR" ]; then
    COUNT=$(find "$MEM_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
    if [ "$COUNT" -gt 0 ]; then
        echo "$COUNT project memory file(s) detected in: $MEM_DIR"
        echo "Load .claude/skills/file-claude/SKILL.md and run the memory integration section (§5) before any other work."
    fi
fi

# ── Agent memory ──────────────────────────────────────────────────────────────
# Check all three scopes: user-level, project-level, project-local (git-ignored).
AGENT_NAMES=""
for AGENT_MEM_DIR in \
    "$HOME/.claude/agent-memory" \
    "$PROJECT_DIR/.claude/agent-memory" \
    "$PROJECT_DIR/.claude/agent-memory-local"; do
    [ -d "$AGENT_MEM_DIR" ] || continue
    for AGENT_DIR in "$AGENT_MEM_DIR"/*/; do
        [ -d "$AGENT_DIR" ] || continue
        COUNT=$(find "$AGENT_DIR" -maxdepth 1 -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
        [ "$COUNT" -gt 0 ] || continue
        NAME=$(basename "$AGENT_DIR")
        AGENT_NAMES="${AGENT_NAMES:+$AGENT_NAMES, }$NAME"
    done
done

if [ -n "$AGENT_NAMES" ]; then
    echo "Agent memory detected for: $AGENT_NAMES"
    echo "Load .claude/skills/subagents/SKILL.md and run the agent memory integration section (§9) before any other work."
fi

exit 0
