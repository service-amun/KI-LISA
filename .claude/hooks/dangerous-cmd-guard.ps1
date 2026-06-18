#!/usr/bin/env pwsh
# PreToolUse (Bash | PowerShell) hook — blocks clearly destructive or irreversible shell commands.
#
# Blocked categories: filesystem destruction (rm/wipefs/truncate), disk formatting
# (dd/mkfs), firewall flush (iptables -F), process kill-all, git force-push to
# protected branches, fork bombs, world-writable root, force reboot, sysrq trigger,
# crontab removal. Windows/PowerShell: Remove-Item -Recurse -Force of a drive root or
# system dir, Format-Volume, Clear-Disk, rd /s of a drive root, Restart/Stop-Computer -Force.
# Does NOT block rm on project paths, git force-push to feature branches, or DROP TABLE
# in migration scripts — only the narrowest unambiguous catastrophes.
#
# Registration in settings.json under hooks.PreToolUse:
#   { "matcher": "Bash|PowerShell", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs dangerous-cmd-guard" }] }
#
# Exit 0: allow. Exit 2: block — stdout sent to Claude as feedback.
# Exit 0 on any parse error: hook failure must never block legitimate work.

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json -ErrorAction Stop
} catch {
    exit 0
}

$command = $payload.tool_input.command
if (-not $command) { exit 0 }

$patterns = @(
    [pscustomobject]@{
        Pattern = 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(/{1,2}\s|~/|/\*)'
        Reason  = "Recursive forced deletion of root filesystem, home directory, or root wildcard"
    }
    [pscustomobject]@{
        Pattern = 'git\s+push\s+.*(--(force|force-with-lease)|-f)\b.*\b(main|master|prod(uction)?|release|staging)\b'
        Reason  = "Force-push to protected branch (main, master, prod, production, release, staging)"
    }
    [pscustomobject]@{
        Pattern = 'git\s+push\s+.*\b(main|master|prod(uction)?|release|staging)\b.*(--(force|force-with-lease)|-f)\b'
        Reason  = "Force-push to protected branch (branch name appears before flag)"
    }
    [pscustomobject]@{
        Pattern = ':\(\)\s*\{\s*:\s*\|\s*:.*&'
        Reason  = "Fork bomb pattern"
    }
    [pscustomobject]@{
        Pattern = '\bdd\b.*\bof=/dev/(sd[a-z]|hd[a-z]|nvme\d|vd[a-z])\b'
        Reason  = "Direct write to raw block device (dd)"
    }
    [pscustomobject]@{
        Pattern = '\bmkfs\b'
        Reason  = "Disk formatting command (mkfs)"
    }
    [pscustomobject]@{
        Pattern = '\bformat\s+[A-Z]:\b'
        Reason  = "Windows disk format"
    }
    [pscustomobject]@{
        Pattern = 'chmod\s+(-R\s+)?777\s+/'
        Reason  = "World-writable permissions on root or system path"
    }
    [pscustomobject]@{
        Pattern = '\bwipefs\b.*\s+/dev/[a-z]'
        Reason  = "Wipe filesystem signatures on block device (wipefs)"
    }
    [pscustomobject]@{
        Pattern = '\biptables\s+((-[A-Za-z]+\s+)*)?(-F|--flush)\b'
        Reason  = "Flush all iptables firewall rules (iptables -F / --flush)"
    }
    [pscustomobject]@{
        Pattern = '\btruncate\b.*-s\s+0\s+/(etc|usr|boot|var/log|var/run|lib|sbin)/'
        Reason  = "Truncate system file to zero bytes"
    }
    [pscustomobject]@{
        Pattern = '\bkill\s+((-[0-9]+|-[A-Z]+|-SIGKILL|-KILL)\s+)+(-1|0)\b'
        Reason  = "Kill all running processes (kill -9 -1)"
    }
    [pscustomobject]@{
        Pattern = '\b(reboot|poweroff|shutdown|halt)\b.*\s(-f|--force)\b'
        Reason  = "Force system shutdown or reboot without graceful unmount"
    }
    [pscustomobject]@{
        Pattern = 'echo\s+[bh]\s*>\s*/proc/sysrq-trigger'
        Reason  = "Kernel sysrq trigger: immediate reboot or emergency remount"
    }
    [pscustomobject]@{
        Pattern = '\bcrontab\s+-r\b'
        Reason  = "Remove all cron jobs (crontab -r; commonly confused with -e)"
    }
    # ── Windows / PowerShell ─────────────────────────────────────────────────
    [pscustomobject]@{
        Pattern = '(remove-item|\bri\b)(?=.*-(recurse|r)\b)(?=.*-(force|f)\b)(?=.*([a-z]:\\(\*|\s|$)|[a-z]:\\windows\b|\$env:(systemroot|windir|systemdrive)))'
        Reason  = "Recursive forced deletion of a Windows drive root or system directory (Remove-Item -Recurse -Force)"
    }
    [pscustomobject]@{
        Pattern = '\bformat-volume\b'
        Reason  = "Windows Format-Volume (formats a volume)"
    }
    [pscustomobject]@{
        Pattern = '\bclear-disk\b'
        Reason  = "Windows Clear-Disk (wipes a disk)"
    }
    [pscustomobject]@{
        Pattern = '\b(rd|rmdir)\b.*\s/s\b.*[a-z]:\\(\*|\s|$)'
        Reason  = "Recursive removal of a Windows drive root (rd /s)"
    }
    [pscustomobject]@{
        Pattern = '\b(restart-computer|stop-computer)\b.*-force\b'
        Reason  = "Force shutdown or restart of the computer"
    }
)

$blocked = @()
foreach ($p in $patterns) {
    try {
        if ($command -imatch $p.Pattern) { $blocked += $p.Reason }
    } catch { }
}

if ($blocked.Count -eq 0) { exit 0 }

$reasons = $blocked -join "; "
Write-Output "COMMAND GUARD: Blocked — $reasons."
Write-Output "This command is destructive or irreversible. Do not run it without explicit user confirmation."
Write-Output "Explain what you were trying to accomplish and ask the user whether to proceed."
exit 2
