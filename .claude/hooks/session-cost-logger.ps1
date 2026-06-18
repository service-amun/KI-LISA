#!/usr/bin/env pwsh
# Stop hook — logs token usage after every assistant response turn.
#
# Appends one JSONL line to $HOME/.claude/session-costs.log:
#   {"ts":"...","session":"...","model":"...","in":N,"out":N,"cache_read":N,"cache_write":N,"transcript":"..."}
#
# Token extraction: reads all assistant entries from the session transcript JSONL,
# deduplicates by message ID (parallel tool calls share one ID), sums across unique
# messages. Parses both the current Claude Code format (.type=="assistant", .message.usage)
# and the legacy flat format (.role=="assistant", .usage) for backwards compatibility.
# Cache fields: cache_read_input_tokens (billed at 10% of input rate) and
# cache_creation_input_tokens (written to cache this turn).
# Falls back to null for any field the transcript does not contain.
#
# Why Stop (not a dedicated SessionEnd event): Stop fires at the end of each
# assistant response turn, at which point the transcript JSONL is up to date.
# Claude Code exposes no distinct session-end hook; Stop is the closest equivalent.
# One log line per turn gives per-turn granularity and a running session total.
#
# Registration: hooks.Stop (per-turn), plus hooks.PreCompact and hooks.SessionEnd (matcher
# "clear") so a cumulative cost snapshot is also logged at compaction and at /clear boundaries:
#   { "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs session-cost-logger" }] }
#
# Exit 0 always — logging must never block the session.

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json -ErrorAction Stop
} catch { exit 0 }

$sessionId      = if ($payload.session_id)      { $payload.session_id }      else { "unknown" }
$transcriptPath = if ($payload.transcript_path) { $payload.transcript_path } else { "" }
$timestamp      = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")

$inputTokens  = $null
$outputTokens = $null
$cacheRead    = $null
$cacheWrite   = $null
$model        = "unknown"

if ($transcriptPath -and (Test-Path $transcriptPath)) {
    try {
        $seenIds = [System.Collections.Generic.HashSet[string]]::new()

        Get-Content -Path $transcriptPath -Encoding UTF8 -ErrorAction Stop |
            ForEach-Object {
                try { $_ | ConvertFrom-Json -ErrorAction SilentlyContinue } catch { $null }
            } |
            Where-Object {
                $_ -and (
                    ($_.type -eq "assistant" -and $_.message -and $_.message.usage) -or
                    ($_.role -eq "assistant" -and $_.usage)
                )
            } |
            ForEach-Object {
                $entry   = $_
                $msgId   = if ($entry.message -and $entry.message.id) { $entry.message.id } else { [System.Guid]::NewGuid().ToString() }
                if (-not $seenIds.Add($msgId)) { return }

                $usage = if ($entry.message -and $entry.message.usage) { $entry.message.usage } else { $entry.usage }
                if ($entry.message -and $entry.message.model) { $model = $entry.message.model }

                if ($null -ne $usage.input_tokens)  {
                    $inputTokens  = if ($null -eq $inputTokens) { $usage.input_tokens }  else { $inputTokens  + $usage.input_tokens }
                }
                if ($null -ne $usage.output_tokens) {
                    $outputTokens = if ($null -eq $outputTokens) { $usage.output_tokens } else { $outputTokens + $usage.output_tokens }
                }
                if ($null -ne $usage.cache_read_input_tokens) {
                    $cacheRead = if ($null -eq $cacheRead) { $usage.cache_read_input_tokens } else { $cacheRead + $usage.cache_read_input_tokens }
                }
                if ($null -ne $usage.cache_creation_input_tokens) {
                    $cacheWrite = if ($null -eq $cacheWrite) { $usage.cache_creation_input_tokens } else { $cacheWrite + $usage.cache_creation_input_tokens }
                }
            }
    } catch { }
}

$logDir  = Join-Path ($env:USERPROFILE ?? $env:HOME) ".claude"
$logFile = Join-Path $logDir "session-costs.log"

try {
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $logEntry = [ordered]@{
        ts          = $timestamp
        session     = $sessionId
        model       = $model
        in          = $inputTokens
        out         = $outputTokens
        cache_read  = $cacheRead
        cache_write = $cacheWrite
        transcript  = $transcriptPath
    }
    ($logEntry | ConvertTo-Json -Compress) | Add-Content -Path $logFile -Encoding UTF8 -ErrorAction Stop
} catch { }

exit 0
