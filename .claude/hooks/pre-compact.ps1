#!/usr/bin/env pwsh
# PreCompact hook — block context compaction until PROJECT.md reflects current work.
#
# Status gate: blocks only when PROJECT.md is missing or stale. If PROJECT.md was
# modified within the last $FRESH_MINUTES minutes it is treated as up to date and
# compaction proceeds — this prevents the unconditional re-block loop that would
# otherwise wedge auto-compaction. After Claude updates PROJECT.md on a block, the
# next compaction attempt sees a fresh timestamp and is allowed.
#
# Registration in settings.json under hooks.PreCompact:
#   { "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs pre-compact" }] }
#
# Exit 0: PROJECT.md fresh — allow. Exit 2: missing or stale — block; STDERR is fed back to Claude.

$FRESH_MINUTES = 10

$null = [Console]::In.ReadToEnd()

$projectDir = $env:CLAUDE_PROJECT_DIR
if ($projectDir) {
    $projectMd = Join-Path $projectDir "PROJECT.md"
    if (Test-Path $projectMd) {
        $ageMinutes = ((Get-Date) - (Get-Item $projectMd).LastWriteTime).TotalMinutes
        if ($ageMinutes -le $FRESH_MINUTES) { exit 0 }
    }
}

[Console]::Error.WriteLine(@"
Before compaction: open PROJECT.md and update or create a 'Current work' section with:
  1. Current goal — one sentence.
  2. Last 3-5 completed items — include file paths.
  3. Next immediate action.
Keep the section under 200 words. Once you save PROJECT.md, compaction proceeds automatically.
"@)
exit 2
