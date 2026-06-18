---
name: toon-style
description: House conventions for TOON output in this harness. Includes full syntax reference because Claude does not parse TOON natively. Format selection is in CLAUDE.md.
updated: 2026-06-14
---

# TOON Style

## 1§ Scope
TOON (Token-Oriented Object Notation, spec v3.2, May 2026 — current) encodes the
JSON data model with minimal punctuation. Official spec: [toonformat.dev](https://toonformat.dev/)
TOON is an LLM-INPUT format: benchmarks validate models reading it (~40% fewer
tokens than JSON at equal or better retrieval accuracy), not generating it as output.

Apply TOON when all three conditions hold:
- Shape fits: a uniform array (objects share identical fields and primitive values),
  a flat object, or an object whose bulk is one or more uniform arrays (named-array
  form). Moderately nested but regular structures still qualify.
- Data is LLM-bound: sent in a prompt or context window, or stored in a file whose
  only consumer is an LLM (e.g. the harness skill and agent indexes).
- The shared header amortizes: TOON's saving comes from one header row replacing
  repeated keys, so payoff scales with rows × fields. Five rows is the default
  heuristic — a wide table (many fields) pays earlier; a 2-column table barely pays
  at any length. Judge by amortization, not a fixed row count.

Decide against the real baseline (minified JSON, not pretty) by tabular eligibility —
the share of the data expressible as uniform rows:
- High (>~60%): TOON wins clearly, 30–60% fewer tokens than JSON.
- Partial (~40–60%): savings shrink — prefer minified JSON if the pipeline uses it.
- Low (<~40%, deeply nested/heterogeneous): minified JSON usually wins — fall back.

Do not apply TOON to tool definitions, skill/agent manifests, settings files, API
payloads, human-facing or GitHub-rendered docs, or any file a non-LLM parser must
read. For latency-critical paths measure TTFT — fewer tokens is not always faster.

## 2§ Rules

### 2.1§ Document conventions
- Encoding: UTF-8 only (mandatory per spec).
- Line endings: LF (`\n`) only, never CRLF.
- Trailing newline: TOON spec mandates NO trailing newline — differs from JSON
  and YAML. Omit the final `\n`.
- File extension: `.toon`.
- Media type: `text/toon`.
- File descriptor: the first line of every stored TOON file must be a `#`
  comment stating the file's purpose and format in one sentence. This is the
  TOON equivalent of document frontmatter.

### 2.2§ Keys
- Implementations must preserve key order (spec requirement). Order by semantic
  importance — required and frequently-accessed keys first.
- Naming: follow the naming convention of the originating data source.

### 2.3§ Values
- Strings: use unquoted strings when unambiguous — reduces token count. Apply
  double quotes when the value is empty, has leading/trailing whitespace, equals
  `true`/`false`/`null`, looks like a number, or contains any of:
  `: `, `"`, `\`, `[`, `]`, `{`, `}`, ` | `, or control characters.
  Single quotes are not supported — only double quotes.
- Numbers: canonical decimal notation for the range [1e-6, 1e21) and zero.
  Scientific notation outside this range. No leading zeros. `-0` normalized to
  `0`. `NaN` and `±Infinity` converted to `null`. Integers above 2^53 as quoted strings.
- Booleans: `true` / `false` only (lowercase).
- Null: `~` (preferred in TOON) or `null`.
- Empty values: `""` for empty string; `[]` for empty array; `{}` for empty object.
- Escape sequences inside quoted strings: `\\`, `\"`, `\n`, `\r`, `\t`,
  `\uXXXX`. Control characters (U+0000–U+001F) must use `\uXXXX`.

### 2.4§ Syntax reference
Claude does not parse TOON natively. Use this reference when producing TOON.

Flat object — one `key: value` pair per line, one space after the colon:
```toon
name: Alice
age: 30
active: true
```

Nested object — indent child keys by 2 spaces, no closing brace:
```toon
user:
  name: Alice
  role: admin
config:
  timeout: 30
  retries: 3
```

Uniform array (tabular) — field names on header line separated by ` | `, one
data row per record in the same field order:
```toon
name | age | city
Alice | 30 | Berlin
Bob | 25 | Munich
Carol | 28 | Hamburg
```

Named array inside an object — indent header and data rows under the parent key:
```toon
users:
  name | age | city
  Alice | 30 | Berlin
  Bob | 25 | Munich
```

Quoting and null in tabular rows:
```toon
name | note | score
Alice | "Lead developer, Berlin" | 95
Bob | "Intern | trainee" | ~
Carol | Manager | null
```

Key folding — single-key chains collapsed to dotted paths:
```toon
server.host: localhost
server.port: 8080
```

### 2.5§ Token savings
Measured on Claude's tokenizer:

| Format | Relative tokens |
|---|---|
| Pretty-printed JSON | 100% |
| YAML | ~95% |
| Minified JSON | ~85% |
| TOON | ~40% |

Savings are largest on uniform tabular arrays (30–60% vs JSON in benchmarks).

### 2.6§ Format declaration
Claude does not yet parse TOON natively. Prepend this declaration before every
TOON block delivered to an LLM:

```text
The following data is in TOON (Token-Oriented Object Notation).
Syntax: key: value pairs; nested objects via 2-space indent; uniform arrays as
a header row of field names separated by " | " followed by data rows in the
same order; null as ~; values containing " | ", ":", or special characters are
double-quoted.
```

The `toon` skill generates this declaration automatically.

### 2.7§ Comments
- Syntax: `#` starts a comment; runs to end of line.
- Placement: standalone lines only — inline comments are not supported by spec.
- Spacing: one space between `#` and the comment text.
- Use sparingly — every comment line costs tokens in LLM-bound output.
- Never include secrets or credentials in comments.

## 3§ Preferred patterns
- Unquoted strings over quoted when the value is unambiguous — every unnecessary
  quote pair adds tokens in LLM-bound output.
- `~` over `null` for null values — idiomatic TOON, one character shorter.
- Tabular array format over repeated flat key-value blocks for uniform data —
  the shared header row is TOON's primary token-efficiency mechanism.
- One descriptive `#` header comment over multiple comment lines — each comment
  line costs tokens; a single file-descriptor comment is sufficient.

## 4§ Avoid
- Trailing newline — the spec explicitly mandates its absence.
- CRLF line endings — LF only.
- Tabs for indentation — 2 spaces only.
- Inline comments (after a value on the same line) — standalone lines only.
- Single-quoted strings — double quotes only.
- `NaN` or `±Infinity` as values — convert to `null`.
- TOON for stored files, API payloads, or tool definitions.
