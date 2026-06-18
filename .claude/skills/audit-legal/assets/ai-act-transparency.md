# EU AI Act — Transparency Obligations (Art. 50)
# updated: 2026-06-11
# check-interval-days: 60
# sources:
#   EU AI Act (Art. 50): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
#   AI Act explorer: https://artificialintelligenceact.eu/ai-act-explorer/
# Hinweis: EU-wide. Keine Rechtsberatung.

## Scope
Art. 50 applies to limited-risk AI systems. These are not high-risk but must
still inform users about the AI nature of the interaction or content.

## Obligation 1 — Chatbots and human-facing AI (Art. 50.1)
Applies when: an AI system is intended to interact directly with natural persons.

Obligation: inform the natural person that they are interacting with an AI system,
in a clear and distinguishable manner, at the latest at the beginning of the interaction.

Exception: does not apply when the AI nature is obvious from context or when the
system is used for law enforcement purposes (where disclosure would compromise investigation).

Applies to: chatbots, AI assistants, automated customer service, AI-generated responses
presented as human.

## Obligation 2 — Synthetic content disclosure (Art. 50.2–50.4)
Applies when: an AI system generates or manipulates image, audio, video, or text content.

Obligation: providers and deployers must ensure outputs are marked as AI-generated
in a machine-readable format and, where technically feasible, with visible disclosure
to the recipient.

Exception: content that has undergone minor editing (spell-check, translation aids);
content authorized by a rights holder for legitimate purposes.

Applies to: AI image generators, deepfake tools, AI-written text presented as
human-authored content, voice cloning, AI video synthesis.

## Obligation 3 — Emotion recognition and biometric categorization (Art. 50.5)
Applies when: a system infers emotions or categorizes persons by biometric data.

Obligation: inform natural persons exposed to the system, unless for medical or
safety purposes.

## Compliance checklist for limited-risk systems

- [ ] Does the system interact with human users? If yes: disclosure at session start.
- [ ] Does the system generate text, audio, image, or video content? If yes: machine-readable AI label on outputs.
- [ ] Does the system infer emotional states or biometric categories? If yes: user notification.
- [ ] Is the disclosure clear, distinguishable, and at the start of the interaction?
- [ ] Is there a documented rationale for any claimed exception?

## Enforcement timeline
Art. 50 obligations apply from 2025-08-02.
