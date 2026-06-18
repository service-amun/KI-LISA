# GDPR — Data Protection Impact Assessment (DPIA) Triggers
# updated: 2026-06-11
# check-interval-days: 90
# sources:
#   GDPR (Art. 35): https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
#   EDPB WP 248 (DPIA guidelines): https://www.edpb.europa.eu/our-work-tools/our-documents/wp29-guidelines/guidelines-data-protection-impact-assessment-dpia_en
# Hinweis: EU-wide. Keine Rechtsberatung.

## When is a DPIA mandatory? (Art. 35.1)
A DPIA is required when processing is likely to result in a high risk to
the rights and freedoms of natural persons. It must be carried out BEFORE
the processing begins.

## Art. 35.3 — Processing types that always require a DPIA
- Systematic and extensive evaluation of personal aspects (including profiling) with automated processing, on which decisions with legal or similarly significant effects are based
- Large-scale processing of special category data (Art. 9) or criminal conviction data (Art. 10)
- Systematic monitoring of a publicly accessible area on a large scale

## EDPB WP 248 — Nine criteria (DPIA required if ≥2 apply)

| # | Criterion | Examples |
|---|---|---|
| 1 | Evaluation or scoring, including profiling | Credit scoring, behaviour prediction, health risk assessment |
| 2 | Automated decision-making with legal or significant effects | Automated loan approval, HR screening, insurance denial |
| 3 | Systematic monitoring | Email monitoring, location tracking, network surveillance |
| 4 | Sensitive data or data of highly personal nature | Special categories (Art. 9), criminal data, financial data, location data |
| 5 | Data processed on a large scale | Millions of records, or processing covering a significant proportion of a population |
| 6 | Matching or combining datasets | Combining data from multiple sources in ways the data subject would not expect |
| 7 | Data concerning vulnerable subjects | Minors, patients, employees (power imbalance), asylum seekers |
| 8 | Innovative use or applying new technological or organisational solutions | AI/ML, IoT, biometrics — any novel technical approach |
| 9 | Processing that prevents data subjects from exercising rights or using services | Blacklisting, fraud screening that denies access |

## Assessment for AI systems
AI tools nearly always trigger criterion 8 (innovative technology). Where personal
data is also involved, check criteria 1, 2, 4, 5, and 7 systematically.

Common AI scenarios and trigger count:
- AI assistant reading employee emails: criteria 1, 3, 7 → ≥2 → DPIA required
- AI-driven resume screening: criteria 1, 2, 7 → ≥2 → DPIA required
- AI inference on health data: criteria 1, 4, 8 → ≥2 → DPIA required
- Internal coding assistant not processing personal data: likely criteria 8 only → assess further

## What a DPIA must contain (Art. 35.7)
1. Systematic description of the processing: purpose, nature, scope, context, necessity
2. Assessment of necessity and proportionality of processing in relation to the purpose
3. Assessment of the risks to the rights and freedoms of data subjects
4. Measures envisaged to address the risks (safeguards, security measures, mechanisms to ensure protection of personal data)

## When a DPIA is not sufficient
If the DPIA indicates high residual risk that cannot be mitigated: prior consultation
with the national supervisory authority (DPA) is mandatory before processing (Art. 36).

## Key point for AI tooling
The EDPB's Opinion 28/2024 specifically addresses AI models trained on personal data:
- LLMs rarely achieve anonymization; training data often contains personal data
- If an AI model was trained on personal data, the training itself may require a legal basis
- Deploying such a model constitutes processing — DPIA trigger criteria apply

## DPIA obligation checklist

- [ ] Listed the personal data processing activities in the project
- [ ] Assessed all nine WP 248 criteria for each processing activity
- [ ] Activities with ≥2 criteria: DPIA initiated before processing starts
- [ ] DPIA contains all four Art. 35.7 elements
- [ ] Residual risks assessed; if high: DPA consulted before launch (Art. 36)
- [ ] DPIA reviewed when processing changes materially
