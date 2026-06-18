#!/usr/bin/env bash
# Stop hook — logs token usage after every assistant response turn.
#
# Appends one JSONL line to ~/.claude/session-costs.log:
#   {"ts":"...","session":"...","model":"...","in":N,"out":N,"cache_read":N,"cache_write":N,"transcript":"..."}
#
# Token extraction: reads all assistant entries from the session transcript JSONL,
# deduplicates by message ID (parallel tool calls share one ID), sums across unique
# messages. Parses both the current Claude Code format (.type=="assistant", .message.usage)
# and the legacy flat format (.role=="assistant", .usage) for backwards compatibility.
# Cache fields: cache_read_input_tokens (billed at 10% of input rate) and
# cache_creation_input_tokens (written to cache this turn). Requires jq.
# Falls back to null for any field the transcript does not contain.
#
# Why Stop: Claude Code exposes no dedicated session-end hook; Stop fires at the end
# of each assistant turn when the transcript is up to date. Per-turn logging provides
# granular cost data and a running session total.
#
# Registration: hooks.Stop (per-turn), plus hooks.PreCompact and hooks.SessionEnd (matcher
# "clear") so a cumulative cost snapshot is also logged at compaction and at /clear boundaries:
#   { "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs session-cost-logger" }] }
#
# Exit 0 always — logging must never block the session.
# No set -euo pipefail by design: every failure is tolerated inline.

PAYLOAD=$(cat /dev/stdin 2>/dev/null || true)

if command -v jq &>/dev/null && [ -n "$PAYLOAD" ]; then
    SESSION_ID=$(printf '%s' "$PAYLOAD" | jq -r '.session_id // "unknown"' 2>/dev/null || echo "unknown")
    TRANSCRIPT=$(printf '%s' "$PAYLOAD" | jq -r '.transcript_path // ""'   2>/dev/null || true)
else
    SESSION_ID="unknown"
    TRANSCRIPT=""
fi

TIMESTAMP=$(date -u "+%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S")
MODEL="unknown"
INPUT_TOKENS="null"
OUTPUT_TOKENS="null"
CACHE_READ="null"
CACHE_WRITE="null"

if [ -n "$TRANSCRIPT" ] && [ -f "$TRANSCRIPT" ] && command -v jq &>/dev/null; then
    AGGREGATED=$(jq -rs '
        [.[] | select(
            (.type == "assistant" and .message.usage != null) or
            (.role == "assistant" and .usage != null)
        )] |
        reduce .[] as $e (
            {"seen": [], "in": null, "out": null, "cr": null, "cw": null, "model": "unknown"};
            ($e.message.id // ($e.id // "")) as $mid |
            if ($mid != "" and (.seen | index($mid) != null)) then .
            else
                (.seen + [$mid]) as $seen2 |
                ($e.message.usage // $e.usage) as $u |
                ($e.message.model // $e.model // .model) as $m |
                {
                    "seen": $seen2,
                    "in":    (if $u.input_tokens                  != null then ((.in  // 0) + $u.input_tokens)                  else .in    end),
                    "out":   (if $u.output_tokens                 != null then ((.out // 0) + $u.output_tokens)                 else .out   end),
                    "cr":    (if $u.cache_read_input_tokens        != null then ((.cr  // 0) + $u.cache_read_input_tokens)        else .cr    end),
                    "cw":    (if $u.cache_creation_input_tokens    != null then ((.cw  // 0) + $u.cache_creation_input_tokens)    else .cw    end),
                    "model": (if $m != null and $m != "" then $m else .model end)
                }
            end
        ) |
        [(.in // "null"|tostring), (.out // "null"|tostring), (.cr // "null"|tostring), (.cw // "null"|tostring), .model] |
        join("|")
    ' "$TRANSCRIPT" 2>/dev/null || true)

    if [ -n "$AGGREGATED" ]; then
        INPUT_TOKENS=$(printf '%s' "$AGGREGATED" | cut -d'|' -f1)
        OUTPUT_TOKENS=$(printf '%s' "$AGGREGATED" | cut -d'|' -f2)
        CACHE_READ=$(printf '%s' "$AGGREGATED" | cut -d'|' -f3)
        CACHE_WRITE=$(printf '%s' "$AGGREGATED" | cut -d'|' -f4)
        MODEL=$(printf '%s' "$AGGREGATED" | cut -d'|' -f5)
    fi
fi

LOG_FILE="${HOME}/.claude/session-costs.log"
mkdir -p "${HOME}/.claude" 2>/dev/null || true

ESCAPED_SESSION=$(printf '%s' "$SESSION_ID"  | sed 's/"/\\"/g')
ESCAPED_MODEL=$(printf '%s'   "$MODEL"        | sed 's/"/\\"/g')
ESCAPED_TRANSCRIPT=$(printf '%s' "$TRANSCRIPT" | sed 's/\\/\\\\/g; s/"/\\"/g')

printf '{"ts":"%s","session":"%s","model":"%s","in":%s,"out":%s,"cache_read":%s,"cache_write":%s,"transcript":"%s"}\n' \
    "$TIMESTAMP" "$ESCAPED_SESSION" "$ESCAPED_MODEL" \
    "$INPUT_TOKENS" "$OUTPUT_TOKENS" "$CACHE_READ" "$CACHE_WRITE" \
    "$ESCAPED_TRANSCRIPT" \
    >> "$LOG_FILE" 2>/dev/null || true

exit 0
