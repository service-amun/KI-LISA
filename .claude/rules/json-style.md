---
name: json-style
description: House conventions for JSON files in this harness. Format selection is in CLAUDE.md.
updated: 2026-06-11
---

# JSON Style

## 1§ Scope
Applies to all `.json` and `.jsonc` files: `settings.json`, `.mcp.json`,
`hooks.json`, API payloads, and tool definitions. Format selection is in [CLAUDE.md].

## 2§ Rules

### 2.1§ Document conventions
- Encoding: UTF-8 without BOM — a BOM (`﻿`) breaks strict parsers.
- Line endings: LF (`\n`) only, never CRLF.
- Trailing newline: end every file with a single `\n` (POSIX convention).
- File extension: `.json` for strict RFC 8259 files; `.jsonc` when comments are
  required (VS Code config, annotated templates).

### 2.2§ Keys
- Claude Code config files (`settings.json`, `hooks.json`, `.mcp.json`): `camelCase`.
- Custom API payloads: `camelCase` or `snake_case`, consistent within one file —
  never mixed.
- Ordering: required and frequently-accessed keys first, optional keys last.
  No alphabetical sorting.
- Array-typed keys: plural names (`users`, `items`). Scalar keys: singular.

### 2.3§ Values
- Strings: use literal UTF-8 characters. Escape only control characters
  (U+0000–U+001F) and the characters the spec mandates (`\"`, `\\`).
  Never use `\uXXXX` escapes for printable Unicode.
- Numbers: no leading zeros (`7` not `007`). Decimal notation for normal range;
  scientific notation only for very large or very small values. Represent integers
  above 2^53 as strings to avoid precision loss.
- Booleans: `true` / `false` only (lowercase).
- Null: use `null` when a key exists but has no value. Omit the key entirely
  when absence is the intended state.
- Empty collections: `[]` for empty arrays, `{}` for empty objects — never
  `null` in place of a missing collection.
- Dates: ISO 8601 string with timezone: `"2026-06-10T14:00:00Z"`.

### 2.4§ Formatting
- Human-editable files: pretty-print with 2-space indentation.
- LLM-bound payloads: minify (no whitespace) — saves ~15% tokens.
- Always double-quote keys and string values. Never use single quotes.
- No trailing commas after the last element of an object or array.

### 2.5§ Comments
- Strict JSON (`.json`): no comments. RFC 8259 prohibits them.
- When comments are needed: use `.jsonc` extension. JSONC supports `//`
  single-line and `/* */` multi-line comments. Make the extension change
  explicit in any README.
- Never use the `_comment` key pattern — it pollutes the data model.

## 3§ Preferred patterns
- `.jsonc` extension over the `_comment` key for annotated or template files —
  keeps the data model clean and signals intent to editors.
- Omit optional keys over setting them to `null` when intentional absence is the
  meaning — `null` means "exists but has no value", not "does not exist".
- Literal UTF-8 characters over `\uXXXX` escapes for printable Unicode — easier
  to read and edit without changing the value.
- Explicit `[]` or `{}` over `null` for empty collections — preserves the type
  and prevents callers from needing a null check before iterating.

## 4§ Avoid
- Trailing commas — parsers reject them.
- Single-quoted keys or string values.
- BOM prefix.
- Comments in `.json` files — use `.jsonc` if comments are needed.
- `undefined`, `NaN`, `Infinity` — these are not valid JSON values.
- Integer values above 2^53 as unquoted numbers.
