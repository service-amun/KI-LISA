---
name: md-style
description: House style for all LLM-authored markdown produced in this harness: frontmatter, sections, lists, code blocks, links, and prohibited elements.
updated: 2026-06-13
---

# Markdown Style

## 1§ Scope
Applies to every markdown file produced in this harness, with no per-type enumeration.
Format selection is handled in [CLAUDE.md].

Exempt — documents that have their own authoring skill, which owns their conventions
instead of this rule: `README*.md`, `CHANGELOG.md`, and `CLAUDE.md`. Every other
markdown file follows this rule in full.

## 2§ Rules

### 2.1§ Frontmatter
- Order fields: `name` first, `description` second, any machine-readable fields, `updated` last.
- `description:` value: max 200 characters, one compound sentence. Used verbatim as the index
  entry — never write separate long and short versions for the same artifact.
- Include machine-readable metadata only — no prose or comments in production files.
- Use frontmatter only where the file type consumes it (rules, skills, agents).
- Reserved field names — do not repurpose for unrelated metadata:
  - Rules: `name`, `description`, `globs`, `alwaysApply`, `updated` — `paths`
    also exists in Claude Code but is banned in this harness (see `rules` §3)
  - Skills: `description`, `disable-model-invocation`, `disallowed-tools`
  - Agents: `name`, `description`, `model`, `tools`, `disallowedTools`, `skills`,
    `permissionMode`, `maxTurns`, `effort`, `isolation`, `memory`
- YAML 1.1 parsers interpret `yes`, `no`, `on`, `off` as booleans — use
  `true`/`false` or quote the value. Full boolean rules in [rules/yaml-style.md] §2.

### 2.2§ Sections
- Number every major section: `## 1§ Title`, `## 2§ Title`.
- Number subsections one level deep only: `### N.M§ Title`. No deeper nesting.
- Use exactly one H1 per file; never skip a heading level.
- Cross-reference with the `N§` shorthand only — never "see the section above".

### 2.3§ Inline code
- Backtick everything a system interprets literally: filenames, paths, field
  names, values, commands.
- Prefix shell commands with `!`: `!git diff --staged`.
- Do not backtick section names, labels, or descriptive prose.

### 2.4§ Lists
- Number a list only when steps are sequential and order matters; begin each step
  with an imperative verb.
- Use bullets for every other enumeration.
- Nest at most one level deep.

### 2.5§ Code blocks
- Give every fenced block a language identifier. A bare ` ``` ` without identifier
  is a defect.

### 2.6§ Links
- Internal files: `[path/to/file.md]` — path only, no display text.
- External URLs: `[display text](https://url)`.

### 2.7§ Placeholders
- Mark fillable fields with `<PLACEHOLDER>` syntax: `<SKILL_NAME>`.
- Leave no unfilled `<PLACEHOLDER>` in a production file; templates may.

### 2.8§ Comments
- Templates only: `# text` end-of-line for fields, `<!-- ... -->` for body guidance.
- Strip all comments before delivering a production file — a comment in a
  production file is a defect.

### 2.9§ Diagrams
- Mermaid is allowed in any skill or rule file where a flow diagram genuinely
  replaces complex prose — decision trees, multi-party sequences, state lifecycles.
  Load the `mermaid` skill before generating a diagram; apply its brand palette (§5).
- One diagram per document maximum. If the document is always-loaded (e.g. CLAUDE.md),
  weigh the permanent token cost against the clarity gain — use only when the diagram
  replaces a table or prose block that is harder to read without it.
- Fenced code block identifier: always ` ```mermaid `.
- GFM alerts (`> [!NOTE]`, `> [!WARNING]`, etc.) render only on GitHub. They are
  blockquotes syntactically and add no value in LLM-facing files (rules, skills loaded
  into context). Restrict GFM alerts to `README.md` and other human-facing docs that
  are never injected into LLM context.

## 3§ Preferred patterns
- Numbered lists for sequential, order-dependent steps; bullet lists for all
  other enumerations — never number a list whose order does not matter.
- `N§` cross-reference shorthand over "see Section X", "see above", or anchor
  links — section numbers survive restructuring; prose references do not.
- `[path/to/file.md]` path-only format for internal links; display text only
  for external URLs where the URL alone is not self-explanatory.
- HTML comment blocks for authoring guidance in template body sections; explicit
  section labels (`Important:`, `Note:`) over bold emphasis for callouts.

## 4§ Avoid
- Bold, italic, strikethrough — tokenization strips markup and models do not act
  on it; use explicit labels (`Important:`), headings, or lists instead.
- Blockquotes — use a labeled line or a bullet list instead.
- Horizontal rules in the body. Exception: frontmatter delimiters, and template
  files using `---` as output-frontmatter delimiters.
- Middle-dot enumeration (`a · b · c`).
