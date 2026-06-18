#!/usr/bin/env pwsh
# PreToolUse (Write | Edit | MultiEdit) hook — blocks file writes that contain known credential patterns.
#
# Patterns covered: Anthropic, OpenAI, GitHub, AWS, Google, Stripe keys;
# PEM private keys; JWT tokens.
# Skips: test/fixture/example file paths; obvious placeholder content.
#
# Registration in settings.json under hooks.PreToolUse:
#   { "matcher": "Write|Edit|MultiEdit", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs check-credentials" }] }
#
# Exit 0: clean or unrecognised tool — allow the write.
# Exit 2: credential detected — block and send findings to Claude as inline feedback.
# All errors exit 0: hook failure must never block a legitimate write.

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json -ErrorAction Stop
} catch {
    exit 0
}

$filePath = $null
$content  = $null

switch ($payload.tool_name) {
    "Write" {
        $filePath = $payload.tool_input.file_path
        $content  = $payload.tool_input.content
    }
    "Edit" {
        $filePath = $payload.tool_input.file_path
        $content  = $payload.tool_input.new_string
    }
    "MultiEdit" {
        $filePath = $payload.tool_input.file_path
        $content  = ($payload.tool_input.edits | ForEach-Object { $_.new_string }) -join "`n"
    }
    default { exit 0 }
}

if (-not $content) { exit 0 }

# Skip test, fixture, example, and template paths
if ($filePath -and $filePath -match '(?i)([\\/]tests?[\\/]|[\\/]fixtures?[\\/]|[\\/]__mock|\.example$|\.template$|\.sample$)') {
    exit 0
}

# Skip obvious placeholder / example content (whole-file check)
if ($content -match '(?i)(YOUR_KEY|YOUR_SECRET|YOUR_TOKEN|<API_KEY|<SECRET|EXAMPLE_KEY|PLACEHOLDER|changeme|replace\.me|redacted|x{8,}|0{8,})') {
    exit 0
}

$patterns = @(
    [pscustomobject]@{ Name = "Anthropic API key"; Pattern = 'sk-ant-[A-Za-z0-9_-]{20,}' }
    [pscustomobject]@{ Name = "OpenAI API key";    Pattern = 'sk-[A-Za-z0-9]{32,}' }
    [pscustomobject]@{ Name = "GitHub PAT";        Pattern = 'gh[ps]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82}' }
    [pscustomobject]@{ Name = "AWS access key";    Pattern = 'AKIA[A-Z0-9]{16}' }
    [pscustomobject]@{ Name = "Google API key";    Pattern = 'AIza[A-Za-z0-9_-]{35}' }
    [pscustomobject]@{ Name = "Stripe live key";   Pattern = 'sk_live_[A-Za-z0-9]{24}' }
    [pscustomobject]@{ Name = "PEM private key";   Pattern = '-----BEGIN .{0,20}PRIVATE KEY-----' }
    [pscustomobject]@{ Name = "JWT token";         Pattern = 'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}' }
)

$found = @()
foreach ($p in $patterns) {
    try {
        if ($content -match $p.Pattern) { $found += $p.Name }
    } catch { }
}

if ($found.Count -eq 0) { exit 0 }

$list = $found -join ", "
Write-Output "CREDENTIAL GUARD: Possible secret(s) detected in content to be written: $list."
Write-Output "Do not write this content. Inform the user what was found and ask how to proceed."
Write-Output "If this is intentional test data or a documentation example, the user must confirm before proceeding."
exit 2
