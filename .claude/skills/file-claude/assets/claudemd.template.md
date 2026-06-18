# <PROJECT_NAME>
<!-- One-line project name only. No tagline or description. -->

## 1§ Commands
<!-- Exact, runnable commands — copy-paste must work.
Include timing estimate for commands over 30 s. Omit section if no build system. -->
- `<test-command>` — <purpose and timing if slow>
- `<build-command>` — <output location and when to run>
- `<lint-command>` — <what it checks; include auto-fix variant if available>

## 2§ Architecture
<!-- Layer boundaries and directory roles Claude cannot infer from filenames.
Include access rules (e.g. "only callers of X"). Omit obvious directories. -->
- `<dir>/` — <role and access constraint>

## 3§ Code conventions
<!-- Deviations from language or framework defaults only.
Omit this section if the project follows all defaults. -->
- <convention that deviates from default>

## 4§ Workflow
<!-- Branch naming, commit format, PR expectations.
Include only enforced rules — not aspirational guidelines. -->
- <workflow constraint>

## 5§ Gotchas
<!-- Non-obvious failure modes, hidden dependencies, environment requirements.
If it would surprise a new contributor, it belongs here. Omit section if none.
If the project involves creating .claude/ artifacts (rules, skills, hooks, agents,
settings), include the following line: -->
- When creating any new `.claude/` artifact, state the full target path before writing and mark inferred scope `[assumed]` if the user did not specify it.
<!-- Remove all HTML comment blocks before writing the production file. -->

## 6§ Available rules
<!-- One bullet per rule file in .claude/rules/. Add the load trigger in parentheses.
Omit section if the project has no rules directory. -->
Rules in `.claude/rules/` load on demand — read before editing matching files:
- `<rule-name>.md` — <one-line purpose> (load when editing <context>)

## 7§ Available skills
<!-- Remove this section if the project has no .claude/skills/ directory. -->
Skills live in `.claude/skills/`. Before invoking one, read
`.claude/skills/skills.index.toon` — TOON format, first non-comment line is a
header row (`name | description`), one skill per subsequent line. Load the full
`skills/<name>/SKILL.md` only when the skill is needed.
After creating or updating a skill, upsert its entry in `.claude/skills/skills.index.toon`.

## 8§ Available agents
<!-- Remove this section if the project has no .claude/agents/ directory. -->
Agents live in `.claude/agents/`. Each agent has its own subdirectory:
`.claude/agents/<name>/AGENT.md` with an optional `assets/` subfolder.
Before invoking one, read `.claude/agents/agents.index.toon` — TOON format,
same structure as skills index. Load the full `agents/<name>/AGENT.md` only
when the agent is needed.
After creating or updating an agent, upsert its entry in `.claude/agents/agents.index.toon`.

## 9§ Verification
<!-- Commands Claude must run after specific types of changes.
Omit if no automated verification exists. -->
- After <change type>: `<command>` — <success condition>
