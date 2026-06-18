<!-- rule.template.md — Strip ALL HTML comment blocks before writing a production rule file -->

<!-- FRONTMATTER: Choose one block, delete the other. -->

<!-- Global rule (loads every session): -->
---
description: "<Specific one-line description of what this rule enforces>"
alwaysApply: true
---

<!-- Path-scoped rule (loads only when matching files are active): -->
---
description: "<Specific one-line description of what this rule enforces>"
globs:
  - "<glob-pattern>"
alwaysApply: false
---

<!-- Replace H1 with the rule topic in Title Case -->
# <Topic>

## 1§ Scope
<!-- When and where this rule applies.
Name the file types, contexts, or situations it governs.
State what it does NOT cover if confusion is likely. -->

## 2§ Rules
<!-- The actual conventions, standards, or requirements.
For simple rules: a flat bullet list.
For complex topics with distinct sub-concerns (e.g. file formats): add numbered
subsections: ### 2.1§ <Sub-topic>, ### 2.2§ <Sub-topic>, etc.
Each entry must be concrete and verifiable — no vague guidance. -->
- <Convention or requirement.>

## 3§ Preferred patterns
<!-- Explicit defaults: "A over B when condition C." At least one entry.
Show the positive direction — not just what to avoid. -->
- <Prefer A over B because C.>

## 4§ Avoid
<!-- Anti-patterns that must not appear. At least one entry.
Where the reason is non-obvious, add a short explanation after the dash. -->
- <Anti-pattern> — <reason or alternative>.
