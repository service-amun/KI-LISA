---
name: file-project
description: Create or update PROJECT.md — the LLM-facing complement to README.md. Documents goal, architecture decisions with rationale, non-goals, and constraints. For project start or major changes.
updated: 2026-06-14
---

# Project Create

## 1§ Purpose
Produce a complete PROJECT.md that gives AI assistants the structural context
they need to work correctly in a project. PROJECT.md documents HOW the project
works — its architecture decisions, data models, invariants, and constraints.

PROJECT.md sits between two neighbours; keep all three boundaries sharp:
- README.md answers "what does this do?" for human users — feature-oriented.
  PROJECT.md answers "how is this built and why?" for AI assistants — structure-oriented.
- CLAUDE.md answers "how do I operate here?" — session and process rules, commands,
  routing, always loaded. PROJECT.md is the structural reference, loaded on demand.
  Operative rules go to CLAUDE.md; architecture, decisions, and invariants go here.

Never duplicate README or CLAUDE.md content. A PROJECT.md that restates either is
waste; an AI can read all three. Internal mechanics displaced from the README —
configuration load order, lifecycle, data flow, build internals — land here, not in
the README and not as operative rules in CLAUDE.md.

## 2§ Use when
- Starting a project that will have AI-assisted development.
- An existing project has no PROJECT.md and AI sessions repeatedly re-derive architecture.
- A PROJECT.md is stale after major refactors or new features.
- The user says "write a project spec", "document the architecture", "update PROJECT.md".
- A CLAUDE.md is growing too large with architecture content that belongs in PROJECT.md.

## 3§ Hard constraints
- Never produce a partial file — always deliver a complete, ready-to-write PROJECT.md.
- Never duplicate README.md content — different audiences, different purpose.
- Every architecture decision section must state WHY, not only WHAT.
- Mark a decision `(locked)` only when the user explicitly states it is not to be revisited.
- Read the actual codebase before writing; architecture claims must match implementation.
- State the full target path (`<project-root>/PROJECT.md`) before writing.
- Never assume architecture that is not verifiable from code, comments, or the user — ask.
- Depth is measured by substance, not length: every non-trivial decision carries its
  rationale, every invariant its consequence, every known AI-failure-mode its
  correction. Hit that bar first; length follows from it. A thin file that lists
  decisions without rationale fails the bar even at 80 lines.
- Length is a ceiling, never a target: stay under 300 lines, never exceed 500 — AI
  assistants largely stop processing past 500. If real substance pushes past 500,
  split into domain sub-docs (`ARCHITECTURE.md`, `DATA_MODEL.md`) referenced from
  PROJECT.md — never drop substance to fit the cap.

## 4§ Decision gate
- No PROJECT.md exists: create mode — follow §5.1.
- PROJECT.md exists: update mode — follow §5.2.
- User asks to document only one area (e.g. "document the data model"): write that
  section; offer to integrate into a full PROJECT.md.
- Existing file exceeds 500 lines: flag to user; offer to split into domain-specific
  sub-docs (`ARCHITECTURE.md`, `DATA_MODEL.md`) cross-referenced from PROJECT.md.

## 5§ Workflow

### 5.1§ Create path
1. Read the project root for orientation: `README.md`, `CLAUDE.md`, manifest files
   (`package.json`, `Cargo.toml`, `pyproject.toml`, or equivalent).
2. Read key source files to identify layers, data flow, non-obvious decisions, and
   constraints — not to summarize code, but to discover what an AI would get wrong.
3. Ask the user for what code cannot reveal:
   - What is explicitly excluded (non-goals)?
   - Which decisions are locked?
   - Any platform, legal, or performance constraints not visible in code?
4. Write PROJECT.md using `assets/project.template.md` as structure. Apply
   the architecture decision pattern (§6.3) to every non-trivial decision.
5. State the full target path before writing.

### 5.2§ Update path
1. Read the existing PROJECT.md in full.
2. Ask the user what changed, or use `!git log --since=<updated-date> --oneline` to
   identify recent commits and read affected files.
3. Identify stale content: architecture that no longer matches the code, missing
   decisions from new features, outdated constraints, locked decisions that were
   unlocked.
4. Integrate updates: revise stale sections, add new architecture subsections,
   preserve locked decisions with their original rationale unless user unlocks them.
5. Treat every recent AI correction or misunderstanding as a signal — if Claude
   got something wrong in a prior session, add a clarification here so it stays
   permanently fixed. PROJECT.md grows through corrections, not upfront speculation.
6. Update the `updated:` frontmatter field to today's date.
7. State the full path before writing.

## 6§ Content guide

### 6.1§ What belongs
- Project goal — the problem solved and for whom; 1-3 sentences, non-redundant with README
- Core features — flat list of what the system actually does; behaviors, not benefits
- Non-goals — what is explicitly excluded; include the reason when it is non-obvious
- Architecture decisions — every decision that is non-obvious or constraining;
  one subsection per decision, always with rationale
- Directory structure — key folders at 2-3 levels deep; state the ROLE of each,
  not its contents; skip obvious folders (`node_modules/`, `dist/`)
- Domain vocabulary — internal terms, type names, or concepts the project uses
  that differ from common usage or that an AI would otherwise name differently
- Data model and persistence — schema, where data lives, invariants, backward-compat rules
- Invariants and gotchas — rules that must hold for the system to stay correct, and
  the non-obvious traps that break it. State each invariant with the consequence of
  violating it; state each gotcha with what to do instead
- AI pitfalls — what an AI assistant gets wrong here and the correction. Every prior
  session where Claude misread the architecture becomes one entry, so the mistake is
  fixed permanently (the update path §5.2 feeds this section)
- Patterns and examples pointer — if the project has canonical example files or
  patterns that Claude should follow, name the paths (e.g. `src/api/users.ts` as
  the reference for all API modules)
- Current work — optional transient section: current goal (one sentence), last
  3-5 completed items with file paths, next immediate action; under 200 words.
  Harness PreCompact hooks block compaction only when PROJECT.md is missing or stale —
  create or refresh this section so a freshly updated PROJECT.md passes the gate
- External interfaces — APIs, IPC protocols, file formats the system consumes or produces
- Build, toolchain, and deployment specifics not already in CLAUDE.md
- Platform and environment constraints
- Performance targets and sizing decisions
- Security model and access constraints

### 6.2§ What does not belong
- Feature documentation for end users — that is README.md
- Code-level implementation details obvious from reading the source
- Step-by-step tutorials or usage guides
- Dependency lists that duplicate package manifests
- Changelog content — that is CHANGELOG.md
- Aspirational plans — what the project might do; only what it does

### 6.3§ Architecture decision pattern
Each non-trivial decision gets its own numbered subsection under
`## N§ Architecture decisions`. Append `(locked)` to the heading when the user
has stated it is not to be revisited.

```text
### N.M§ Decision name

What was decided — one sentence stating the choice made.

Rationale: why this over the alternatives; what constraint or incident drove it.
```

Use subsections liberally — one per discrete decision, not one per topic area.
A decision with no stated rationale provides half its value: an AI can see WHAT
was chosen, but not WHY, so it cannot judge edge cases.

## 7§ Output contract
Must include:
- YAML frontmatter: `name`, `description`, `updated`
- `## 1§ Goal` — one to three sentences, never redundant with README
- `## 2§ Core features` — flat list of actual behaviors
- `## 3§ Non-goals` — flat list with reasons where non-obvious
- `## 4§ Directory structure` — key folders at 2-3 levels, with role annotations
- `## 5§ Architecture decisions` — one numbered subsection per decision, each with rationale
- `## 6§ Constraints` — platform, legal, performance; one bullet per constraint
- Conditional sections when the project warrants them (§6.1): Domain vocabulary,
  Data model, Invariants and gotchas, AI pitfalls — add as their own numbered sections
- Substance bar met (§3): every decision has rationale, every invariant its consequence
- Total length under 300 lines (target); hard limit 500 lines

Must not include:
- User-facing feature documentation
- Content that duplicates README.md verbatim or in summary
- Architecture claims not verifiable from code or user input
- Stale entries not updated or removed

## 8§ Associated documents
- [assets/project.template.md] — structural template for PROJECT.md output
- [assets/project.example.md] — completed example calibrated to a mid-sized project
