---
name: lean-review
description: Universal read-only quality review of any artifact — code, config, docs, or a whole harness — across correctness, simplification, performance, tests, waste, coherence, and style. Findings only.
updated: 2026-06-13
---

# Lean Review

## 1§ Purpose
Evaluate any artifact against the dimension set that
matches its type, at either scope — one file or a whole construct (directory, repo, harness) —
and return severity-classified findings. Read-only: never modifies files.

This is a process schema, not a role. It is loaded by whoever needs it:
- `ag-cto` loads it to self-review its own diff before declaring done.
- `ag-cqo` loads it to sweep a whole harness in isolation.
- `ag-cso` loads it as the internal pass before external benchmarking.
- The main session loads it for inline review of a file, diff, or PR.

Scope boundary: security exploitability (injection, OWASP, CVEs) is a different, adversarial
lens and is out of scope here — note any such issue and flag that a dedicated security review
is needed, but do not analyze it. This skill covers correctness, quality, waste, coherence,
and convention — not exploitability.

## 2§ Use when
- User asks for a code review, file review, diff review, or PR feedback.
- User asks to audit, prune, or simplify a file, config, or whole harness.
- User asks "is this correct?", "can this be simplified?", "what can go?", "is this consistent?".
- An agent must self-review produced output before reporting completion.
- Pre-merge or pre-release sign-off on any artifact.

Do not use for security-specific analysis (injection, OWASP, CVEs) — that adversarial lens is out of scope.

## 3§ Hard constraints
- Never modify files. Analysis only. All fixes go through the calling session or agent.
- Report specific locations: file path + section or line. No general impressions.
- Read every cross-referenced file before declaring something unused, missing, or redundant.
- Severity reflects actual impact: `critical` is broken correctness or broken loading, not style.
- Never soften a finding — report what is found regardless of effort invested in it.
- If a security-specific vulnerability surfaces, note it and flag that a dedicated security
  review is needed; do not attempt full security analysis here.

## 4§ Scope selection
1. Single file or diff: apply the dimension set matching the artifact type (5.1§ or 5.2§).
2. Whole construct (directory, repo, harness): apply the matching per-file set to each file,
   then additionally apply the cross-file dimensions (5.3§).

A source file gets the code dimensions; a Markdown/config/prose/harness file gets the
artifact dimensions. A mixed scope gets both, per file.

## 5§ Dimension sets

### 5.1§ Source code — C-dimensions
Apply in order C1→C6. A critical finding does not stop later dimensions — complete all.

- C1 Correctness — wrong output or crash under realistic input: off-by-one, null/undefined
  dereference, unchecked returns, incorrect conditionals, race conditions, unhandled
  promise rejections, misuse of async/await.
- C2 Error handling — empty catch blocks, over-broad catches hiding bugs, missing
  propagation, silent recovery from programmer errors (not transient failures).
- C3 Simplification — duplicated logic, nesting deeper than 3 levels, functions doing more
  than one thing, unused variables/imports, premature abstraction.
- C4 Architecture — coupling to concretes where interfaces exist, dependency-direction
  violations, bypassing established patterns, public API design (naming, parameter order,
  return types).
- C5 Performance — only obvious, high-impact issues: N+1 queries, unbounded memory
  accumulation, O(n²) over large realistic input where O(n log n)/O(n) exists, blocking I/O
  in hot async paths, expensive repeated work invariant across a loop. Omit micro-optimizations.
- C6 Tests — for non-trivial code only: new public functions with no test, trivially-true
  assertions, missing edge cases (null, empty, boundary, error paths), tests that duplicate
  the implementation rather than specify behavior.

### 5.2§ Documents, config, prose, harness artifacts — A-dimensions
Apply all that are relevant to the artifact.

- A1 Necessity — the remove test. If deleted, would the rest stay correct and actionable?
  If yes: waste. Token cost must be justified by value. Apply first.
- A2 Token efficiency — information-per-token. For LLM-facing content target >70%
  instructional density; flag filler, synonym variation, examples restating a rule.
- A3 Clarity and usability — for human-facing content: dense paragraphs, nesting beyond one
  level, unclear order, sentences >20 words. For LLM instructions: narrative prose,
  conversational explainers, justification text that belongs in commit messages.
- A4 Coherence and references — broken cross-references, dead links, a section that
  contradicts another, a mandatory rule (`must`/`never`/`always`) violated by an example in
  the same file, a summary claiming N items where the body has a different count,
  scope in §1 not matching what §2 covers, non-consecutive or duplicate section numbers,
  truncated content (empty heading body, paragraph ending mid-sentence).
- A5 Lean and structure — purposes conflated in one document (reference mixed with tutorial),
  step counts higher than necessary, files that could merge without loss, over-engineering
  with no proportional benefit.
- A6 Convention and style — for harness Markdown apply `md-style.md`: no bold/italic/
  strikethrough/blockquote, no horizontal rule in body, every code block has a language id,
  `N§` section numbering, `N§` cross-reference form only, `[path/to/file.md]` internal links,
  `name:` first and `updated:` last in frontmatter, no comments/unfilled `<PLACEHOLDER>` in
  production files. This is structural style only — content correctness of a finished
  deliverable (figures, names, facts, logic) is out of scope for this dimension.

### 5.3§ Whole-construct — X-dimensions
Apply only at construct scope, after per-file analysis.

- X1 Coverage and registry parity — every entry in a catalog or index resolves to an existing
  item, and every item that should be catalogued is; no orphaned (unreferenced) or unreachable
  elements. Report what is dropped, never silently.
- X2 Cross-file consistency — no two files contradict each other on a shared convention; a
  referenced identifier, function, or file actually exists (Grep/Glob to confirm before asserting
  absence); a summary count matches the body.
- X3 Claude Code harness wiring — when the construct is a `.claude/` harness, additionally verify:
  every entry in `skills.index.toon`, `agents.index.toon`, and `rules.index.toon` resolves to an
  existing file, and every such file has a matching index entry; each index `description` equals the
  artifact's frontmatter `description` verbatim (≤200 chars); each mapping column resolves (skills
  index `agents` → real agents, agents index `skills` → real skills); every on-demand rule (not
  `alwaysApply: true`) appears in the CLAUDE.md routing table; every registered hook in
  `settings.json` references an existing companion script. Deep per-artifact structural conformance
  (exact frontmatter fields, section template, field bans, glob validity) is owned by each
  artifact's own authoring skill, not this dimension.

## 6§ Severity levels
- `critical` — broken correctness, data loss, incorrect output on common input, or a
  structural defect that breaks Claude Code loading or invocation.
- `major` — significant logic, quality, or coverage gap that degrades reliability or output.
- `minor` — improvement available; not a reliability risk; style non-compliance.
- `info` — observation worth noting; no action required.

## 7§ Workflow
1. Resolve scope: a file, a diff (`!git diff HEAD`), a PR range (`!git diff main...HEAD`),
   or a construct (directory/area). If ambiguous and uninferable, ask before reading.
2. Read all files in scope. For callers, related types, or cross-references, read those too
   before making any finding about a contract, usage, or redundancy.
3. Select dimension sets per 4§. Apply systematically. Record each finding: dimension,
   severity, location, description, recommended action.
4. At construct scope, apply 5.3§ after the per-file pass.
5. Group by severity: critical → major → minor → info.
6. Deliver inline. State scope covered, count per severity, the single highest-priority action.

This skill produces findings and severities only — the analytical process. How the result is
reported (a verdict, a gate decision, a formatted block) is the caller's reporting standard,
not part of this skill. An agent that needs a sign-off renders its own verdict from these
severities.

## 8§ Output contract
Must include:
- Scope statement (files and dimension sets covered)
- Findings table: dimension | severity | location | description | recommendation
- Summary: count per severity, top recommended action

May include:
- One "Positive findings" line noting genuinely well-built parts, to calibrate the review

Must not include:
- File modifications or patches
- Findings without a specific location
- `critical` severity for style or preference issues
- Security-specific findings — out of this skill's scope

## 9§ Associated documents
- [assets/lean-review.template.toon] — TOON output template; fill and write when a persistent
  findings file is requested.
