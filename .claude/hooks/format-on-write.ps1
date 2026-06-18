#!/usr/bin/env pwsh
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
# Silently skips if no formatter is installed for the file type.
# Never fails — PostToolUse exit 0 always continues the session.
#
# Registration in settings.json under hooks.PostToolUse (single group):
#   { "matcher": "Write|Edit|MultiEdit", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs format-on-write" }] }

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json -ErrorAction Stop
} catch { exit 0 }

$filePath = switch ($payload.tool_name) {
    "Write"     { $payload.tool_input.file_path }
    "Edit"      { $payload.tool_input.file_path }
    "MultiEdit" { $payload.tool_input.file_path }
    default     { exit 0 }
}

if (-not $filePath) { exit 0 }
if (-not (Test-Path $filePath -PathType Leaf)) { exit 0 }

$ext = [System.IO.Path]::GetExtension($filePath).TrimStart('.').ToLower()

try {
    switch ($ext) {
        { $_ -in @('md','markdown') } {
            if (Get-Command markdownlint -ErrorAction SilentlyContinue) {
                & markdownlint --fix $filePath 2>$null
            }
        }
        { $_ -in @('js','jsx','ts','tsx','css','scss','html','json','jsonc','yaml','yml') } {
            if (Get-Command biome -ErrorAction SilentlyContinue) {
                & biome format --write $filePath 2>$null
            } elseif (Get-Command prettier -ErrorAction SilentlyContinue) {
                & prettier --write $filePath 2>$null
            }
        }
        'py' {
            if (Get-Command ruff -ErrorAction SilentlyContinue) {
                & ruff format $filePath 2>$null
            } elseif (Get-Command black -ErrorAction SilentlyContinue) {
                & black --quiet $filePath 2>$null
            }
        }
        'go' {
            if (Get-Command goimports -ErrorAction SilentlyContinue) {
                & goimports -w $filePath 2>$null
            } elseif (Get-Command gofmt -ErrorAction SilentlyContinue) {
                & gofmt -w $filePath 2>$null
            }
        }
        'rs' {
            if (Get-Command rustfmt -ErrorAction SilentlyContinue) {
                & rustfmt $filePath 2>$null
            }
        }
        'rb' {
            if (Get-Command rubocop -ErrorAction SilentlyContinue) {
                & rubocop -a -q $filePath 2>$null
            }
        }
        'java' {
            if (Get-Command google-java-format -ErrorAction SilentlyContinue) {
                & google-java-format -i $filePath 2>$null
            }
        }
        'php' {
            if (Get-Command php-cs-fixer -ErrorAction SilentlyContinue) {
                & php-cs-fixer fix $filePath 2>$null
            }
        }
        'dart' {
            if (Get-Command dart -ErrorAction SilentlyContinue) {
                & dart format $filePath 2>$null
            }
        }
        'zig' {
            if (Get-Command zig -ErrorAction SilentlyContinue) {
                & zig fmt $filePath 2>$null
            }
        }
    }
} catch { }

exit 0
