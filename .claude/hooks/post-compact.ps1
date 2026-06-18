#!/usr/bin/env pwsh
# SessionStart (compact) hook — re-inject PROJECT.md into Claude's context after compaction.
#
# Registration in settings.json under hooks.SessionStart, matcher "compact":
#   { "matcher": "compact", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs post-compact" }] }
#
# Exit 0 always. On SessionStart, stdout from exit 0 is added to Claude's context;
# no output (PROJECT.md absent or empty) means the session continues normally.

$null = [Console]::In.ReadToEnd()

$projectDir = $env:CLAUDE_PROJECT_DIR
if (-not $projectDir) { exit 0 }

$projectMd = Join-Path $projectDir "PROJECT.md"
if (-not (Test-Path $projectMd)) { exit 0 }

$content = Get-Content $projectMd -Raw -ErrorAction SilentlyContinue
if (-not $content -or $content.Trim() -eq '') { exit 0 }

Write-Output "=== PROJECT.md reloaded after context compaction ==="
Write-Output $content
exit 0
