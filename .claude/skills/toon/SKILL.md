---
name: toon
description: Convert JSON or YAML to TOON format for token-efficient LLM input. Use when reducing prompt token count on tabular or structured data, or when TOON output is explicitly requested.
updated: 2026-06-14
---

# TOON Conversion

## 1§ Purpose
Convert JSON or YAML structured data to valid TOON (Token-Oriented Object
Notation, spec v3.2, May 2026 — current) for LLM-bound INPUT — data the model
reads, not a model-output target. Always prepend the format declaration so models
parse correctly without native TOON support.

## 2§ Use when
- User provides JSON or YAML and wants to reduce token usage.
- User explicitly requests TOON output or mentions token efficiency.
- Composing a prompt with data the model READS: a uniform array, or an object whose
  bulk is one or more uniform arrays (named-array form), or a moderately nested but
  regular structure — TOON is an input format, not a model-output target.

Do not invoke when:
- Data will be passed to a non-LLM parser (API, database, tool definition) or
  rendered for humans (GitHub-facing docs).
- Tabular eligibility is low: deeply nested or heterogeneous fields between objects —
  minified JSON usually wins; fall back (§6).
- The header does not amortize: too few rows or too few fields to repay it. Five rows
  is the default heuristic — judge by rows × fields, not a fixed count: a 2-column
  table rarely pays, a wide table can pay below five.

## 3§ Hard constraints
- Always read `rules/toon-style.md` before converting — it is the authoritative
  syntax reference for this harness.
- Never output TOON with a trailing newline — the spec mandates its absence.
- Never use single quotes — only double quotes for values that require quoting.
- Always prepend the format declaration for LLM-bound output (§5).
- Always wrap TOON output in a fenced code block with the `toon` language tag.
- Always fall back to minified JSON with a reason when TOON does not apply.

## 4§ Conversion rules

### 4.1§ Structure selection
Identify the input shape and select the matching TOON structure:
- Single flat or nested object → flat object or nested object syntax.
- Array where every object shares identical field names → tabular array syntax.
- Array nested inside a parent object → named array syntax.
- Deeply nested or heterogeneous fields → minified JSON fallback (§6).

### 4.2§ Value encoding
Apply encoding rules from `toon-style.md` §2.3 exactly.

### 4.3§ Key folding
Collapse a chain of single-key nested objects into a dotted path:

```toon
server.host: localhost
server.port: 8080
```

Apply only when every level in the chain has exactly one key. Do not fold when
any level has sibling keys — that would misrepresent the structure.

### 4.4§ Syntax examples
Syntax reference and all examples: `toon-style.md` §2.4.

## 5§ Format declaration
Use the exact text from `toon-style.md` §2.6, verbatim.
Omit only when output is stored or displayed for humans, not passed to an LLM.

## 6§ Fallback
When TOON is not applicable, output minified JSON and state the reason:

```text
TOON pays off when a shared header amortizes over many uniform rows. This data
[reason], so minified JSON is used instead (~15% token savings over pretty-printed JSON).
```

Common reasons: heterogeneous fields between objects; header does not amortize (too
few rows or fields); low tabular eligibility / deep nesting where minified JSON wins;
non-LLM or human-facing destination.

## 7§ Output contract
Must include:
- Format declaration (for LLM-bound output)
- TOON in a fenced `toon` code block, no trailing newline inside the block
- Estimated token savings relative to pretty-printed JSON

Must not include:
- Trailing newline at the end of the TOON content
- Single-quoted values
- Inline comments within tabular data rows
- TOON output intended for non-LLM consumption

## 8§ Associated documents
- [rules/toon-style.md] — authoritative TOON syntax reference for this harness;
  read before every conversion. No skill-local assets: the rule fully specifies
  the output format.
