---
name: outputstyle
description: Create, update, or audit Claude Code output style files in .claude/output-styles/ — a session-wide communication mode (tone, verbosity, persona, format). One style active per session.
updated: 2026-06-13
---

# Output Styles Create

## 1§ Purpose
Produce complete output style files that Claude Code loads as system prompt additions
to change HOW Claude responds across an entire session.

The three mechanisms compared:
- Output style — session-wide communication mode: tone, depth, persona, format
- Skill — on-demand task workflow: guides WHAT Claude does for a specific request
- Agent — isolated Claude instance with restricted tools: determines WHO handles a task

A session holds exactly one active output style. Changing styles requires `/clear`
or a new session (prompt cache boundary).

Built-in styles (provided by Claude Code — do not recreate):
- `Default` — standard Claude Code software engineer
- `Proactive` — autonomous, minimal confirmation, assumes and executes
- `Explanatory` — inserts teaching insights between coding tasks
- `Learning` — collaborative tutor; asks human to implement, adds `TODO(human)` markers

## 2§ Use when
- A user wants a persistent communication mode beyond the four built-in styles.
- A user asks for "terse mode", "deep detail mode", "creative mode", or any
  session-wide tone or depth preference.
- A user wants to audit or update an existing style file.
- A user is uncertain which mechanism (style / skill / agent / rule) fits their goal.

## 3§ Hard constraints
- Never recreate the four built-in styles — redirect to the built-in instead.
- Never add enforcement logic — output styles are advisory, not enforcement.
- Set `keep-coding-instructions: true` for all styles used during software engineering.
  Set `keep-coding-instructions: false` only for fully non-coding sessions (writing,
  brainstorming, analysis without code). When in doubt, use `true`.
- State the full target path before writing; mark inferred scope `[assumed]`.
- Inform the user: style changes require `/clear` or a new session to take effect.
- Body must not exceed 50 lines — a focused style outperforms a sprawling one.

## 4§ Decision gate
Apply before writing anything:
- Session-wide tone / depth / persona → output style (this skill)
- Specific task workflow or reusable instruction set → a reusable skill
- Isolated context with restricted tools → a subagent
- Guidance scoped to file types or path areas → a path-scoped rule
- Built-in style already covers the need → redirect, do not create a duplicate

## 5§ Workflow

### 5.1§ Create path
1. Clarify intent — what communication mode does the user want?
   - Tone: formal / informal / technical / casual
   - Verbosity: terse / standard / exhaustive
   - Depth: answer-only / reasoned / reference-grade
   - Engineering context: coding-focused (keep-coding-instructions: true) or open-ended (false)
2. Check built-ins — confirm the need is not already met by Explanatory or Learning.
3. Determine scope:
   - User scope (`~/.claude/output-styles/`): cross-project communication preferences
   - Project scope (`.claude/output-styles/`): project-specific personas or domain context
   Mark inferred scope `[assumed]`.
4. Write the file using `assets/style.template.md` as structure.
5. Tell the user how to activate: add `"outputStyle": "<name>"` to `settings.json`
   (value must match the `name:` frontmatter field exactly), or use `/config` → Output style.
   Remind: takes effect after `/clear`.

### 5.2§ Update path
1. Read the existing style file.
2. Identify what needs changing: tone, keep-coding-instructions value, instruction gaps.
3. Update in place; preserve `name:` and `description:` unless the user explicitly changes them.

### 5.3§ Audit path
1. Read all `.md` files in the target `output-styles/` directory.
2. Check each for: valid frontmatter, meaningful body, no built-in duplication,
   keep-coding-instructions set appropriately.
3. Report findings by severity; offer to fix defects inline.

## 6§ Content guide

### 6.1§ keep-coding-instructions semantics
- `true`: retains Claude Code's engineering behavior — scope management, comment
  conventions, verification steps. Use for every style applied during coding sessions.
- `false`: removes all engineering guardrails. Only for fully non-coding sessions.
  Must include a note in the style body reminding the user to switch back before coding.

### 6.2§ Body structure
Write as direct instructions to Claude — not a description of the style. The body
appends to the end of the system prompt.

Effective patterns:
- Open with the primary persona statement ("You are in X mode.")
- Define concrete response conventions: "lead with X", "limit to Y bullets", "never Z"
- Use `##` subsections for distinct behavioral areas (format, depth, tone, prohibitions)
- For structural changes, give a response template or concrete example

Anti-patterns:
- Vague directives ("be more helpful") — no behavioral change
- Contradicting keep-coding-instructions value — creates conflicting instructions
- Duplicating built-in behavior — adds tokens with no benefit
- Body exceeding 50 lines — dilutes focus; split into separate styles

### 6.3§ Scope guidance
User scope (`~/.claude/output-styles/`): generic communication modes that apply
across all projects. This is where the harness pre-built styles live.

Project scope (`.claude/output-styles/`): domain-specific personas that only make
sense for one codebase — "MCP tool documenter", "accessibility reviewer",
"financial-regulation aware responder".

## 7§ Pre-built styles
The harness ships one pre-built style in `.claude/output-styles/`, available after
copying `.claude/`:
- `executive` — bottom-line first, maximum signal density, emoji section headers,
  ✅/❌ bullets, short punchy phrasing; keep-coding-instructions: true

This complements the four built-ins. Do not recreate it.

The harness `.claude/settings.json` pre-sets `"outputStyle": "Executive"` as the
default. Users who copy `.claude/` inherit this; users who copy `~/.claude/` should
add it manually to `~/.claude/settings.json`.

## 8§ Output contract
Must include:
- Valid frontmatter: `name`, `description`, `keep-coding-instructions`
- A body with concrete, actionable behavioral instructions (not vague directives)
- Full target path stated before writing, scope marked `[assumed]` if inferred
- Activation instructions (settings.json field + /config path + /clear reminder)

Must not include:
- Recreations of Default, Proactive, Explanatory, or Learning
- Enforcement logic or assertions
- Body exceeding 50 lines

## 9§ Associated documents
- [assets/style.template.md] — template for new output style files
- [assets/outputstyle.example.md] — example session creating a custom style
- [.claude/output-styles/executive.md] — pre-built: terse, bottom-line mode
