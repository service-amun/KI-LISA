#!/usr/bin/env bash
# PreToolUse (Write | Edit | MultiEdit) hook — blocks file writes that contain known credential patterns.
#
# Patterns covered: Anthropic, OpenAI, GitHub, AWS, Google, Stripe keys;
# PEM private keys; JWT tokens.
# Skips: test/fixture/example file paths; obvious placeholder content.
# Requires jq. Exits 0 (never blocks) when jq is unavailable.
#
# Registration in settings.json under hooks.PreToolUse:
#   { "matcher": "Write|Edit|MultiEdit", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs check-credentials" }] }
#
# Exit 0: clean or unrecognised tool — allow the write.
# Exit 2: credential detected — block and send findings to Claude as inline feedback.
# All errors exit 0: hook failure must never block a legitimate write.

command -v jq &>/dev/null || exit 0

PAYLOAD=$(cat /dev/stdin 2>/dev/null || true)
[ -z "$PAYLOAD" ] && exit 0

TOOL_NAME=$(printf '%s' "$PAYLOAD" | jq -r '.tool_name // ""' 2>/dev/null || true)

case "$TOOL_NAME" in
    Write)
        FILE_PATH=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // ""' 2>/dev/null || true)
        CONTENT=$(printf '%s'  "$PAYLOAD" | jq -r '.tool_input.content // ""' 2>/dev/null || true)
        ;;
    Edit)
        FILE_PATH=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // ""' 2>/dev/null || true)
        CONTENT=$(printf '%s'  "$PAYLOAD" | jq -r '.tool_input.new_string // ""' 2>/dev/null || true)
        ;;
    MultiEdit)
        FILE_PATH=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // ""' 2>/dev/null || true)
        CONTENT=$(printf '%s'  "$PAYLOAD" | jq -r '[.tool_input.edits[]?.new_string] | join("\n")' 2>/dev/null || true)
        ;;
    *) exit 0 ;;
esac

[ -z "$CONTENT" ] && exit 0

# Skip test, fixture, example, and template file paths
printf '%s\n' "$FILE_PATH" | grep -qiE '(/tests?/|/fixtures?/|/__mock|\.example$|\.template$|\.sample$)' && exit 0

# Skip obvious placeholder / example content
printf '%s\n' "$CONTENT" | grep -qiE '(YOUR_KEY|YOUR_SECRET|YOUR_TOKEN|<API_KEY|<SECRET|EXAMPLE_KEY|PLACEHOLDER|changeme|replace\.me|redacted)' && exit 0

FINDINGS=""
check_pattern() {
    local name="$1" pattern="$2"
    printf '%s\n' "$CONTENT" | grep -qE "$pattern" 2>/dev/null && FINDINGS="${FINDINGS}${name}, "
}

check_pattern "Anthropic API key"  'sk-ant-[A-Za-z0-9_-]{20,}'
check_pattern "OpenAI API key"     'sk-[A-Za-z0-9]{32,}'
check_pattern "GitHub PAT"         'gh[ps]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}'
check_pattern "AWS access key"     'AKIA[A-Z0-9]{16}'
check_pattern "Google API key"     'AIza[A-Za-z0-9_-]{35}'
check_pattern "Stripe live key"    'sk_live_[A-Za-z0-9]{24}'
check_pattern "PEM private key"    '-----BEGIN .{0,20}PRIVATE KEY-----'
check_pattern "JWT token"          'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}'

[ -z "$FINDINGS" ] && exit 0
FINDINGS="${FINDINGS%, }"

echo "CREDENTIAL GUARD: Possible secret(s) detected in content to be written: ${FINDINGS}."
echo "Do not write this content. Inform the user what was found and ask how to proceed."
echo "If this is intentional test data or a documentation example, the user must confirm before proceeding."
exit 2
