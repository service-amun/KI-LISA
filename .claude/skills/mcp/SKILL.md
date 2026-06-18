---
name: mcp
description: Author, audit, or repair .mcp.json files for Claude Code MCP servers. All transport types (stdio, http, sse, ws), credential handling, scope selection, and settings.json permission links.
updated: 2026-06-13
---

# MCP JSON

## 1§ Purpose
Produce valid, complete `.mcp.json` files for Claude Code MCP server configuration.
Covers transport type selection, credential handling, environment variable expansion,
scope decisions, and the link between server names and `settings.json` permission rules.

Not for MCP tool permissions — those belong in `settings.json`; configure them there
when the user asks to allow/deny/ask for MCP tools.

## 2§ Use when
- User wants to add or configure an MCP server connection.
- User wants to audit an existing `.mcp.json` for credentials, stale entries, or
  invalid fields.
- User asks about `.mcp.json`, "MCP server config", "connect a tool server", or
  "how do I add an MCP server".
- User has MCP server configuration mixed into `settings.json` — extract and redirect.

## 3§ Hard constraints
- Never put credentials, API keys, or tokens as literal values — use `${VAR}` expansion
  or `headersHelper`; committed `.mcp.json` files are version-controlled.
- Never use `sse` transport for new configurations — it is deprecated; use `http`.
- Server name `workspace` is reserved by Claude Code; never use it.
- Never produce partial JSON — always deliver a complete, valid file.
- Preserve all existing server entries not in conflict with the request.
- Always include `$schema` in produced files.
- Credentials that cannot be expressed as environment variables belong in
  `headersHelper` (dynamic) or OAuth config — never inline.

## 4§ Decision gate
- MCP tool permissions (`allow`/`deny`/`ask` for MCP tools): that is a `settings.json` permissions concern.
- Hook or lifecycle automation: that is a lifecycle hook.
- Scope unclear: default to `.mcp.json` project-level, label `[assumed]`, explain trade-off.

Transport type selection — choose once per server:

| Use case | Transport |
|---|---|
| Local process (npm, Python, Go binary) | `stdio` |
| Remote API with persistent connection | `http` |
| Remote API, legacy SSE-only endpoint | `sse` (deprecated — prefer `http`) |
| WebSocket endpoint | `ws` |

Scope selection:

| Who should see this server | File |
|---|---|
| Whole team, version-controlled | `.mcp.json` (project root) |
| Personal, this project only | `~/.claude.json` → `projects.<hash>.mcpServers` |
| Personal, all projects | `~/.claude.json` → `mcpServers` |

Precedence (highest → lowest): local (personal project) → project → user.
When the same server name appears in multiple scopes, the highest-precedence entry
wins — fields are not merged across scopes.

## 5§ Transport type reference

### 5.1§ stdio (local process)
Required: `command` (executable), `args` (array of strings).
Optional: `env` (object), `timeout` (ms), `alwaysLoad` (bool).

```json
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

No automatic reconnect for stdio — local processes are relaunched by the host.
`type` field defaults to `stdio` if omitted, but always include it explicitly.

### 5.2§ http (remote server — preferred)
Required: `type: "http"`, `url` (HTTPS).
Optional: `headers`, `headersHelper`, `timeout`, `alwaysLoad`, `oauth`.

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "https://mcp.example.com/endpoint",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      },
      "timeout": 30000
    }
  }
}
```

Auto-reconnects on transient failures (5xx, timeout) with exponential backoff up to
5 attempts. Auth errors (401/403) and 404 are not retried — they require config changes.

### 5.3§ sse (deprecated)
Same fields as `http`. Only use when the remote endpoint supports SSE only and cannot
be upgraded. New configurations must use `http`.

### 5.4§ ws (WebSocket)
Required: `type: "ws"`, `url` (WebSocket URL, `wss://`).
Optional: `headers`, `headersHelper`, `timeout`, `alwaysLoad`.
OAuth is not supported for WebSocket — use `headers` with bearer token expansion.

```json
{
  "mcpServers": {
    "realtime-server": {
      "type": "ws",
      "url": "wss://mcp.example.com/socket",
      "headers": {
        "Authorization": "Bearer ${WS_TOKEN}"
      }
    }
  }
}
```

## 6§ Credential handling
Never put literal secrets in `.mcp.json`. Use one of these patterns:

Environment variable expansion (preferred for static tokens):
```json
"headers": { "Authorization": "Bearer ${API_KEY}" }
```
Set the variable in the shell profile, `.env` (gitignored), or CI/CD secrets manager.
`${VAR:-default}` syntax provides a fallback when the variable is unset.

Dynamic headers via `headersHelper` (for short-lived or rotated tokens):
```json
"headersHelper": "/opt/bin/get-mcp-headers.sh"
```
The script receives `CLAUDE_CODE_MCP_SERVER_NAME` and `CLAUDE_CODE_MCP_SERVER_URL` as
environment variables. It must print a JSON object of headers to stdout within 10 seconds.

OAuth 2.0 (for servers that support it):
```json
"oauth": {
  "clientId": "my-client-id",
  "callbackPort": 9876
}
```
Tokens are stored in the system keychain; refresh is automatic. Preferred over static
tokens when the server supports the OAuth 2.0 device or PKCE flow.

Available variable expansions in `command`, `args`, `env`, `url`, `headers`:
- `${VAR}` — shell environment variable at connection time
- `${VAR:-default}` — with fallback
- `${CLAUDE_PROJECT_DIR}` — project root directory (use `${CLAUDE_PROJECT_DIR:-.}` in
  config to provide a `.` fallback when expansion is unavailable)

## 7§ Optional field reference

`timeout` (integer, milliseconds): per-tool hard execution limit. Ignored if < 1000 ms.
For HTTP/SSE servers, the first-byte budget minimum is always 60 seconds regardless
of this value. Typical override for long-running tools: `600000` (10 min).

`alwaysLoad` (boolean, default false): exempt this server from tool deferral. When
`true`, all tools load into context at session start (requires v2.1.121+). Use only
for small, frequently-needed tool sets — large tool lists slow startup.

`headersHelper` (string): shell command path. Must output `{"Header-Name": "value"}`
JSON to stdout within 10 seconds. The script receives the server name and URL as env
vars (`CLAUDE_CODE_MCP_SERVER_NAME`, `CLAUDE_CODE_MCP_SERVER_URL`).

## 8§ Relationship to settings.json
`.mcp.json` controls how servers are configured and who can see them.
`settings.json` controls which tools Claude can use from those servers.

The server name key in `.mcp.json` maps directly to permission rules in `settings.json`:

| .mcp.json key | settings.json permission pattern |
|---|---|
| `"github"` | `MCP(github)` — all tools from github server |
| `"filesystem"` | `MCP(filesystem)` — all tools from filesystem server |

Granular tool-level permissions use `mcp__<server-name>__<tool-name>` syntax in
`settings.json`. Example: `mcp__github__create_issue`. Use `mcp__github__*` for all
tools from a server.

To disable a server without removing its config: add a `deny` rule in `settings.json`
for all its tools. There is no `disabled` field in `.mcp.json`.

Approval prompt: the first time Claude Code loads a `.mcp.json` from a project, it
prompts for approval (security check against untrusted repos). Approval is stored per
project. Reset with `!claude mcp reset-project-choices` if needed.

## 9§ Workflow

### 9.1§ Configure (add or change a server)
1. Read the target file if it exists; note if a new file will be created.
2. Apply the decision gate — confirm `.mcp.json` is the right artifact.
3. Determine scope (§4). Label `[assumed]` if defaulting.
4. Select transport type (§5). Refuse `sse` for new servers.
5. Handle credentials via §6 patterns — flag any literal values as blockers.
6. Write the complete updated file. Preserve all existing entries not in conflict.
7. State the file path, what changed, and whether companion permission rules in
   `settings.json` need to be added.

### 9.2§ Audit (review an existing file)
1. Read `.mcp.json` and, if accessible, `settings.json`.
2. Flag: literal credentials in `headers` or `env`; `sse` transport (deprecated);
   server name `workspace`; missing `$schema`; servers with no matching permission
   rules in `settings.json`.
3. Report by severity: Blocker (credential exposure, invalid config) → Warning
   (deprecated transport, missing permissions) → Note (style, redundancy).
4. Propose fixes; apply only after user confirmation.

## 10§ Output contract
Must include:
- `$schema` as the first key in every produced file
- Complete file content — never a partial snippet requiring manual merging
- Confirmation: file path, one-line summary of changes
- A follow-up note when companion permission rules in `settings.json` are needed

Must not include:
- Literal API keys, tokens, or credentials as values
- `sse` transport for new server entries
- Server name `workspace`
- Comments inside `.json` files (use `.jsonc` for annotated templates only)
- Partial files requiring manual merging

## 11§ Associated documents
- [assets/mcp.example.json] — example of a well-structured project `.mcp.json` with stdio, http, and credential patterns.
