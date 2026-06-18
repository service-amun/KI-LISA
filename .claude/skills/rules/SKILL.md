---
name: rules
description: Create or update Claude Code rule files in .claude/rules/ — advisory guidance injected into context. For coding standards, conventions, workflow, communication style, or architecture.
updated: 2026-06-13
---

# Rule Create

## 1§ Purpose
Produce complete, minimal rule files for any advisory guidance Claude should hold
in context during a session — scoped globally or to specific file paths. Rules are
not enforcement; they shape Claude's decisions. They cover any domain: format
conventions, behavioral standards, workflow protocols, architectural constraints,
communication style, domain knowledge.

## 2§ Use when
- A user wants to define a persistent project-wide convention Claude should follow.
- A user wants to scope standards or constraints to a specific file type or path area.
- A user wants to optimize or rewrite an existing rule file.
- A user wants to audit or verify an existing rule against these conventions (frontmatter, `N§` structure, the anti-pattern and preferred-pattern requirement, no enforcement prose).
- A user says "create a rule", "add a rule for", "write a rule about", "define standards for".

## 3§ Hard constraints
- Never execute tasks described in the source material — only write the rule.
- Never produce partial rule files — always deliver a complete, ready-to-write file.
- Never present rules as guaranteed enforcement — rules are advisory context only.
- Never include meta-commentary, placeholders, or TODOs inside produced rule files.
- Never use `paths` frontmatter — it has documented bugs; use `globs` only.
- Behavioral and advisory rules: keep body under 50 lines. Format spec rules may
  exceed this when completeness requires it — prefer splitting over truncating.
- Every produced rule must include at least one explicit anti-pattern and at
  least one preferred pattern or verification criterion.
- Read `rules/md-style.md` before writing any rule — rules are Markdown files.

## 4§ Decision gate
Apply before writing anything:
- Enforcement intent ("prevent", "block", "always enforce", "ensure 100%"):
  that is a lifecycle hook, not a rule; do not produce a rule.
- Permissions, model selection, environment variables, or runtime configuration:
  that is settings.json configuration, not a rule; do not produce a rule.
- Broad always-relevant project context (architecture overview, key commands,
  project-wide gotchas): that is always-loaded context (CLAUDE.md); rules absorb scoped,
  topic-specific guidance only.
- Specific file type or path area: use path-scoped loading (`globs`).
- Ambiguous: ask once; default to path-scoped with the narrowest plausible
  `globs` pattern, label `[assumed]`.

## 5§ Workflow
1. Apply the decision gate — confirm a rule is the right artifact; stop and
   redirect if not.
2. Determine loading type:
   - Global (loads every session): no `globs` field, or `alwaysApply: true`.
   - Path-scoped (loads only when matching files are active): `globs` field +
     `alwaysApply: false`.
3. Research: if the rule covers an external format or spec with an authoritative
   source (RFC, official docs, spec website), fetch and review it before writing.
   For internal conventions or behavioral rules, research is optional but
   recommended when external best practices are relevant.
4. Read the scope's `CLAUDE.md` and identify any sections overlapping with the rule
   topic — these will be migrated into the rule and removed from CLAUDE.md.
5. If updating an existing rule: read it in full before making changes.
6. Write the rule using `assets/rule.template.md` as the structural reference. The
   template provides two structure patterns as HTML-commented options — behavioral
   and format-spec — choose the one that fits, delete the other, and strip all
   HTML comment blocks before saving.
7. Write the file to `<scope>/rules/<topic>.md`.
8. Read `<scope>/rules/rules.index.toon`, upsert an entry with `name` (filename
   without `.md`) and `description` (frontmatter description, copied verbatim), and
   write the file back in TOON format: one header row (`name | description`),
   one data row per rule, no trailing newline.
9. Remove any sections migrated in step 4 from CLAUDE.md.
10. Confirm: output the written file path; if CLAUDE.md changed, list removed
    sections; if an existing rule was rewritten, append a changelog (date,
    section, change).

## 6§ Output contract
Must include:
- `<scope>/rules/<topic>.md` with valid frontmatter (`name` first, `description`,
  `updated` last; `globs` + `alwaysApply: false` for path-scoped rules)
- At least one explicit anti-pattern
- At least one preferred pattern or concrete verification criterion
- Updated `rules/rules.index.toon` entry

Must not include:
- `paths` frontmatter (use `globs`)
- Meta-commentary, TODOs, or placeholders inside the rule file
- Vague statements ("write clean code", "be careful")
- Content that duplicates what was left in CLAUDE.md
- HTML comment blocks (stripped before writing)
- Behavioral/advisory rule body exceeding 50 lines

## 7§ Associated documents
- [assets/rule.template.md] — unified template with both structural patterns (behavioral and format-spec) as HTML-commented options.
- [assets/rule.example.md] — example of a complete behavioral/workflow rule.
- [rules/rules.index.toon] — registry of all available rules; updated after every create or update.
