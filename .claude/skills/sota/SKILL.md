---
name: sota
description: Grounded, cross-verified web research against the current state of the art; refresh a stale artifact to the current standard or report an external assessment, as the context requires.
updated: 2026-06-13
---

# SOTA

## 1§ Purpose
One process: research the current state of the art for a subject — grounded in freshly fetched
sources — and resolve by context. When invoked by the CLAUDE.md staleness checks for an artifact
past its 30-day window, it refreshes that artifact to the confirmed current standard. When invoked
directly or by `ag-cso` for a project, it reports an external best-practice assessment. Same research
discipline either way; the output adapts to what was passed in.

## 2§ Use when
- A rule, skill, or agent is past its 30-day staleness check and must be verified against current sources.
- A user asks to compare a project against the current state of the art, best practice, or the market.
- Before adopting a new approach, to confirm it is actually current and not already superseded.

## 3§ Hard constraints
- Ground every claim in freshly fetched content — never from training memory. A finding without a
  fetched source is not a finding.
- Cross-verify each material claim against at least two authoritative sources before acting on it.
- Extract concrete facts verbatim — versions, dates, thresholds, deprecations — not paraphrase.
- Default to "no change / inconclusive" when sources do not confirm a change. Selective adoption:
  act only on confirmed, material, broadly-current changes; never chase novelty.
- Read the subject (the artifact or project) before researching; never recommend what it already
  does or explicitly rejected.
- Read-only by default. The single write exception: when invoked to refresh a specific artifact,
  edit that artifact and nothing else.
- On a failed fetch, record "check failed — verify manually"; never update content or set a fresh
  date on what was not actually verified.

## 4§ Process
1. Frame the subject: read the artifact or project; extract what it asserts about the current
   standard, its stated goals, and explicit non-goals.
2. Derive 3–5 specific research questions from what the subject actually does — never generic (6§).
3. Research each: WebSearch for authoritative sources, WebFetch at least two; extract concrete
   current facts with their URLs; discard anything not grounded in fetched content.
4. Compare the subject against the fetched standard. Keep only confirmed gaps or changes that are
   material, aligned with the subject's goals, and actionable without a redesign.
5. Resolve by context:
   - Refreshing an artifact: apply the confirmed changes to that file and set `updated:` to today.
     If nothing changed, record "verified — no change" and still set `updated:` to today.
   - Assessing a project: score with the 5§ rubric and report gaps, opportunities, and competitive
     edge; change no files.
6. Report: the subject, sources used (URL → the question each answered), what changed or was
   confirmed, and anything left inconclusive.

## 5§ Scoring rubric
When assessing a project, score each dimension with these anchors — apply strictly, never inflate:

| Score | Meaning |
|---|---|
| 0-2 | Absent or fundamentally broken |
| 3-4 | Present but with significant gaps |
| 5-6 | Functional but below mature-project standards |
| 7 | Solid with minor gaps; a practitioner would accept it |
| 8 | Fully functional; improvements are minor |
| 9 | Near-optimal; further improvements are marginal |
| 10 | Reference-class; exemplary |

Dimensions: capability completeness; edge and differentiation; currency; forward compatibility;
usability and onboarding.

## 6§ Research question templates
Replace brackets with specifics from the subject.
- Currency: "What is the current authoritative standard for [domain], and has [version/threshold the subject assumes] changed?"
- Capability gap: "What do mature [project type] projects include that [project] does not?"
- Evolution: "How has best practice for [technique used here] changed recently, and what is now deprecated?"
- Edge: "What do the most effective [domain] configurations do that is not yet common?"

## 7§ Gotchas
- Updating from memory instead of fetched sources — the most common failure; always fetch first.
- Acting on a single source — a claim needs cross-verification before it changes anything.
- Chasing novelty — a new approach is not yet a standard; adopt only what is broadly current.
- Widening an artifact's scope during a refresh — change only what the sources confirm, nothing else.
- Setting a fresh `updated:` date after a failed or skipped fetch — only date what was verified.

## 8§ Output contract
Must include:
- The subject and how it was resolved (artifact refreshed, or project assessed)
- Sources: each fetched URL mapped to the question it answered
- For a refresh: what changed (or "verified — no change"), with the source per change
- For an assessment: a score per dimension with a calibration-anchored justification, plus gaps,
  opportunities, and competitive edge
- Anything inconclusive, stated explicitly

Must not include:
- Any claim not grounded in a fetched source
- A change not confirmed by at least two sources
- File edits beyond the single artifact a refresh was invoked on
