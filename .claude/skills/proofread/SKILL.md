---
name: proofread
description: Verify a finished deliverable before it ships — numbers consistent, names and proper nouns right, facts accurate, internally consistent, logically sound. Read-only; returns severity findings.
updated: 2026-06-13
---

# Proofread

## 1§ Purpose
The process schema for proofing a finished deliverable — a report, proposal, slide deck, memo,
or any content destined for a client or external recipient. Verify that the content is correct
and ready: figures, names, facts, consistency, and logic. Read-only: produce findings, never modify.

This checks the result, not the process or the code. Technical quality of source code or harness
artifacts, and security, are out of scope — this skill is content correctness only.

It is loaded by whoever needs it — typically the `ag-cqo` agent as a final deliverable gate, or
the main session for an inline proof.

## 2§ Use when
- A deliverable is finished and about to be sent to a client or published.
- User asks to "proofread", "fact-check", "check the numbers", "final review before sending",
  or "is this ready to go out?".
- Any finished document needs a correctness and consistency pass.

## 3§ Hard constraints
- Read-only. Produce findings; never edit the deliverable.
- Cite an exact location for every finding: page, section, heading, table, or figure.
- Verify against the source when one is available (the data, inputs, or brief the deliverable is
  based on). Read it before judging a figure or claim correct.
- When no source is available: check internal consistency and plausibility, and flag every
  unverifiable figure or claim explicitly rather than passing it silently.
- Never soften a finding. A transposed figure or a wrong client name is a critical defect, not a nitpick.
- Distinguish confirmed errors from suspected ones.

## 4§ Dimensions
Apply all that the deliverable contains.

- P1 Numbers — every figure correct and internally consistent: totals add up, subtotals match the
  total, the same quantity is stated identically everywhere it appears, percentages sum as
  expected, units and currencies correct, dates and amounts not transposed, a number in the text
  matches the number in the table or chart it refers to, cross-references ("see Table 3") point to
  the right object.
- P2 Names and proper nouns — person, company, product, and place names spelled and capitalized
  correctly and consistently throughout; the client's name exactly right everywhere; trademarks per
  `assets/proper-nouns.md`; titles and roles correct.
- P3 Facts — every checkable claim matches its source; quoted figures match the underlying data;
  citations and references resolve; no claim contradicts the provided inputs.
- P4 Internal consistency — no statement contradicts another; terminology used consistently; the
  executive summary matches the body; numbers in text match numbers in tables and charts;
  recommendations match the findings they rest on.
- P5 Logic — conclusions follow from the stated evidence; no non-sequiturs; assumptions are stated;
  no gap where a claim depends on something not shown; recommendations are consistent with the analysis.
- P6 Completeness and language — no leftover placeholders, TODOs, tracked changes, or draft markers;
  every promised section present; spelling and grammar correct; tone and register fit the recipient.

## 5§ Severity levels
- `critical` — would mislead or embarrass the recipient: wrong figures, wrong client or person name,
  a factual error, a self-contradiction, a logical break. Must be fixed before sending.
- `major` — a real error that should be fixed before sending but is unlikely to mislead on its own.
- `minor` — polish: wording, minor inconsistency, formatting.
- `info` — observation; no action required.

## 6§ Workflow
1. Identify the deliverable and, if available, its source (data, brief, prior version). Read both.
2. Apply P1–P6. For every figure and factual claim, trace it to the source or mark it unverifiable.
3. Record each finding: dimension, severity, exact location, what is wrong, the corrected value or
   the fix, and whether it is confirmed or suspected.
4. Group by severity: critical → major → minor → info.
5. Deliver findings. State what was checked, what source was used, and what could not be verified.

## 7§ Output contract
Must include:
- Scope statement: the deliverable checked, the source used (or "no source available"), dimensions applied
- Findings table: dimension | severity | location | issue | correction | confirmed/suspected
- Summary: count per severity; the unverifiable items listed explicitly

Must not include:
- Edits to the deliverable
- Findings without an exact location
- Silent passing of an unverifiable figure or claim

This skill produces findings only. The ship/no-ship stage-gate decision and its format are the
calling agent's reporting standard (see `ag-cqo`), not part of this skill.

## 8§ Associated documents
- [assets/proper-nouns.md] — trademark and product-name capitalization reference for P2.
