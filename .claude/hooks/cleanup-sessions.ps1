#!/usr/bin/env pwsh
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

$RETENTION_DAYS  = 14
$BACKUPS_KEEP    = 3
$TASK_ENTRY_DAYS = 7

$payload          = [Console]::In.ReadToEnd() | ConvertFrom-Json -ErrorAction SilentlyContinue
$currentSessionId = $payload.session_id

$claudeRoot  = Join-Path ($env:USERPROFILE ?? $env:HOME) ".claude"
$projectDir  = $env:CLAUDE_PROJECT_DIR
$cutoff      = (Get-Date).AddDays(-$RETENTION_DAYS)
$uuidPattern = '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'

# ── Project: orphaned and stale session subdirectories ──────────────────────────
if ($projectDir -and (Test-Path $projectDir)) {
    try {
        Get-ChildItem -Path $projectDir -Directory -ErrorAction Stop | Where-Object {
            $_.Name -match $uuidPattern -and $_.Name -ne $currentSessionId
        } | ForEach-Object {
            $dir           = $_
            $matchingJsonl = Join-Path $projectDir "$($dir.Name).jsonl"
            $isOrphaned    = -not (Test-Path $matchingJsonl)
            $isStale       = (Test-Path $matchingJsonl) -and (Get-Item $matchingJsonl).LastWriteTime -lt $cutoff
            if ($isOrphaned -or $isStale) {
                Remove-Item -Path $dir.FullName -Recurse -Force -ErrorAction SilentlyContinue
                Write-Output "cleanup: project session removed $($dir.Name)"
            }
        }
    } catch { }
}

# ── Root: session-env (per-session env state, never reused after session ends) ──
try {
    $envDir = Join-Path $claudeRoot "session-env"
    if (Test-Path $envDir) {
        Get-ChildItem -Path $envDir -Directory -ErrorAction Stop | Where-Object {
            $_.Name -match $uuidPattern -and $_.Name -ne $currentSessionId -and $_.LastWriteTime -lt $cutoff
        } | ForEach-Object {
            Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "cleanup: session-env removed $($_.Name)"
        }
    }
} catch { }

# ── Root: shell-snapshots (orphaned after session end, never reused) ─────────────
try {
    $snapDir = Join-Path $claudeRoot "shell-snapshots"
    if (Test-Path $snapDir) {
        Get-ChildItem -Path $snapDir -File -ErrorAction Stop | Where-Object {
            $_.LastWriteTime -lt $cutoff
        } | ForEach-Object {
            Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
            Write-Output "cleanup: shell-snapshot removed $($_.Name)"
        }
    }
} catch { }

# ── Root: tasks — stale session directories (UUID-keyed, $RETENTION_DAYS) ───────
try {
    $tasksDir = Join-Path $claudeRoot "tasks"
    if (Test-Path $tasksDir) {
        Get-ChildItem -Path $tasksDir -Directory -ErrorAction Stop | Where-Object {
            $_.Name -match $uuidPattern -and $_.Name -ne $currentSessionId -and $_.LastWriteTime -lt $cutoff
        } | ForEach-Object {
            Remove-Item -Path $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
            Write-Output "cleanup: tasks removed $($_.Name)"
        }
    }
} catch { }

# ── Root: tasks — completed/deleted entries (status-based, $TASK_ENTRY_DAYS) ────
try {
    $taskEntryCutoff = (Get-Date).AddDays(-$TASK_ENTRY_DAYS)
    $tasksEntryDir   = Join-Path $claudeRoot "tasks"
    if (Test-Path $tasksEntryDir) {
        Get-ChildItem -Path $tasksEntryDir -Recurse -Filter "*.json" -File -ErrorAction Stop | Where-Object {
            $_.LastWriteTime -lt $taskEntryCutoff
        } | ForEach-Object {
            try {
                $t = Get-Content -Path $_.FullName -Raw -ErrorAction Stop | ConvertFrom-Json -ErrorAction Stop
                if ($t.status -in @("completed", "deleted")) {
                    Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
                    Write-Output "cleanup: task entry removed $($_.Name) [$($t.status)]"
                }
            } catch { }
        }
    }
} catch { }

# ── Root: telemetry ──────────────────────────────────────────────────────────────
try {
    $telDir = Join-Path $claudeRoot "telemetry"
    if (Test-Path $telDir) {
        Get-ChildItem -Path $telDir -File -ErrorAction Stop | Where-Object {
            $_.LastWriteTime -lt $cutoff
        } | ForEach-Object {
            Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
            Write-Output "cleanup: telemetry removed $($_.Name)"
        }
    }
} catch { }

# ── Root: backups — keep only the N newest .backup.* files ──────────────────────
try {
    $backupsDir = Join-Path $claudeRoot "backups"
    if (Test-Path $backupsDir) {
        Get-ChildItem -Path $backupsDir -File -Filter "*.backup.*" -ErrorAction Stop |
            Sort-Object LastWriteTime -Descending |
            Select-Object -Skip $BACKUPS_KEEP |
            ForEach-Object {
                Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
                Write-Output "cleanup: backup removed $($_.Name)"
            }
    }
} catch { }

exit 0
