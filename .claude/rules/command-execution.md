---
name: command-execution
description: Claude always executes commands via its own tools, never asks the user to run CLI manually. Fallback for UAC/interactive cases: a launcher at project root — .bat on Windows, .sh on Unix.
alwaysApply: true
updated: 2026-06-13
---

# Command Execution

## 1§ Scope
Applies to every session in any project using this harness. Governs how shell
and system commands are handled.

## 2§ Rules
- Always execute shell commands directly using the Bash or PowerShell tool.
  Never output a command and ask the user to run it manually.
- If a command genuinely cannot be executed by Claude (UAC/sudo elevation, interactive
  authentication, GUI-session context): create a launcher at the project root — a `.bat`
  on Windows, a `.sh` (with `#!/usr/bin/env bash`, made executable via `chmod +x`) on macOS/Linux.
- Windows `.bat` launchers invoke PowerShell internally:
  `powershell -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -File "%~dp0script.ps1"`
- Unix `.sh` launchers invoke the target directly (`bash "$(dirname "$0")/script.sh"`), or
  `pwsh -File` when the logic is PowerShell and `pwsh` is present.
- Never use `.vbs` for new scripts — VBScript is deprecated and disabled by
  default in Windows 11 Phase 2 (estimated 2026-2027).
- Single-use launchers: delete after the user confirms successful execution.
  Reusable launchers (recurring build, migration scripts): keep and document in CLAUDE.md.
- Name launchers descriptively: `install-deps.bat`, `run-migration.bat`.

## 3§ Preferred patterns
- Bash or PowerShell tool for everything executable within Claude's session context.
- A launcher (`.bat` on Windows, `.sh` on Unix) only when direct execution is genuinely
  impossible — not as a convenience.
- One launcher per distinct operation, not one per command.

## 4§ Avoid
- Asking the user to open a terminal and enter any command.
- Using `.vbs` for any new script.
- Creating a launcher when Claude can execute the command directly.
- Leaving orphaned launcher files (`.bat`/`.sh`) in the project root after use.
