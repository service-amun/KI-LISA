#!/usr/bin/env pwsh
# SessionStart hook — detect project memory files and agent memory files; trigger migration.
#
# Registration in settings.json under hooks.SessionStart:
#   { "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs check-memory" }
#
# Exit 0 always. On SessionStart, stdout from exit 0 is added to Claude's context;
# no output means no memory files were found and the session proceeds normally.

$projectDir = $env:CLAUDE_PROJECT_DIR
if (-not $projectDir) { exit 0 }

# ── Project memory ────────────────────────────────────────────────────────────
# Claude Code encodes the project path by replacing every non-alphanumeric
# character with '-' (e.g. 'C:\Dev\my_app' -> 'C--Dev-my-app').
$encoded = $projectDir -replace '[^A-Za-z0-9]', '-'
$memDir  = "$env:USERPROFILE\.claude\projects\$encoded\memory"

if (Test-Path $memDir) {
    $files = Get-ChildItem -Path $memDir -Filter '*.md' -ErrorAction SilentlyContinue
    if ($files.Count -gt 0) {
        Write-Output "$($files.Count) project memory file(s) detected in: $memDir"
        Write-Output "Load .claude/skills/file-claude/SKILL.md and run the memory integration section (§5) before any other work."
    }
}

# ── Agent memory ──────────────────────────────────────────────────────────────
# Check all three scopes: user-level, project-level, project-local (git-ignored).
$agentMemDirs = @(
    "$env:USERPROFILE\.claude\agent-memory",
    (Join-Path $projectDir ".claude\agent-memory"),
    (Join-Path $projectDir ".claude\agent-memory-local")
) | Where-Object { $_ -and (Test-Path $_) }

$agentNames = @()
foreach ($dir in $agentMemDirs) {
    Get-ChildItem -Path $dir -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $hasFiles = (Get-ChildItem -Path $_.FullName -Filter '*.md' -ErrorAction SilentlyContinue).Count -gt 0
        if ($hasFiles) { $agentNames += $_.Name }
    }
}

if ($agentNames.Count -gt 0) {
    $unique = ($agentNames | Sort-Object -Unique) -join ', '
    Write-Output "Agent memory detected for: $unique"
    Write-Output "Load .claude/skills/subagents/SKILL.md and run the agent memory integration section (§9) before any other work."
}

exit 0
