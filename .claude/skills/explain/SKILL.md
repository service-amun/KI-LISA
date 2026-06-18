---
name: explain
description: Explain any topic at the right depth — simple (plain language, one analogy) or deep (mechanisms, trade-offs, design decisions). Depth inferred from context or stated explicitly.
updated: 2026-06-11
---

# Explain

## 1§ Purpose
Deliver targeted explanations calibrated to the audience's knowledge level and the
question's depth signal. Two modes: `simple` (accessible, one core idea, one analogy)
and `deep` (mechanisms, internal structure, trade-offs, limitations). The mode is
inferred automatically or stated explicitly.

## 2§ Use when
- User asks "what is X", "how does X work", "explain X", or "why does X...".
- User requests a specific depth: "ELI5", "plain English", "simple", "deep dive",
  "technical explanation", "trade-offs".
- A topic needs to be explained to a mixed or unknown audience.
- User says "explain" without further qualification.

## 3§ Hard constraints
- Never deliver simple mode when the question signals technical depth — and vice versa.
- Never omit the core mechanism in either mode.
- In simple mode: use at most one analogy; stick to it; never switch to another.
- In simple mode: never infantilize or personify abstract concepts. The audience is
  an adult unfamiliar with the domain — simplified means domain-accessible, not
  childlike. No nursery metaphors, no humanizing of abstractions, no "imagine X is
  a little person who...". Use neutral, concrete analogies from adjacent domains.
- In deep mode: state prerequisites upfront; do not assume knowledge that was not
  signalled in the question.
- In deep mode: always include project context implications — how the concept's
  behavior, trade-offs, or limitations concretely affect the current project.
- Never invent technical details not supported by actual knowledge of the topic.
- Always offer the other depth level at the end of the response.

## 4§ Depth modes

### 4.1§ Simple
For lay audiences, executives, or anyone who signals plain-language intent.

Structure: core idea (1–2 sentences) → one neutral analogy (optional) →
one example → why it matters → offer deep alternative.

Target: readable in under 30 seconds. Max 2–3 new terms, each immediately defined.
Omit: trade-offs, edge cases, historical context, implementation detail.

Tone: clear and direct for adults — not simplified to the point of condescension.
Concrete comparisons from adjacent domains are welcome; personification and nursery-
style metaphors are not.

### 4.2§ Deep
For practitioners, implementers, or anyone who signals technical intent.

Structure: prerequisites → overview → how it works (mechanisms, 3–5 steps) →
design decisions and trade-offs → concrete example → where it breaks down →
project context implications → optional further depth pointer.

Target: complete enough that a practitioner can act on it. No jargon without
definition; precision over brevity.

Project context implications: always state how the explained concept specifically
affects the current project — which decisions it constrains, which risks it
introduces, or which patterns it enables. Generic explanations without project
anchoring are incomplete in deep mode.

## 5§ Context detection
Determine depth from the question before generating output.

Signals for simple mode:
- Lay vocabulary; no domain jargon.
- Question starts with "what is", "explain", "can you describe".
- Explicit markers: "ELI5", "simple", "plain English", "non-technical", "for a
  non-developer", "quick overview".
- Question has no follow-up technical qualifier.

Signals for deep mode:
- Question uses domain jargon correctly.
- Question asks "how does it work internally", "why does it fail", "what are the
  trade-offs", "how is it implemented", "how does it compare to X".
- Explicit markers: "deep dive", "technical", "internals", "edge cases", "details".
- Question is from a stated practitioner context.

When signals are mixed or absent: deliver a top-down executive summary (2–3
sentences) and explicitly offer both modes: "Want the simple version or the
technical deep dive?"

Bloom's level heuristic — map the question's action verb:
- "What is / Explain" → simple (Understand).
- "How would I use" → simple + worked example (Apply).
- "Why does / How does it work" → deep (Analyze).
- "What are the trade-offs / Is X better than Y" → deep (Evaluate).
- "Design / What if we" → deep (Create).

## 6§ Explanation patterns

### 6.1§ Analogy rules
Use one analogy that covers the core mechanism, not just surface features. After
the analogy, state explicitly where it breaks down — incomplete mental models are
worse than no analogy. Avoid analogies when the concept has no stable equivalent
in common experience (prefer first principles instead).

### 6.2§ Structure direction
- Top-down (overview first, then detail): use for simple mode and management contexts.
- Bottom-up (primitives first, then assembly): use for deep mode and implementer contexts.

### 6.3§ Chunking
Each chunk: one concept. Do not combine mechanism + trade-offs + example in the
same paragraph. In deep mode: conceptual → mechanism → example → limits.

## 7§ Workflow
1. Parse the question for depth signals (§5). Identify Bloom's level from the
   action verb. If ambiguous, state it and offer both modes.
2. Identify what the person already knows from vocabulary and context — anchor the
   explanation one level above that, not from zero.
3. Select mode (simple or deep) and structure direction (§6.2).
4. In simple mode: draft core idea → choose one analogy → pick one example → state
   why it matters.
5. In deep mode: state prerequisites → write overview → break mechanism into 3–5
   steps → add trade-offs → write a concrete example → state where it breaks down.
6. Append a one-line offer of the other depth level.
7. Format the output following the in-chat template (§9). The templates define the
   chat output structure — output is written inline in the conversation, not to a file.

## 8§ Output contract
Must include:
- Core mechanism — present in both modes, never omitted
- Depth signal acknowledged (explicit or inferred) — state which mode is being used
- Offer of the other depth level at the end
- In deep mode: prerequisites stated upfront; trade-offs and at least one limitation

Must not include:
- Invented technical details
- Multiple analogies for the same concept in simple mode
- Jargon without definition in simple mode
- Assumed prior knowledge not signalled by the question in deep mode

## 9§ Associated documents
In-chat format templates — these define the structure Claude writes directly in the
conversation, not file artifacts:
- [assets/explain-simple.template.md] — simple mode format.
- [assets/explain-deep.template.md] — deep mode format with project context section.
