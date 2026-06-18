# EU AI Act — Risk Classification Reference
# updated: 2026-06-11
# check-interval-days: 60
# sources:
#   EU AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
#   AI Act explorer: https://artificialintelligenceact.eu/ai-act-explorer/
#   EC compliance checker: https://ai-act-service-desk.ec.europa.eu/en/eu-ai-act-compliance-checker
# Hinweis: EU-wide. Keine Rechtsberatung.

## Risk tiers (Art. 3, Art. 5, Art. 6, Annex III)

### Prohibited (Art. 5) — enforcement from 2025-02-02
Systems that are banned outright regardless of safeguards:
- Subliminal, manipulative, or deceptive techniques that impair autonomous decision-making
- Exploitation of vulnerabilities of specific groups (age, disability)
- Social scoring by public authorities
- Real-time remote biometric identification in publicly accessible spaces by law enforcement (with narrow exceptions)
- Retrospective remote biometric identification unless authorized by judicial/administrative authority
- Emotion inference in workplace or educational settings
- Biometric categorization inferring sensitive attributes (race, political opinion, religion, sexual orientation)
- AI-assisted individual crime prediction based on profiling (without objective individual evidence)

### High-risk (Art. 6 + Annex III) — enforcement from 2026-08-02
AI systems listed in Annex III used in specific contexts:
- Biometric identification and categorization (not prohibited)
- Critical infrastructure management (water, gas, electricity, transport)
- Education: determining access, admission, assessment outcomes
- Employment: recruitment, promotion, task allocation, performance monitoring
- Essential private and public services: credit scoring, insurance risk, public benefit eligibility
- Law enforcement: risk assessment, evidence reliability, crime prediction
- Migration: border control, visa/asylum assessment
- Administration of justice: legal research assistance, judicial decisions

High-risk providers must:
- Establish a risk management system (Art. 9)
- Meet data governance requirements (Art. 10)
- Produce technical documentation (Art. 11 + Annex IV)
- Enable automatic logging (Art. 12)
- Ensure transparency to deployers (Art. 13)
- Implement human oversight measures (Art. 14)
- Meet accuracy, robustness, and cybersecurity standards (Art. 15)
- Register in the EU database (Art. 71) before placing on market

### Limited-risk — Art. 50 transparency obligations
Applies when the system:
- Interacts with humans (chatbots, AI assistants visible to end users)
- Generates synthetic content (text, audio, image, video)
- Uses emotion recognition or biometric categorization

Obligations: inform users they are interacting with AI (unless obvious from context);
label synthetic content as AI-generated. See ai-act-transparency.md for details.

### Minimal risk — no AI Act obligations
All other AI systems. GDPR still applies where personal data is processed.

## Role definitions relevant to compliance obligations

| Role | Definition | Obligations |
|---|---|---|
| Provider | Develops or places an AI system on the market under own name | Primary: risk management, documentation, conformity assessment, registration |
| Deployer | Uses an AI system for own purposes | Secondary: human oversight, monitoring, DPIA if high-risk, user notification |
| Importer | Brings non-EU provider's AI system into EU market | Verify CE marking, documentation, registration |
| GPAI provider | Places a general-purpose AI model on the market | See ai-act-gpai.md |

## Classification decision aid

1. Is the system or use case on the Art. 5 prohibited list? → STOP. Prohibited.
2. Is the AI system used in an Annex III context with significant effects on persons? → High-risk.
3. Does the system interact with humans, generate synthetic content, or infer emotions? → Limited-risk (Art. 50).
4. None of the above → Minimal risk (GDPR may still apply).

Note: "significant effects" and Annex III scope involve legal interpretation.
A human lawyer must confirm high-risk classification before compliance planning.
