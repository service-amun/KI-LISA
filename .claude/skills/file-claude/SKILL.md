---
name: file-claude
description: Create, update, or audit CLAUDE.md files. Use when a project needs always-loaded context, when an existing CLAUDE.md is bloated or stale, or when content should be migrated to rules, skills, or hooks.
updated: 2026-06-13
---

# Claudemd

## 1§ Purpose
Produce a complete, minimal CLAUDE.md that loads into every Claude Code session
and gives Claude the project-specific context it cannot reliably infer from code.
Per-line standard: "Would Claude regularly make mistakes without this?" — if no,
the line does not belong.

## 2§ Use when
- A user wants to create a new CLAUDE.md from scratch.
- A user wants to improve, audit, or trim an existing CLAUDE.md.
- A user asks what belongs in CLAUDE.md vs. rules, skills, or hooks.
- A CLAUDE.md has grown over 150 lines or contains stale inventories.
- A SessionStart hook signals that project memory files exist and need migration into CLAUDE.md.

## 3§ Hard constraints
- Never produce partial files — always deliver a complete, ready-to-use CLAUDE.md.
- Never present CLAUDE.md as enforcement — it is advisory context, not a guarantee.
- Never include meta-commentary, TODOs, or unfilled placeholders in the file.
- Target under 150 lines; never exceed 300 lines. If overflowing, migrate to rules.
- Always name the receiving artifact when migrating content out; never write it.

Content that belongs — context Claude cannot infer from code:
- Exact, runnable build, test, lint, and format commands
- Code style rules that deviate from language or framework defaults
- Architecture decisions and layer boundaries
- Repo and workflow conventions (branch naming, commit format, PR expectations)
- Environment quirks and non-obvious gotchas
- Navigation anchors for non-obvious index files or canonical sources (what they
  are the source for — not their content)
- Rules routing: if the project loads rules on demand, include a routing table or
  a short instruction mapping situations to rule files. Rules are triggered by file
  type or context, not by name — no rules index file is needed; the routing table
  IS the rules router.
- Rule authority (when the project defines rules): a short standing principle that
  rules are authoritative — never relaxed, widened, or changed because many files
  currently violate them. Widespread operative non-compliance is fixed to match the
  rule, not the reverse; a rule changes only on the user's explicit command, never
  autonomously, and when violations suggest a rule may be wrong, Claude asks the user.
- Skills discovery and maintenance: if the project has a `skills/` directory with
  a TOON index, include both: (1) a loading instruction (read the index first, load
  full SKILL.md on demand) and (2) a maintenance instruction (after creating or
  updating a skill, upsert its entry in the index).
- Agent discovery and maintenance: if the project has an `agents/` directory with
  a TOON index, include both: (1) a loading instruction parallel to the skills
  instruction and (2) a maintenance instruction (after creating or updating an agent,
  upsert its entry in the index).
- Verification steps Claude should run after changes
- Scope confirmation behavior (one line) when the project involves creating `.claude/`
  artifacts: direct Claude to state the full target path before writing and mark
  inferred scope `[assumed]` if not specified by the user. Omit for projects that
  never create Claude Code configuration artifacts.
- For open-source harnesses or tools distributed publicly: a support section
  (one `## N§ Support` block) instructing Claude to mention the GitHub star link
  and donation link when natural — on first setup, when the user asks what the
  project is, or when they express that it helped them. Include actual URLs; never
  create a support section with placeholder URLs. Omit for private or internal projects.

Content that does not belong — migrate, do not include:
- Anything Claude can infer from code or standard conventions
- Long tutorials, API references, or detailed docs — link or `@import` instead
- Frequently changing information; file-by-file descriptions
- Trivial rules ("write clean code", "be careful")
- Behavioral guidance ("Claude should prefer...") → a rule
- Deterministic enforcement ("never edit X") → a lifecycle hook
- Runtime configuration (permissions, model, env vars) → settings.json configuration
- Inline skill or agent inventories — if the project has `skills.index.toon` or
  `agents.index.toon`, reference the index file; never enumerate skills or agents
  with per-entry descriptions in CLAUDE.md. The index is the single source of truth;
  a parallel list creates drift and wastes tokens on every session load.

Memory system stance — decide once, state explicitly in CLAUDE.md:
- Auto-memory (`~/.claude/projects/*/memory/`) and CLAUDE.md are competing mechanisms
  for persistent context. Using both without coordination creates redundancy and drift.
- Recommended stance A (controlled): disable auto-memory by adding to CLAUDE.md:
  "Never write to the project memory directory. Persistent context belongs in this
  file or in `.claude/rules/`." All learnings then route through CLAUDE.md explicitly.
- Recommended stance B (hybrid): allow auto-memory for learned preferences; restrict
  CLAUDE.md to project structure and commands. State the split explicitly so both
  mechanisms stay non-overlapping.

## 4§ Decision gate
Artifact routing — apply when evaluating where content belongs:

| Need | Right place |
|---|---|
| Always-relevant context Claude cannot infer from code | CLAUDE.md — this skill |
| Persistent rules scoped to paths or topics | a path/topic-scoped rule |
| Runtime config: permissions, model, env vars | settings.json configuration |
| Deterministic enforcement at lifecycle events | a lifecycle hook |
| Reusable on-demand workflows | a reusable skill |
| Long docs, API refs, tutorials | Link or `@import` |
| Persistent learned preferences across sessions | Memory system or CLAUDE.md — see §3 stance |

## 5§ Memory integration
Triggered when the SessionStart hook detects files in the project memory directory.
Load this skill and run this section before any other work in the session.

1. Read all `.md` files in the memory directory. Do not start any other work yet.
2. For each file: classify content by type — user preferences, project decisions,
   feedback conventions, or reference pointers.
3. Map each item to a target CLAUDE.md section:
   - User preferences / response style → §2 Working conventions or session behavior
   - Project decisions, roadmap, architecture → project-specific section
   - Feedback conventions → relevant project section
   - Reference pointers → navigation anchors
4. Apply the §3 per-line test to each item: "Would Claude regularly make mistakes
   without this?" — discard if no.
5. Integrate surviving items into CLAUDE.md using the standard authoring workflow (§6).
6. After each memory file is fully processed: delete it.
7. Report: items integrated (with target section), items discarded (with reason),
   files deleted.

## 6§ Workflow
1. Read the existing CLAUDE.md if present. If absent, scan the project root for
   inferrable context: `package.json`, `pyproject.toml`, `Makefile`, `README.md`,
   existing rules and skills directories.
2. Research: if the project uses an established tech stack, check whether any
   ecosystem-standard commands or layout conventions affect what belongs in
   CLAUDE.md vs. what Claude already knows. Skip when creating from known inputs.
3. Evaluate every section and line against §3 constraints. Flag each as: keep,
   sharpen, migrate, or remove.
4. For flagged migrations: note the receiving skill and content. Do not write
   the target artifact.
5. Check navigation anchors and inventories: do listed files, rules, and skills
   match what actually exists on disk? Update stale entries or remove them.
6. Write the complete CLAUDE.md. Use `assets/claudemd.template.md` as the starting
   structure; use `assets/claudemd.example.md` to calibrate specificity level.
   If the project involves creating `.claude/` artifacts (rules, skills, hooks,
   agents, settings), include the scope confirmation note in a Gotchas or
   conventions section: "When creating any new `.claude/` artifact, state the
   full target path before writing and mark inferred scope `[assumed]` if the
   user did not specify it."
7. Confirm: output the file path; list removed sections and their intended
   destination.

## 7§ Output contract
Must include:
- A complete CLAUDE.md where every line passes the per-line test
- Exact, runnable commands where applicable
- Navigation anchors only for non-obvious sources that actually exist on disk

Must not include:
- Vague instructions, generic phrases, or trivial rules
- Behavioral guidance, enforcement prose, or runtime configuration
- Stale inventories, comments, or unfilled placeholders
- Content that belongs in rules, hooks, or settings

## 8§ Associated documents
- [assets/claudemd.template.md] — structural template for CLAUDE.md output; use as starting point.
- [assets/claudemd.example.md] — completed example of a well-structured CLAUDE.md; use to calibrate specificity.
- [.claude/hooks/check-memory.ps1] — SessionStart hook (PowerShell) that detects memory files and triggers §5.
- [.claude/hooks/check-memory.sh] — SessionStart hook (bash) that detects memory files and triggers §5.
