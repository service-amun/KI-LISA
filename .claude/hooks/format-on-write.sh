#!/usr/bin/env bash
# PostToolUse (Write | Edit | MultiEdit) hook — auto-formats the written file with the installed formatter.
#
# Formatter selection by extension (primary → fallback):
#   .md .markdown                                              → markdownlint --fix
#   .js .jsx .ts .tsx .css .scss .html .json .jsonc .yaml .yml → biome (primary) or prettier
#   .py                                                         → ruff format (primary) or black
#   .go                                                         → goimports (primary) or gofmt
#   .rs                                                         → rustfmt
#   .rb                                                         → rubocop -a (safe autocorrect)
#   .java                                                       → google-java-format -i
#   .php                                                        → php-cs-fixer fix
#   .dart                                                       → dart format
#   .zig                                                        → zig fmt
#
# Silently skips if no formatter is installed for the file type. Requires jq.
# Never fails — PostToolUse hook always exits 0.
#
# Registration in settings.json under hooks.PostToolUse (single group):
#   { "matcher": "Write|Edit|MultiEdit", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs format-on-write" }] }

command -v jq &>/dev/null || exit 0

PAYLOAD=$(cat /dev/stdin 2>/dev/null || true)
[ -z "$PAYLOAD" ] && exit 0

TOOL_NAME=$(printf '%s' "$PAYLOAD" | jq -r '.tool_name // ""' 2>/dev/null)
case "$TOOL_NAME" in
    Write|Edit|MultiEdit)
        FILE_PATH=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // ""' 2>/dev/null)
        ;;
    *) exit 0 ;;
esac

[ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ] && exit 0

EXT="${FILE_PATH##*.}"
EXT="${EXT,,}"

case "$EXT" in
    md|markdown)
        command -v markdownlint &>/dev/null && markdownlint --fix "$FILE_PATH" 2>/dev/null || true
        ;;
    js|jsx|ts|tsx|css|scss|html|json|jsonc|yaml|yml)
        if command -v biome &>/dev/null; then
            biome format --write "$FILE_PATH" 2>/dev/null || true
        elif command -v prettier &>/dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    py)
        if command -v ruff &>/dev/null; then
            ruff format "$FILE_PATH" 2>/dev/null || true
        elif command -v black &>/dev/null; then
            black --quiet "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    go)
        if command -v goimports &>/dev/null; then
            goimports -w "$FILE_PATH" 2>/dev/null || true
        elif command -v gofmt &>/dev/null; then
            gofmt -w "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    rs)
        command -v rustfmt &>/dev/null && rustfmt "$FILE_PATH" 2>/dev/null || true
        ;;
    rb)
        command -v rubocop &>/dev/null && rubocop -a -q "$FILE_PATH" 2>/dev/null || true
        ;;
    java)
        command -v google-java-format &>/dev/null && google-java-format -i "$FILE_PATH" 2>/dev/null || true
        ;;
    php)
        command -v php-cs-fixer &>/dev/null && php-cs-fixer fix "$FILE_PATH" 2>/dev/null || true
        ;;
    dart)
        command -v dart &>/dev/null && dart format "$FILE_PATH" 2>/dev/null || true
        ;;
    zig)
        command -v zig &>/dev/null && zig fmt "$FILE_PATH" 2>/dev/null || true
        ;;
esac

exit 0
