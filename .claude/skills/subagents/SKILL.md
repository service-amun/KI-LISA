---
name: subagents
description: Create or update Claude Code subagent files — frontmatter and system prompt for isolated specialist agents with constrained tools and custom roles. Flat-file or index-loaded layouts.
updated: 2026-06-14
---

# Subagent Create

## 1§ Purpose
Produce `.md` subagent definition files for Claude Code. Each file contains YAML
frontmatter (name, tools, model, etc.) and a markdown system prompt. Subagents run
in isolated context windows with their own tool access and permissions.

## 2§ Use when
- User wants a reusable specialist agent (reviewer, debugger, formatter, etc.).
- User wants tool isolation — limit what Claude can do within a specific task.
- User wants an agent that is delegated to automatically or invoked by name.
- User wants to audit or verify an existing subagent against these conventions (frontmatter fields, the banned `skills:` field, the tool allowlist, a role-only body).
- User says "create an agent", "subagent", "specialized agent", or describes a
  recurring role they want Claude to fill.

## 3§ Hard constraints
- `name` must be unique within its scope; lowercase, hyphens only.
- `description` drives automatic delegation — write it as a precise task-matching phrase.
- Never include unfilled placeholders in a delivered file.
- Never add `Agent` to `tools` — subagents cannot spawn other subagents.
- Do not include `AskUserQuestion`, `EnterPlanMode`, or `ScheduleWakeup` in `tools`.
- Do not invent frontmatter fields — use only documented fields (§5). The harness
  `updated:` convention is the single sanctioned addition.
- Never use the `skills:` frontmatter field. It preloads the named skills' full content
  into the agent's context at startup, defeating on-demand loading and bloating every
  invocation. Name the skills the agent may load in the body (role and workflow) instead;
  the agent reads each `SKILL.md` only when it needs it. The agent's skill set is recorded
  in the `agents.index.toon` `skills` column (a catalog, not a preload).
- Every system prompt body must include an explicit output format section (see §7).
  This section specifies the exact fields, their order, and format type. Without it,
  the agent's output is non-reproducible and cannot be compared across runs.
- Hooks defined in subagent frontmatter fire only while that subagent is active;
  for session-level lifecycle automation, use a separate hook artifact.
- Plugin subagents ignore `hooks`, `mcpServers`, and `permissionMode` frontmatter
  fields — note this if writing for plugin distribution.

## 4§ Decision gate
- Reusable workflow steps or advisory guidance → a reusable skill.
- Behavioral or style guidance → a rule.
- Permission rules or model config → settings.json configuration.
- Session-level lifecycle automation → a lifecycle hook.

Subagent and skill are complementary, not alternatives — they sit on different axes
and compose:
- A skill is a process schema (the "how"): reusable procedural knowledge, no own tools,
  loadable by the main session or by any agent.
- A subagent is a role (the "who/where"): its own context window, tool allowlist, and
  persona. It composes skills — it loads them rather than re-encoding their knowledge.

Build a subagent when isolation, tool restriction, or automatic delegation matters.
Make its procedural knowledge a skill it loads on demand from the workflow body (never via
the `skills:` frontmatter field — that preloads content into context), so the same knowledge
stays usable inline and by other agents. Never copy a skill's content into an agent body —
that forks the knowledge. A role that would
only wrap a single skill with no isolation, tools, or persona benefit does not need to be
an agent; invoke the skill directly instead.

## 5§ Frontmatter reference

| Field | Required | Purpose |
|---|---|---|
| `name` | Yes | Unique identifier; lowercase, hyphens; appears as `agent_type` in hooks |
| `description` | Yes | Routing signal for automatic delegation; copied verbatim to `agents.index.toon`. Max 200 characters, one compound sentence. |
| `tools` | No | Comma-separated allowlist; omit to inherit all parent tools |
| `disallowedTools` | No | Comma-separated denylist; applied before `tools` |
| `model` | No | `sonnet`, `opus`, `haiku`, `fable`, or full model ID; default `inherit` |
| `permissionMode` | No | `default`, `acceptEdits`, `auto`, `bypassPermissions`, `plan` |
| `isolation` | No | `worktree` — runs in isolated git worktree, auto-cleaned if unchanged |
| `skills` | Never | Banned in this harness — preloads the named skills' full content into context at startup. Reference skills in the body for on-demand loading; record the set in the agents index `skills` column. |
| `memory` | No | Memory scope: `project` (`.claude/agent-memory/<name>/`, tracked by git), `user` (`~/.claude/agent-memory/<name>/`, cross-project), `local` (`.claude/agent-memory-local/<name>/`, git-ignored). Harness default: `project`. Omit only when the agent has no value from persistent context. |
| `updated` | Harness | Last-revision date (`YYYY-MM-DD`); harness convention, always the last field |

Additional fields exist (`mcpServers`, `hooks`, `maxTurns`, `background`,
`effort`, `color`, `initialPrompt`) — use when the user requests them; otherwise omit.

## 6§ Tool access
Apply least-privilege: grant only what the subagent's role requires.

| Role type | Recommended `tools` value |
|---|---|
| Read-only analysis | `Read, Grep, Glob` |
| Code modification | `Read, Edit, Write, Grep, Glob` |
| Command execution | `Read, Bash, Grep, Glob` |
| Full access | (omit `tools` field) |

`disallowedTools` removes specific tools from the inherited set without listing all
others — use when one tool is too risky and the rest are acceptable.

Always blocked regardless of `tools`: `Agent`, `AskUserQuestion`, `EnterPlanMode`,
`ExitPlanMode` (unless `permissionMode: plan`), `ScheduleWakeup`.

## 7§ System prompt
The markdown body after the frontmatter `---` becomes the subagent's complete system
prompt. Subagents do not receive the main Claude Code base system prompt — they receive
only the body plus basic environment details (working directory, etc.).

CLAUDE.md files load into subagent context (built-in Explore and Plan agents skip
CLAUDE.md for speed; custom subagents load it normally).

Required body structure (all four sections are mandatory):
- Role and persona — one and the same (see 7.2§): one sentence naming the agent's executive
  office and what it owns, written in that voice. Its depth is set by the agent type per 7.3§ —
  Minimal for accuracy-critical agents, more voice only when the task is alignment- or style-dominant.
- Hard constraints — what the subagent must never do; file access rules; scope limits.
- Workflow — numbered steps for what to do when invoked.
- Output format — the exact structure of the agent's response (see below).

Keep the body focused. Dilute instructions reduce output quality.

### 7.1§ Output format section (mandatory)

Every agent body must include an output format section that specifies:
- The exact fields or sections the output contains, in order
- The format type per field: table, structured text, plain line, code block
- What to omit (no preamble, no trailing summary, no softening language)
- Any field-level constraints (cap, ordering rule, required vs. optional)

The format must be reproducible: two separate runs on the same input should produce
the same structure, even if findings differ.

Token efficiency requirements:
- Prefer tables over prose for structured data
- Use short, consistent labels: `[CRITICAL]`, `Score:`, `Next:` — not full sentences
- No field restates another field
- Omit optional fields entirely when empty (do not write "None" unless the spec requires it)

Format types by agent category — adapt as needed:

| Agent category | Recommended format type |
|---|---|
| Audit / quality check | Structured text: label: value per line; findings as `[SEVERITY] location: text` |
| Scored evaluation | Score table (dimensions × columns) + findings blocks per low-score dimension |
| Compliance / legal | Numbered section report with tables per finding cluster |
| Data extraction | TOON or table — never prose |
| Advisory / optimization | Structured report: context → scores → findings → opportunities → actions |

### 7.2§ Executive persona (mandatory)
Every harness agent is an executive officer on a leadership team that the main session (the CEO)
orchestrates. Persona and role are the same thing — never write them as separate or optional
layers. The agent's Role section IS its persona: name the office in the first sentence and write
the whole role in that voice — ownership, gate authority, accountability.

Name the agent after its office: the `ag-` namespace prefix plus the C-suite abbreviation. Map the
office to the agent's actual function:
- Build, implementation, engineering → `ag-cto` (Chief Technology Officer)
- Audit, quality, risk, compliance, release gate → `ag-cqo` (Chief Quality Officer)
- Outward strategy, benchmarking, competitive positioning → `ag-cso` (Chief Strategy Officer)
- Other domains → the closest office (e.g. CFO, CISO, COO, CMO). If no office fits cleanly, that is
  a signal the role is genuinely distinct — raise it with the user rather than forcing a title.

The office name and the `description` drive routing. The persona sets tone, ownership, and
authority; the process still lives in skills, and the output contract still governs the result.

### 7.3§ Persona depth by agent type (auto-classify)
Persona length is a trade-off, not a free dial: a persona prefix aids tone, alignment, and
open-ended generation but damages factual and coding accuracy, and the damage grows with length
(MMLU 71.6% no persona → 68.0% minimal → 66.3% long). So the correct depth depends on what the
agent's dominant task rewards. Detect the agent's task nature first, then set depth from the table —
do not default to a fixed depth.

Classify by the agent's dominant task nature (from its `description` and workflow):

| Dominant task nature | Signals / examples | Persona depth |
|---|---|---|
| Accuracy-critical — knowledge, deterministic, verifiable | audit, security, compliance, code writing and review, data extraction, classification, fact-check, math, proofread | Minimal — the one-sentence office only, no added voice. Persona measurably lowers accuracy here |
| Mixed execution — reasoning, orchestration, judgment | general task runner, refactor-and-verify, multi-step reasoning, extraction needing interpretation | Standard — office line plus one short ownership/voice clause; stop there |
| Alignment- or style-dominant — open-ended, tone, persuasion | safety/refusal monitor, brand-voice or comms, creative/roleplay, persuasion, tone-heavy user-facing advisory | Expressive — office line plus a short stance/voice paragraph; a fuller persona measurably improves alignment and tone here (e.g. +17.7% vs +8.9% refusal for a longer safety persona) |

Rules for the classification:
- Spans rows → pick the SHALLOWER depth. Accuracy damage is the costlier error, so a mixed
  audit-plus-advisory agent is treated as accuracy-critical (Minimal).
- Invariant at every tier: the elaboration a higher tier permits is role, stance, and VOICE
  (what the agent prioritizes and how it should sound) — never fictional backstory, demographics,
  age, or "N years of experience" framing. Those add tokens and accuracy risk with zero benefit
  at any depth.
- Most harness agents are accuracy-critical (audit, code, grounded research) → Minimal. Only a
  genuinely alignment- or style-dominant role earns Expressive. When unsure between two tiers, cut.
- Depth governs only the persona layer. The skill's process and the output contract are unchanged
  by tier — they, not the persona, produce correct results.

## 8§ Workflow
1. Apply decision gate — confirm a subagent is the right artifact.
2. Determine scope: `.claude/agents/` (project, team-shared via git) or
   `~/.claude/agents/` (personal, all projects). Label `[assumed]` when defaulting.
   File layout: a minimal agent with no assets is a single file
   (`<scope>/agents/<name>.md`); an agent that bundles assets uses the subdirectory
   convention (`<scope>/agents/<name>/AGENT.md` + `assets/`). Both layouts require an
   upsert in `<scope>/agents/agents.index.toon` after create or update — in this harness
   the index is the catalog regardless of native auto-discovery. Prefer the single-file
   layout; only create a subdirectory when the agent genuinely needs its own assets, and
   first check whether that material belongs in a skill the agent orchestrates instead.
3. Select model (`inherit` unless the role clearly benefits from a specific tier).
4. Select memory scope — default `project` unless there is a clear reason to differ:
   - `project` — learnings are project-bound and git-tracked; good for most agents.
   - `user` — learnings carry across all projects; for general-purpose agents.
   - `local` — git-ignored; for agents with sensitive or machine-specific context.
   - omit — only when the agent has no value from persistent learned context.
5. Select tools — apply least-privilege patterns from §6.
6. Write `name` and `description`. Description is the delegation signal — be specific.
7. Classify the agent's dominant task nature and set the persona depth from the 7.3§ table —
   pick the shallower tier when it spans rows. Then write the system prompt body at that depth:
   role/persona, when-invoked context, numbered workflow, output contract.
8. Deliver the complete file with the deployment path.
9. Confirm: state the file path, scope, and a one-line summary of the subagent's role.

## 9§ Agent memory integration
Triggered when the SessionStart hook detects files in an agent memory directory.
Load this skill and run this section before any other work in the session.

1. Identify the agent(s) with memory files from the hook output.
2. For each agent: read its `AGENT.md` system prompt body and all `.md` files in
   its memory directory (`.claude/agent-memory/<name>/` or the scope reported by the hook).
3. Classify each memory item:
   - Stable structural learning — a pattern, constraint, or domain fact the agent
     discovered that applies reliably across sessions → integrate into AGENT.md
   - Interaction pattern — how the user prefers the agent to respond or format output
     in ways not already covered by the system prompt → integrate into AGENT.md
   - Transient context — specific to a past project state, a completed task, or a
     single session → remove from memory; do not integrate
   - Outdated or superseded — contradicts the current AGENT.md or known project state
     → remove from memory; do not integrate
4. Apply the relevance test: "Would the agent make systematically worse decisions next
   session without this in its system prompt?" — discard if no.
5. Integrate surviving items into the agent's AGENT.md body under a
   `## Learned context` section (append if already present, create at the end if not).
   Keep this section under 20 lines — compress, do not enumerate.
6. Remove integrated items from MEMORY.md. Do not delete MEMORY.md itself — it
   continues serving as auto-loaded context for remaining transient items.
7. Report: items integrated (with target section in AGENT.md), items discarded
   (with reason), MEMORY.md lines removed, AGENT.md updated.

## 10§ Output contract

Must include:
- Complete `.md` file with valid frontmatter and non-empty system prompt body
- `memory:` field set to the selected scope (default `project`)
- Output format section in the body (see §7.1) — mandatory, not optional
- Deployment path: single-file `<scope>/agents/<name>.md` (minimal agent) or
  `<scope>/agents/<name>/AGENT.md` + `assets/` (asset-bundling agent); either way an
  `agents.index.toon` upsert (with the `skills` mapping column)
- Scope label, marked `[assumed]` if not specified by user
- One-line summary of role and delegation trigger

Must not include:
- Unfilled placeholders in the delivered file
- Invented frontmatter fields
- `Agent`, `AskUserQuestion`, or `ScheduleWakeup` in `tools`
- Session-level hook logic in frontmatter (use a separate hook artifact)
- Overlong system prompts — body should be readable in under 30 seconds
- Fictional backstory, demographics, age, or "N years of experience" framing in any persona
  (banned at every depth tier), or persona voice exceeding the agent's 7.3§ depth tier — both
  degrade accuracy on knowledge and coding tasks with no offsetting benefit
- Output format described only in prose — use the actual format template or table

## 11§ Associated documents
- [assets/subagent.example.md] — complete example subagent demonstrating key patterns.
