---
name: yaml-style
description: House conventions for YAML files and frontmatter blocks in this harness. Format selection is in CLAUDE.md.
updated: 2026-06-11
---

# YAML Style

## 1§ Scope
Applies to `.yaml` and `.yml` files, and to YAML frontmatter blocks inside
Markdown files. Frontmatter field ordering follows [rules/md-style.md] §2.1.
Format selection is in [CLAUDE.md].

## 2§ Rules

### 2.1§ Document conventions
- Encoding: UTF-8.
- Line endings: LF (`\n`) only, never CRLF.
- Trailing newline: end every file with a single `\n` (POSIX convention).
- Document start marker (`---`): optional for single-document files; required
  between documents in a multi-document stream.
- Document end marker (`...`): use only in streaming contexts where the parser
  must signal end-of-document. Omit otherwise.
- Multi-document files: separate each document with `---`. Use only when a
  single file logically contains independent documents (e.g. multiple Kubernetes
  manifests).

### 2.2§ Indentation
- 2 spaces per level. Never tabs — YAML parsers reject them.
- No blank lines inside a frontmatter block.
- One blank line between top-level keys when a block has more than three keys.

### 2.3§ Keys
- Ordering: required and frequently-accessed keys first, optional keys last.
  No alphabetical sorting.
- Naming: follow the convention of the consuming system. For Claude Code
  frontmatter use the reserved field names listed in [rules/md-style.md] §2.1.

### 2.4§ Values
- Style: block style by default. Use flow style (`{key: val}`, `[a, b]`) only
  for genuinely short, single-line structures. Never with Jinja2 templates.
- Strings: quote only when required. Do not over-quote — unquoted values are
  more readable and more token-efficient. Use double quotes when a value
  contains `: `, `#`, `{`, `}`, `[`, `]`, `|`, `>`, `&`, starts/ends with
  whitespace, or would be misread as a boolean or number. Use single quotes
  only when the value itself contains double quotes.
- Booleans: `true` / `false` only (lowercase). Never `yes`, `no`, `on`, `off`
  — YAML 1.1 parsers silently coerce these to booleans.
- Null: `null` (lowercase) for JSON interoperability. Omit optional keys
  instead of setting them to null where possible.
- Numbers: let YAML infer the type. Use `!!str` to force a string type only
  when implicit parsing produces the wrong type. No other type tags.
- Multiline strings: `|` (literal block) when line breaks are significant.
  `>` (folded block) for prose that wraps visually but is logically one paragraph.
  Never inline `\n` escapes.
- Dates: YAML implicitly parses ISO 8601 dates to datetime objects. Use `!!str`
  if a date string must remain a string.

### 2.5§ Comments
- Syntax: `#` starts a comment; runs to end of line.
- Spacing: exactly one space before `#`; one space between `#` and the text.
- Placement: prefer a standalone comment on the line above the item it describes.
  Inline comments allowed but use sparingly — they reduce readability on long lines.
- Indentation: match the indentation level of the item being commented.
- Style: start with a capital letter. Use `TODO:` and `NOTE:` prefixes for
  action items and callouts.
- Never include secrets, tokens, or credentials in comments.

## 3§ Preferred patterns
- Block style over flow style for any structure with more than two keys or any
  nested value — readability degrades quickly in flow style.
- Omit optional keys over `key: null` when intentional absence is the meaning —
  a missing key is cleaner than an explicit null callers must check.
- Double quotes over single quotes when quoting is necessary — consistent with
  JSON and avoids confusion in mixed-format files.
- Standalone comment lines over inline comments for anything longer than a short
  callout — inline comments on long value lines are hard to read.
- `|` literal block scalar over `\n` escape sequences for multiline strings —
  line breaks stay visible and the value is easier to edit.

## 4§ Avoid
- Tabs — parsers reject them.
- `yes`, `no`, `on`, `off` as boolean values — use `true`/`false`.
- Anchors (`&`) and aliases (`*`) in production files — they confuse LLM
  parsers; duplicate the value instead.
- Flow style for complex or nested structures.
- Explicit type tags (`!!str`, `!!int`, etc.) except where implicit parsing
  is genuinely wrong.
- Secrets or credentials in comments.
