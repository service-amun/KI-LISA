---
name: masterprompt
description: Generate a maximal, comprehensive masterprompt on any topic — research the domain, then build the most complete expert prompt: persona, sub-domains, edge cases, behavioral mandates.
updated: 2026-06-12
---

# Masterprompt

## 1§ Purpose
Generate a comprehensive, maximal masterprompt for any given topic. The output is
a standalone, ultra-detailed prompt that transforms Claude into a deep expert on
that exact subject. No topic is too specific or too abstract — truck driving,
three yellow chickens, quantum mechanics, medieval baking: every topic gets the
same maximum treatment.

A masterprompt is not a summary. It is the densest possible expert briefing:
a prompt so complete that anyone reading it walks away knowing exactly what
questions to ask, what answers to expect, and what a true master of the topic
would know.

## 2§ Use when
- User asks for a masterprompt, mega-prompt, super-prompt, or expert prompt on any topic.
- User wants a comprehensive prompt covering all aspects of a subject.
- User names a topic and wants the most powerful possible prompt for it.

## 3§ Hard constraints
- Always research the topic before writing — never build from memory alone.
- Never truncate or abbreviate the output. Length is a feature, not a flaw.
- Never add meta-commentary, preamble, or explanation outside the prompt itself.
- Never ask the user for clarification — interpret the topic maximally and begin.
- The output IS the prompt. Deliver it ready to paste.

## 4§ Research phase
Before writing a single line of the prompt, research the topic across all
relevant dimensions. For each topic, identify:

- Core domain and sub-domains: what are the main areas of knowledge?
- Expert vocabulary: what terms, jargon, classifications does a master use?
- Practical application: what does this look like in real-world use?
- Edge cases and rare scenarios: what does a novice miss but an expert knows?
- Regulatory, safety, or ethical dimensions: what constraints apply?
- Cultural, historical, or contextual background: what shaped this field?
- Common misconceptions: what do beginners get wrong?
- Hierarchies and systems: how is this domain structured internally?

Use `WebSearch` and `WebFetch` to gather current, specific information.
Research depth should match topic complexity — more layers for professional
domains, less for narrow/playful topics (but even "3 yellow chickens" gets
full creative treatment with breed specifics, behavior, care, lore, etc.).

## 5§ Prompt construction
Build the masterprompt in this structure. All sections are mandatory unless
the topic makes a section genuinely inapplicable.

### 5.1§ Persona block
Open with a richly detailed expert identity. Include:
- Role title and seniority level
- Years and type of experience
- Specific sub-specializations within the domain
- Real-world context (where they work, what they've done)
- Mindset and approach to the subject

### 5.2§ Knowledge domains
Enumerate all major knowledge areas the expert holds. Cover:
- Primary domain knowledge in full depth
- Adjacent domains that intersect
- Technical, theoretical, and practical knowledge
- Tools, instruments, terminology, classifications used

### 5.3§ Behavioral mandates
Define how the expert thinks and communicates:
- How they analyze problems in this domain
- What precision standard they apply
- How they handle uncertainty or conflicting information
- What they refuse to simplify beyond a certain point
- How they distinguish beginner from expert questions

### 5.4§ Domain specifics
The densest section — everything specific to this topic:
- All key sub-topics, each with a sentence of substance
- Standard processes, sequences, or protocols
- Known failure modes, risks, and how to handle them
- Best practices vs. common practice vs. expert shortcuts
- Relevant standards, regulations, certifications, or norms (where applicable)
- Historical development and current state of the field
- Open questions, debates, or unsettled areas in the domain

### 5.5§ Interaction style
Define how the masterprompt persona responds:
- Tone (e.g., direct, technical, patient, authoritative)
- Default detail level
- How they handle vague questions (interpret maximally, ask once if critical)
- Examples: when they use them, at what depth
- What they proactively add beyond what was asked

### 5.6§ Output format defaults
Define what the expert's default output looks like:
- Structure (prose, lists, hierarchies, tables — when to use which)
- Length defaults per question type
- Use of examples, analogies, counter-examples
- Caveats: when included, when omitted

## 6§ Length and density
The masterprompt must be substantial. A minimal topic warrants at minimum one
full page of dense content. A complex professional domain warrants 3–6 pages.
Density over filler: every sentence carries specific, non-obvious information.

Filler phrases that consume tokens without adding knowledge ("it is important to",
"one must consider", "always keep in mind") are forbidden. Replace with the
actual content those phrases were gesturing at.

## 7§ Output contract
The output is the masterprompt itself — nothing else.

Must include:
- All six sections from §5, in order
- Specific, researchable facts woven throughout (not generic expert-speak)
- Expert vocabulary used correctly and in context
- Minimum one full page of content for any topic

Must not include:
- Meta-text explaining what the prompt does
- Preamble ("Here is your masterprompt:")
- Trailing commentary or instructions to the user
- Apologies, caveats about AI limitations, or requests for feedback
- Filler sentences that state no specific fact
