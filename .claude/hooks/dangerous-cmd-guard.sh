#!/usr/bin/env bash
# PreToolUse (Bash | PowerShell) hook — blocks clearly destructive or irreversible shell commands.
#
# Blocked categories: filesystem destruction (rm/wipefs/truncate), disk formatting
# (dd/mkfs), firewall flush (iptables -F), process kill-all, git force-push to
# protected branches, fork bombs, world-writable root, force reboot, sysrq trigger,
# crontab removal. Windows/PowerShell: Remove-Item -Recurse -Force of a drive root or
# system dir, format X:, Format-Volume, Clear-Disk, rd /s of a drive root, Restart/Stop-Computer -Force.
# Requires jq; exits 0 (allow) when jq is unavailable.
#
# Registration in settings.json under hooks.PreToolUse:
#   { "matcher": "Bash|PowerShell", "hooks": [{ "type": "command", "command": "node ${CLAUDE_PROJECT_DIR}/.claude/hooks/dispatch.mjs dangerous-cmd-guard" }] }
#
# Exit 0: allow. Exit 2: block — stdout sent to Claude as feedback.
# Exit 0 on any parse error: hook failure must never block legitimate work.

command -v jq &>/dev/null || exit 0

PAYLOAD=$(cat /dev/stdin 2>/dev/null || true)
[ -z "$PAYLOAD" ] && exit 0

CMD=$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.command // ""' 2>/dev/null || true)
[ -z "$CMD" ] && exit 0

BLOCKED=""
check() {
    local reason="$1" pattern="$2"
    printf '%s\n' "$CMD" | grep -qsiE "$pattern" 2>/dev/null && BLOCKED="${BLOCKED}${reason}; "
}

check "Recursive forced deletion of root/home/wildcard" \
    'rm\s+-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*\s+(/{1,2}\s|~/|/\*)'

check "Force-push to protected branch" \
    'git\s+push\s+.*(--force|--force-with-lease|-f)\b.*(main|master|prod(uction)?|release|staging)'

check "Force-push to protected branch (reversed arg order)" \
    'git\s+push\s+.*(main|master|prod(uction)?|release|staging).*(--force|--force-with-lease|-f)'

check "Fork bomb" \
    ':\(\)\s*\{\s*:\s*\|\s*:.*&'

check "Direct write to raw block device (dd)" \
    '\bdd\b.*\bof=/dev/(sd[a-z]|hd[a-z]|nvme[0-9]|vd[a-z])\b'

check "Disk formatting (mkfs)" \
    '\bmkfs\b'

check "World-writable permissions on root path" \
    'chmod\s+(-R\s+)?777\s+/'

check "Wipe filesystem signatures on block device (wipefs)" \
    '\bwipefs\b.*\s+/dev/[a-z]'

check "Flush all iptables firewall rules" \
    '\biptables\s+((-[A-Za-z]+\s+)*)?(-F|--flush)\b'

check "Truncate system file to zero bytes" \
    '\btruncate\b.*-s\s+0\s+/(etc|usr|boot|var/log|var/run|lib|sbin)/'

check "Kill all running processes (kill -9 -1)" \
    '\bkill\s+((-[0-9]+|-[A-Z]+|-SIGKILL|-KILL)\s+)+(-1|0)\b'

check "Force system shutdown or reboot without graceful unmount" \
    '\b(reboot|poweroff|shutdown|halt)\b.*\s(-f|--force)\b'

check "Kernel sysrq trigger: immediate reboot or emergency remount" \
    'echo\s+[bh]\s*>\s*/proc/sysrq-trigger'

check "Remove all cron jobs (crontab -r; commonly confused with -e)" \
    '\bcrontab\s+-r\b'

# ── Windows / PowerShell ─────────────────────────────────────────────────
check "Windows disk format (format X:)" \
    '\bformat\s+[a-z]:\b'

check "Windows Format-Volume (formats a volume)" \
    '\bformat-volume\b'

check "Windows Clear-Disk (wipes a disk)" \
    '\bclear-disk\b'

check "Recursive removal of a Windows drive root (rd /s)" \
    '\b(rd|rmdir)\b.*\s/s\b.*[a-z]:\\(\*|[[:space:]]|$)'

check "Force shutdown or restart of the computer" \
    '\b(restart-computer|stop-computer)\b.*-force\b'

# Remove-Item -Recurse -Force of a drive root or system dir
# (ERE has no lookahead → require all conditions via separate matches)
if printf '%s\n' "$CMD" | grep -qsiE 'remove-item|\bri\b' \
   && printf '%s\n' "$CMD" | grep -qsiE -- '-(recurse|r)\b' \
   && printf '%s\n' "$CMD" | grep -qsiE -- '-(force|f)\b' \
   && printf '%s\n' "$CMD" | grep -qsiE '([a-z]:\\(\*|[[:space:]]|$)|[a-z]:\\windows\b|\$env:(systemroot|windir|systemdrive))'; then
    BLOCKED="${BLOCKED}Recursive forced deletion of a Windows drive root or system directory; "
fi

[ -z "$BLOCKED" ] && exit 0
BLOCKED="${BLOCKED%; }"

echo "COMMAND GUARD: Blocked — ${BLOCKED}."
echo "This command is destructive or irreversible. Do not run it without explicit user confirmation."
echo "Explain what you were trying to accomplish and ask the user whether to proceed."
exit 2
