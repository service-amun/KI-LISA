#!/bin/bash
set -euo pipefail

# Read hook input from stdin — read exactly once
hook_input=$(cat)

# Extract common fields
tool_name=$(echo "$hook_input" | jq -r '.tool_name // empty')
command_str=$(echo "$hook_input" | jq -r '.tool_input.command // empty')
file_path=$(echo "$hook_input" | jq -r '.tool_input.file_path // empty')
cwd=$(echo "$hook_input" | jq -r '.cwd')

# --- PreToolUse: block via exit 2 ---
# stderr is shown as an error message; action stops
if [[ "$command_str" == rm\ -rf* ]]; then
    echo "Destructive rm -rf blocked by hook." >&2
    exit 2
fi

# --- PreToolUse: deny via JSON (exit 0 alternative) ---
# Use when you want a structured reason sent to Claude
# echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Blocked by policy"}}'
# exit 0

# --- PostToolUse: block with structured output ---
# echo '{"decision":"block","reason":"Lint failed — fix before continuing"}'
# exit 0

# --- Stop session entirely (any event) ---
# echo '{"continue":false,"stopReason":"Build failed; session halted"}'
# exit 0

# --- Info message to user (non-blocking) ---
# echo '{"systemMessage":"Warning: editing a generated file"}'
# exit 0

# Success — action continues
exit 0
