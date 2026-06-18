---
name: <PROJECT_NAME>
description: <One-sentence product spec and architecture reference for this project.>
updated: <YYYY-MM-DD>
---

# <Project Title> — Project Spec

## 1§ Goal

<!-- 1-3 sentences: what problem this solves and for whom.
Do not restate README.md or CLAUDE.md content — complement them. -->
<goal>

## 2§ Core features

<!-- Flat list of actual system behaviors, not user-facing features.
What does the system DO internally? -->
- <feature>

## 3§ Non-goals

<!-- Explicitly excluded capabilities, platforms, or use cases.
Include the reason when non-obvious. -->
- <exclusion>

## 4§ Directory structure

<!-- Key folders at 2-3 levels deep. State the role and access rules, not contents.
Omit obvious folders (node_modules/, dist/, build/). -->
```text
<project-root>/
  <dir>/         — <role and access constraint>
  <dir>/
    <subdir>/    — <role>
```

## 5§ Architecture decisions

<!-- One subsection per non-trivial decision.
Every subsection MUST include a Rationale line. -->

### 5.1§ <Decision name>

<!-- Append (locked) to the heading if this decision is not to be revisited. -->
<What was decided — one sentence.>

Rationale: <Why this over the alternatives; what constraint or incident drove the choice.>

### 5.2§ <Invariant-style decision name>

<!-- Use this shape for a decision that establishes an invariant the system relies on. -->
<What was decided, and the invariant it establishes — one or two sentences.>

Rationale: <Why; what breaks if the invariant is violated.>

## 6§ Domain vocabulary

<!-- OPTIONAL: include only when the project uses internal terms, type names, or
concepts that differ from common usage or that an AI would otherwise name wrong.
Remove this section if the project has no such vocabulary. -->
- <term> — <what it means here, and what it is NOT to be confused with>

## 7§ Invariants and gotchas

<!-- OPTIONAL but high-value: rules that must hold for correctness, and the
non-obvious traps that break the system. Remove if genuinely none apply. -->
- Invariant: <rule that must hold> — <consequence if violated>
- Gotcha: <the trap> — <what to do instead>

## 8§ AI pitfalls

<!-- OPTIONAL, grows through corrections: what an AI assistant gets wrong here and
the correction. Add one entry per prior misunderstanding so it stays fixed.
Remove this section on a fresh project until the first correction appears. -->
- <what an AI tends to assume> — <the correct behavior>

## 9§ Constraints and external dependencies

<!-- Platform requirements, external APIs, performance or sizing targets.
One bullet per discrete constraint. -->
- <constraint>
