#!/usr/bin/env bash
# SessionStart (clear) hook — removes stale session artifacts from the current
# project directory and the global ~/.claude root.
#
# Project cleanup: orphaned or stale session subdirectories under CLAUDE_PROJECT_DIR.
# Root cleanup:    session-env, shell-snapshots, tasks (stale sessions + completed entries), telemetry, backups.
#
# Registration in settings.json under hooks.SessionStart, matcher "clear":
#   { "matcher": "clear", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs cleanup-sessions" }] }
#
# Exit 0: always — cleanup errors must not block session start.
# No `set -euo pipefail` by design: every failure path is tolerated inline
# (|| true, 2>/dev/null); strict mode could abort cleanup mid-run and is
# intentionally omitted for this never-blocking hook.

RETENTION_DAYS=14
BACKUPS_KEEP=3
TASK_ENTRY_DAYS=7

PAYLOAD=$(cat /dev/stdin 2>/dev/null || true)
CURRENT_SESSION=""
if command -v jq &>/dev/null; then
    CURRENT_SESSION=$(printf '%s' "$PAYLOAD" | jq -r '.session_id // ""' 2>/dev/null || true)
fi

CLAUDE_ROOT="${HOME}/.claude"
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-}"
UUID_PATTERN='^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# ── Project: orphaned and stale session subdirectories ──────────────────────────
if [ -n "$PROJECT_DIR" ] && [ -d "$PROJECT_DIR" ]; then
    for dir in "$PROJECT_DIR"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        printf '%s\n' "$name" | grep -qE "$UUID_PATTERN" || continue
        [ "$name" = "$CURRENT_SESSION" ] && continue
        matching_jsonl="$PROJECT_DIR/$name.jsonl"
        is_orphaned=false
        is_stale=false
        [ ! -f "$matching_jsonl" ] && is_orphaned=true
        if [ -f "$matching_jsonl" ]; then
            find "$matching_jsonl" -mtime "+$RETENTION_DAYS" 2>/dev/null | grep -q . && is_stale=true
        fi
        if [ "$is_orphaned" = true ] || [ "$is_stale" = true ]; then
            rm -rf "$dir" 2>/dev/null || true
            echo "cleanup: project session removed $name"
        fi
    done
fi

# ── Root: session-env (per-session env state, never reused after session ends) ──
env_dir="$CLAUDE_ROOT/session-env"
if [ -d "$env_dir" ]; then
    for dir in "$env_dir"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        printf '%s\n' "$name" | grep -qE "$UUID_PATTERN" || continue
        [ "$name" = "$CURRENT_SESSION" ] && continue
        find "$dir" -maxdepth 0 -mtime "+$RETENTION_DAYS" 2>/dev/null | grep -q . || continue
        rm -rf "$dir" 2>/dev/null || true
        echo "cleanup: session-env removed $name"
    done
fi

# ── Root: shell-snapshots (orphaned after session end, never reused) ─────────────
snap_dir="$CLAUDE_ROOT/shell-snapshots"
if [ -d "$snap_dir" ]; then
    find "$snap_dir" -maxdepth 1 -type f -mtime "+$RETENTION_DAYS" 2>/dev/null | while read -r f; do
        rm -f "$f" 2>/dev/null || true
        echo "cleanup: shell-snapshot removed $(basename "$f")"
    done
fi

# ── Root: tasks — stale session directories (UUID-keyed, RETENTION_DAYS) ────────
tasks_dir="$CLAUDE_ROOT/tasks"
if [ -d "$tasks_dir" ]; then
    for dir in "$tasks_dir"/*/; do
        [ -d "$dir" ] || continue
        name=$(basename "$dir")
        printf '%s\n' "$name" | grep -qE "$UUID_PATTERN" || continue
        [ "$name" = "$CURRENT_SESSION" ] && continue
        find "$dir" -maxdepth 0 -mtime "+$RETENTION_DAYS" 2>/dev/null | grep -q . || continue
        rm -rf "$dir" 2>/dev/null || true
        echo "cleanup: tasks removed $name"
    done
fi

# ── Root: tasks — completed/deleted entries (status-based, TASK_ENTRY_DAYS) ─────
if [ -d "$tasks_dir" ] && command -v jq &>/dev/null; then
    find "$tasks_dir" -maxdepth 2 -name "*.json" -mtime "+$TASK_ENTRY_DAYS" 2>/dev/null | while read -r f; do
        status=$(jq -r '.status // ""' "$f" 2>/dev/null || true)
        case "$status" in
            completed|deleted)
                rm -f "$f" 2>/dev/null || true
                echo "cleanup: task entry removed $(basename "$f") [$status]"
                ;;
        esac
    done
fi

# ── Root: telemetry ─────────────────────────────────────────────────────────────
tel_dir="$CLAUDE_ROOT/telemetry"
if [ -d "$tel_dir" ]; then
    find "$tel_dir" -maxdepth 1 -type f -mtime "+$RETENTION_DAYS" 2>/dev/null | while read -r f; do
        rm -f "$f" 2>/dev/null || true
        echo "cleanup: telemetry removed $(basename "$f")"
    done
fi

# ── Root: backups — keep only the N newest .backup.* files ──────────────────────
backups_dir="$CLAUDE_ROOT/backups"
if [ -d "$backups_dir" ]; then
    ls -1t "$backups_dir"/*.backup.* 2>/dev/null | tail -n "+$((BACKUPS_KEEP + 1))" | while read -r f; do
        rm -f "$f" 2>/dev/null || true
        echo "cleanup: backup removed $(basename "$f")"
    done
fi

exit 0
