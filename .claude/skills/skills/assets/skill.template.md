<!-- skill.template.md — Strip ALL HTML comment blocks before writing a production SKILL.md -->
---
name: <SKILL_NAME>
description: <One imperative sentence. Lead with the trigger keywords a user would naturally say.
Include what the skill does AND when to use it. Max 1024 chars.
Example: "Generate X from Y. Use when the user asks to Z or mentions W.">
disable-model-invocation: false  <!-- true = user-invoked via /name only; false = Claude may auto-invoke -->
allowed-tools: <Space-separated list of pre-approved tools, e.g. "Read Write Edit Bash".
Omit field entirely if no pre-approval is needed.>
updated: <YYYY-MM-DD>
---

<!-- Replace the H1 below with the skill's display name in Title Case -->
# <Skill Name>

<!-- Keep SKILL.md under 500 lines. Move reference material to assets/. -->

## 1§ Purpose
<!-- One short paragraph: what this skill produces and why it exists.
Do not describe HOW — that belongs in §5 Workflow. -->
<PURPOSE>

## 2§ Use when
<!-- Bullet list of specific situations that should trigger this skill.
Be concrete — Claude uses this section for fuzzy matching during auto-invocation. -->
- <trigger situation 1>
- <trigger situation 2>

## 3§ Hard constraints
<!-- Non-negotiable rules Claude must follow during execution.
Write each as an "Always..." or "Never..." imperative. -->
- Always <constraint>.
- Never <constraint>.

## 4§ Decision rules
<!-- How to handle ambiguity, scope creep, or missing inputs.
Format: situation → resolution. Keep short. -->
- <Situation>: <resolution>.

## 5§ Workflow
<!-- Numbered imperative steps. Each step begins with an action verb.
If a step references an asset file, name it explicitly.
Include error-handling or fallback steps where relevant. -->
1. <Do first thing.>
2. <Do second thing.>

## 6§ Output contract
<!-- Declare exactly what this skill must produce and what it must not include.
Be specific about file names, formats, and forbidden patterns. -->
Must include:
- <required output>

Must not include:
- <forbidden output>

## 7§ Associated documents
<!-- Links to assets/ files this skill reads or produces.
Omit section entirely if the skill has no associated assets. -->
- [assets/<file.md>] — <one-line purpose>
