---
name: skills
description: Create new skills or update existing skills from a user need, workflow, or draft instruction. Use when a repeatable task should become a reusable skill with a valid SKILL.md and appropriate assets.
updated: 2026-06-13
---

# Skill Create

## 1§ Purpose
Produce complete, minimal skill packages from a user need, existing workflow,
or draft instruction file. Output is a valid `SKILL.md` and only the assets
that materially improve execution quality.

A skill is a process schema — reusable procedural knowledge (the "how to do X").
It runs in whatever context loads it: the main session, or an agent. Skills and
agents are complementary, not alternatives, and sit on different axes:
- Skill = the "how" (methodology). No own tools, no isolation. Loadable by anyone.
- Agent = the "who/where" (a role with its own tools, context window, and persona).
  An agent composes skills — it loads them rather than re-encoding their knowledge.
Knowledge lives once, in the skill. When an agent needs a procedure, it loads the
skill. Decide the number of skills (distinct process schemas) and the number of
agents (distinct roles) independently. Build the role as a subagent when isolation, tool restriction, or automatic
delegation matters.

## 2§ Use when
- A user wants to create a new skill from scratch.
- A user wants to update, rewrite, or optimize an existing skill.
- A user wants to convert a repeatable workflow or instruction set into a reusable skill.
- A user provides an existing skill file and wants it aligned to the current harness standard.
- A user wants to audit or verify an existing skill against these conventions (frontmatter, index entry, referenced assets exist, no unfilled placeholders).

## 3§ Hard constraints
- Never execute the task the produced skill would perform — only write the skill files.
- Keep a skill self-contained: in the optimal case it does not reference another skill by name.
  Cross-references couple skills and breed the same drift a shared dependency would; if two skills
  overlap enough to need a pointer between them, that is a signal to sharpen the boundary or merge
  them, not to add the reference. A single one-line scope-routing note ("X is out of scope — that is
  the `Y` skill") is the only sanctioned exception, and mutual (two-way) references are never allowed.
- Keep `SKILL.md` under 500 lines; target 300 lines or fewer.
- Move detailed reference material to `assets/`; keep `SKILL.md` lean.
- Write all task instructions in imperative form beginning with a verb.
- The template defines the mandatory `##` sections; do not omit them. Content-rich skills may
  add additional `##` sections for substantial reference material (catalogs, type references,
  decision tables, format specs). Use `###` subsections for secondary content within an existing section.
- Never add files that do not materially improve execution quality.
- Read `assets/skill.template.md` before writing any skill; use it as the structural reference.
- Strip all HTML comment blocks from produced files before writing.
- Always produce `assets/skill.template.md` for any skill whose workflow references a template.
- Produce an example asset (`assets/<topic>.example.<ext>`) for every skill whose
  output benefits from a worked example. Skills fully specified by their templates
  or by an authoritative harness rule may omit it; state the omission reason in
  the delivery summary.
- Never set `disable-model-invocation: true` in produced skills — Claude must be able to invoke
  any skill from context without a slash command.

## 4§ Decision rules
- Scope too broad: reduce to one stable primary function; inform the user.
- Existing skill is inconsistent: preserve useful intent, rewrite structure, resolve conflicts conservatively.
- Details missing: apply conservative defaults for low-impact gaps; keep scope narrow; inform the user.
- Multiple independent capabilities requested: keep the strongest core; inform the user what was excluded.
- Material ambiguity blocks output: inform the user; produce the strongest partial file set possible.

## 5§ Workflow
1. Determine whether the request is a new skill, an update, or a standard-alignment rewrite.
2. Research: if the skill automates a workflow involving an external tool, API, platform, or
   Claude Code feature, search for current documentation or best practices before writing.
   For internal workflow automation, research is optional but recommended when the skill
   touches areas where official guidance exists (e.g., Claude Code hooks, MCP configuration).
3. Extract the core capability, trigger conditions, required inputs, expected outputs, and
   non-negotiable constraints from the available context. Define one clear primary responsibility.
4. Read `assets/skill.template.md` to load the current template structure and field conventions.
5. Write `SKILL.md` following the template structure. Strip all HTML comment blocks before saving.
6. Produce supporting assets: always `assets/skill.template.md` when the workflow references a
   template; an example asset (`assets/<topic>.example.<ext>`) when a worked example improves
   execution quality; additional `assets/` files only when each has a concrete operational purpose.
7. Write `SKILL.md` and all assets to `<scope>/skills/<name>/`. Read `<scope>/skills/skills.index.toon`, upsert an entry
   with `name` (directory name) and `description` (frontmatter description, copied verbatim),
   and write the file back in TOON format: one header row (`name | description`),
   one data row per skill, no trailing newline.
8. Tighten all content: remove filler, repetition, vague guidance, and unused sections.

## 6§ Output contract
Must include:
- `SKILL.md`
- `assets/skill.template.md` when the skill's workflow references a template
- An example asset when a worked example improves execution quality (omission reason otherwise)
- Updated `skills/skills.index.toon` entry

Must not include:
- `disable-model-invocation: true` in produced skills
- Meta-commentary inside produced files
- Empty placeholder sections that add no value
- Redundant rules stated more than once
- Invented capabilities, files, or requirements not present in the source material
- HTML comment blocks (stripped before writing)

## 7§ Associated documents
- [assets/skill.template.md] — master template for all skills produced by this harness.
- [skills/skills.index.toon] — registry of all available skills; updated after every create or update.
