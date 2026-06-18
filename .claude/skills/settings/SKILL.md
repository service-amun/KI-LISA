---
name: settings
description: Configure, audit, or maintain settings.json and settings.local.json. Use when adding permissions, model selection, env vars, output style, or any other Claude Code runtime configuration.
updated: 2026-06-13
---

# Settings JSON

## 1§ Purpose
Produce valid, complete settings.json or settings.local.json files for Claude Code.
Covers permissions, model selection, environment variables, and all other runtime
configuration fields. Not for behavioral guidance — that belongs in rules or CLAUDE.md.

## 2§ Use when
- User wants to add, change, or remove a setting (permissions, model, env, etc.).
- User wants to audit an existing settings file for stale rules, conflicts, or risks.
- User wants to clean up accumulated one-off permission entries.
- User says "configure settings", "add permission", "allow/deny tool", "set model",
  "settings.json", or "settings.local.json".

## 3§ Hard constraints
- Never put behavioral instructions, style guides, or workflow guidance in settings.json —
  those belong in CLAUDE.md, rules, or skills.
- Never commit secrets, tokens, or machine-specific absolute paths to shared project
  settings (`.claude/settings.json`).
- Never add credential paths (`~/.aws/credentials`, `.env`, `secrets/**`) to `allow`
  without explicit user acceptance of the security risk.
- Never produce partial JSON — always deliver a complete, valid file.
- Preserve all existing entries not in conflict with the request.
- Always include `$schema` in produced files.
- Never author hook script logic here — the settings.json `hooks` field only wires events to companion scripts.

## 4§ Decision gate
- Authoring hook scripts (the logic behind a `hooks` entry): out of scope — that is a separate hook artifact.
- MCP server configuration (`command`, `args`, `url`, `env` per server): that belongs in `.mcp.json`, not settings.
- Behavioral guidance ("Claude should...", style rules): that is a rule.
- Always-relevant project context (commands, architecture, gotchas): that is always-loaded context (CLAUDE.md).
- Unknown field: check `$schema` at `https://json.schemastore.org/claude-code-settings.json`.
- Scope unclear: default to `settings.local.json`, label `[assumed]`, explain the trade-off.

Scope selection:

| Applies to | File |
|---|---|
| This machine only, not shared | `.claude/settings.local.json` |
| Team-shared via git | `.claude/settings.json` |
| Personal defaults across all projects | `~/.claude/settings.json` |
| Org-wide enforcement (MDM only) | `managed-settings.json` |

Precedence (highest → lowest): Managed → CLI args → Local → Project → User.
Arrays (`permissions`, `hooks`, `availableModels`) merge across scopes. Scalars override.

## 5§ Permission rules
The `permissions` object has three levels, evaluated in order — first match wins:
- `deny` — blocked entirely, no user prompt possible
- `ask` — always prompts, even if previously approved
- `allow` — pre-approved, never prompts

Rule pattern syntax:

| Pattern | Matches |
|---|---|
| `Bash(cmd *)` | Bash commands starting with `cmd` (`*` = any args, single level) |
| `Read(./path/**)` | File reads under a path (`**` = recursive) |
| `Edit(./path/**)` | File edits under a path |
| `Write` | All file writes |
| `WebFetch(domain:example.com)` | Web requests to a specific domain |
| `WebFetch(domain:*.example.com)` | Domain wildcard (all subdomains) |
| `MCP(server-name)` | All tools from a specific MCP server |
| `mcp__server-name__*` | All tools from a specific MCP server (alternative syntax) |
| `mcp__server-name__tool` | One specific MCP tool |
| `Agent` | All subagent spawns |
| `Agent(type)` | Spawning a specific subagent type |

Common deny patterns:

| Goal | Deny rule |
|---|---|
| Block all computer-use (screenshots, clicks, keyboard) | `mcp__computer-use__*` |
| Block all browser MCP tools | `mcp__Claude_in_Chrome__*` |
| Block subagent spawning entirely | `Agent` |
| Block a specific subagent type | `Agent(explore)` |

Additional permission fields:
- `additionalDirectories` — grants Read to paths outside the project root
- `defaultMode: "acceptEdits"` — pre-approves all Write/Edit without per-call prompts
- `disableBypassPermissionsMode: "disable"` — blocks `--dangerously-skip-permissions`

## 6§ Workflow

### 6.1§ Configure (add or change a field)
1. Read the target file if it exists; note if a new file will be created.
2. Apply the decision gate — confirm settings.json is the right artifact.
3. Determine scope (§4). Label `[assumed]` if defaulting.
4. Write the complete updated file. Preserve all existing entries not in conflict.
5. Confirm: output the file path and a one-line summary of what changed.

### 6.2§ Audit (review an existing file)
1. Read all accessible settings files: `settings.local.json`, `.claude/settings.json`,
   `~/.claude/settings.json`.
2. Flag: overly broad permissions, credential paths in `allow`, machine-specific
   absolute paths in shared files, behavioral prose, hook entries without companion
   scripts, scope conflicts (same key overriding unintentionally across files).
3. Report by severity: Blocker (security risk) → Warning (maintenance) → Note.
4. Propose fixes; apply only after user confirmation.

### 6.3§ Maintain (clean up)
1. Read the target file.
2. Identify stale entries (commands/paths no longer in the project) and one-off
   permissions that can be consolidated or removed.
3. Propose a cleaned version; apply after user confirmation.

## 7§ Output contract
Must include:
- `$schema` as the first key in every produced file
- Complete file content — never a partial snippet requiring manual merging
- Confirmation: file path and one-line summary of changes

Must not include:
- Comments inside `.json` files (RFC 8259 prohibits them; use `.jsonc` for annotated
  templates only)
- Trailing commas
- Behavioral instructions, prose, or style guidance
- Secrets, tokens, or credential values
- Machine-specific absolute paths in shared project files

## 8§ Associated documents
- [assets/settings.example.json] — example of a well-structured project settings.json.
