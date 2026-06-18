---
name: hooks
description: Create or update Claude Code hook configurations — settings.json entries and companion scripts for lifecycle event automation, policy enforcement, logging, and validation.
updated: 2026-06-13
---

# Hook Create

## 1§ Purpose
Produce settings.json hook entries and companion scripts for Claude Code lifecycle
automation. Use for deterministic actions tied to lifecycle events: blocking tool calls,
validating output, logging activity, or running setup on session start.

## 2§ Use when
- User wants to block, validate, or log a specific tool call.
- User wants to run a check after file edits (lint, format, test).
- User wants setup or teardown logic on session start or stop.
- User wants to enforce policies beyond what permission rules allow.
- User wants to audit or verify an existing hook against these conventions (companion script exists, exit-code semantics documented, correct event and matcher).
- User says "hook", "intercept", "pre-tool", "post-tool", "block", "enforce", or
  "run a script when Claude...".

## 3§ Hard constraints
- Never put hook logic in CLAUDE.md or rules — hooks belong in settings.json.
- Always produce a complete hook entry in settings.json, never a partial snippet.
- Write complex logic to a companion script — do not inline multi-line shell logic
  in the `command` field.
- Exit 2 to block an action; exit 1 shows a warning but does not block.
- Read stdin exactly once per script.
- Include a bash shebang (`#!/usr/bin/env bash`) and `set -euo pipefail` in all
  bash companion scripts. Exception: hooks that must never block (cleanup,
  logging) may omit strict mode when every failure path is explicitly tolerated —
  document the omission in the script header.
- Never use `suppressOutput: true` on security-relevant hook output.
- Always reference companion scripts via `${CLAUDE_PROJECT_DIR}/.claude/hooks/<name>.sh`.

## 4§ Decision gate
- Behavioral guidance ("Claude should prefer...") → a rule, not a hook.
- Permission allow/deny rules (not lifecycle hooks) → a settings.json permission entry, not a hook.
- Always-relevant project context → always-loaded context (CLAUDE.md), not a hook.
- Hook vs. rule unclear: hooks execute code deterministically on an event; rules are
  advisory. If the intended action is a shell command or HTTP call, it is a hook.

## 5§ Lifecycle events
Key events for most hook use cases:

| Event | Fires when | Can block |
|---|---|---|
| `PreToolUse` | Before any tool executes | Yes |
| `PostToolUse` | After a tool succeeds | No |
| `PostToolUseFailure` | After a tool fails | No |
| `PermissionRequest` | Permission dialog fires; before auto-mode approval | Yes |
| `PermissionDenied` | Tool call denied by auto mode | No |
| `UserPromptSubmit` | Before Claude processes the user prompt | Yes — erases prompt; 30 s timeout |
| `Stop` | Claude finishes a turn | Yes — prevents stop; conversation continues |
| `SessionStart` | Session begins, resumes, or follows `/clear` or compaction | No |
| `SessionEnd` | Session terminates | No |
| `Setup` | One-time initialization via `!claude --init` | No |
| `PreCompact` | Before context compaction | Yes |
| `PostCompact` | After context compaction completes | No |
| `SubagentStart` | Subagent spawned | No |
| `SubagentStop` | Subagent finishes | Yes |

Matchers for tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`,
`PermissionRequest`, `PermissionDenied`): exact tool name (`Bash`, `Edit`),
pipe-separated list (`Bash|Edit`), JavaScript regex, or `*` for all.
MCP tools use `mcp__<server>__<tool>` pattern.
Matchers for `SessionStart`: `startup`, `resume`, `clear`, `compact`.
Matchers for `SessionEnd`: `clear`, `resume`, `logout`, `prompt_input_exit`, `other`.
Matchers for `PreCompact` and `PostCompact`: `manual` (user-triggered `/compact`),
`auto` (context-threshold compaction).
Matchers for `Setup`: `init`, `maintenance`.
Matchers for `SubagentStart` and `SubagentStop`: agent type name (`general-purpose`,
`Explore`, `Plan`, or any custom agent name).
Events with no matcher support: `Stop`, `UserPromptSubmit`, `PostToolBatch`.

Claude Code documents further usable events beyond the table above — fetch the
official hooks reference for their matchers and payloads before targeting one:
`Notification`, `MessageDisplay`, `UserPromptExpansion`, `TaskCreated`,
`TaskCompleted`, `StopFailure`, `TeammateIdle`, `InstructionsLoaded`,
`ConfigChange`, `CwdChanged`, `FileChanged`, `WorktreeCreate`,
`WorktreeRemove`, `Elicitation`, `ElicitationResult`.

Optional `if` field on any handler for finer filtering using permission-rule syntax:
`Bash(rm *)`, `Edit(*.ts)` — one rule per handler, no compound operators.

## 6§ Handler types

| Type | Use for | Stability |
|---|---|---|
| `command` | Shell script (bash / PowerShell) | Stable |
| `http` | POST to a webhook URL | Stable |
| `mcp_tool` | Call a connected MCP server tool | Stable |
| `prompt` | Yes/no question answered by Claude | Experimental |
| `agent` | Spawn a subagent for evaluation | Experimental |

Default to `command`. Use `http` for external service integrations. Avoid `prompt`
and `agent` in production hooks — semantics are not yet finalized.

## 7§ Configuration

Three-level structure: event → matcher group → handler array.

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/pre-bash.sh",
          "timeout": 30
        }
      ]
    }
  ]
}
```

Exit code semantics for `command` handlers:

| Exit code | Effect |
|---|---|
| `0` | Success; stdout JSON parsed for decision fields. For `SessionStart`, `UserPromptSubmit`, and `UserPromptExpansion`, plain stdout is added to Claude's context |
| `2` | Blocking; stderr (not stdout) is fed back to Claude, action stopped |
| any other | Non-blocking; stderr shown as warning, action continues; stdout ignored |

JSON output (stdout, exit 0) — key fields:

- PreToolUse deny: `{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"...","updatedInput":{...}}}`
- General block: `{"decision":"block","reason":"..."}`
- Stop session: `{"continue":false,"stopReason":"..."}`
- Hide hook output: `{"suppressOutput":true}`
- SessionStart context injection: `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"...","sessionTitle":"...","watchPaths":[...],"reloadSkills":true}}`
- Stop additional context: `{"hookSpecificOutput":{"hookEventName":"Stop","additionalContext":"..."}}`

Each JSON schema above is event-specific — select by the event the handler is
registered on; fields from another event's schema are ignored. For `SessionStart`
context injection, plain stdout on exit 0 and the `additionalContext` JSON field
are equivalent; use JSON only when `sessionTitle`, `watchPaths`, or
`reloadSkills` are also needed.

Input to every hook (stdin JSON) includes `tool_name`, `tool_input`, `cwd`,
`session_id`, and `hook_event_name`. Parse with `jq` in bash scripts.

Note: `SessionStart` only supports `command` and `mcp_tool` handler types —
`http`, `prompt`, and `agent` types are ignored on this event.

## 8§ Workflow
1. Apply decision gate — confirm a hook is the right artifact.
2. Identify the trigger: what event and which tool or context should fire the hook.
3. Select lifecycle event (§5) and handler type (§6).
4. Determine scope: `.claude/settings.json` (team-shared) or `~/.claude/settings.json`
   (personal). Label `[assumed]` when defaulting.
5. Determine the response: exit 2 to block, exit 0 + JSON for structured decisions,
   exit 0 alone for logging or side effects.
6. Write the complete settings.json hook entry.
7. Write the companion script: read stdin once, process, output JSON if needed, exit
   with the correct code. Bash on Unix/Mac; PowerShell on Windows
   (`$input = [Console]::In.ReadToEnd() | ConvertFrom-Json`).
8. Confirm: state both file paths and a one-line summary of what fires and when.

## 9§ Output contract
Must include:
- Complete settings.json hook entry — not a snippet
- Companion script with shebang, `set -euo pipefail`, single stdin read, explicit exit code
- Both file paths
- One-line summary of hook purpose and trigger event

Must not include:
- Multi-line logic inlined in `command` — use a companion script
- Exit code 1 where exit 2 is intended for blocking
- `suppressOutput: true` on security-relevant output
- Partial JSON requiring manual merging
- Behavioral guidance — that belongs in rules

## 10§ Associated documents
- [assets/hook.example.sh] — companion script template with stdin/stdout/exit code pattern.
