# GDPR — Core Data Processing Obligations
# updated: 2026-06-11
# check-interval-days: 90
# sources:
#   GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
#   EDPB guidance: https://www.edpb.europa.eu/our-work-tools/our-documents/topic/artificial-intelligence_en
#   BDSG: https://www.gesetze-im-internet.de/bdsg_2018/
# Hinweis: EU-wide (GDPR); BDSG ergänzt für Deutschland. Keine Rechtsberatung.

## Art. 5 — Processing principles (always applicable)
All personal data processing must comply with all six principles simultaneously:

| Principle | Requirement |
|---|---|
| Lawfulness, fairness, transparency | Legal basis required; processing must be fair; data subjects informed |
| Purpose limitation | Collected for specified, explicit, legitimate purposes; no incompatible further use |
| Data minimisation | Adequate, relevant, limited to what is necessary for the purpose |
| Accuracy | Kept accurate and up to date; inaccurate data erased or rectified without delay |
| Storage limitation | Not kept longer than necessary; define and enforce retention periods |
| Integrity and confidentiality | Appropriate technical and organisational security measures |

## Art. 6 — Legal bases for processing (one required per processing activity)

| Legal basis | When applicable |
|---|---|
| Consent (Art. 6.1.a) | Freely given, specific, informed, unambiguous. Withdrawable at any time. Rarely appropriate for B2B tools. |
| Contract (Art. 6.1.b) | Processing necessary for performing a contract with the data subject |
| Legal obligation (Art. 6.1.c) | Required by EU or Member State law |
| Vital interests (Art. 6.1.d) | Life or death situations — very narrow |
| Public task (Art. 6.1.e) | Public authority exercising official functions |
| Legitimate interest (Art. 6.1.f) | Balancing test required; does not override data subject rights; common for B2B analytics |

For AI tools: contract (Art. 6.1.b) and legitimate interest (Art. 6.1.f) are the most
common bases. Document the legal basis before processing begins.

## Art. 9 — Special category data (stricter obligations)
Special categories: racial/ethnic origin, political opinions, religious/philosophical beliefs,
trade union membership, genetic data, biometric data for identification purposes, health data,
sex life or sexual orientation data.

Default: processing is prohibited unless one of Art. 9.2 exceptions applies:
- Explicit consent (Art. 9.2.a)
- Employment/social security law obligations (Art. 9.2.b)
- Vital interests (Art. 9.2.c)
- Legitimate activities of foundations, associations (Art. 9.2.d)
- Manifestly made public by data subject (Art. 9.2.e)
- Legal claims (Art. 9.2.f)
- Substantial public interest (Art. 9.2.g — requires Member State law)
- Health/medical purpose (Art. 9.2.h/i)
- Public health (Art. 9.2.i)
- Archiving, research, statistics (Art. 9.2.j)

AI systems that infer or process special categories require a separate legal basis
under Art. 9 in addition to the Art. 6 basis.

## Art. 22 — Automated individual decision-making
Applies when: a decision is based solely on automated processing (no meaningful human
involvement) and produces legal effects or similarly significantly affects a person.

Default: prohibited unless:
- Necessary for contract (Art. 22.2.a) — with right to human review
- Authorised by EU/Member State law (Art. 22.2.b)
- Based on explicit consent (Art. 22.2.c)

When permitted: data subject must have right to obtain human intervention, express
point of view, and contest the decision (Art. 22.3).

Relevance for AI tools: any AI-driven decision that affects employment, creditworthiness,
insurance, housing, or similar — assess whether Art. 22 applies.

## Art. 25 — Data protection by design and by default
Obligation: implement appropriate technical and organisational measures from the design
phase to implement data protection principles effectively. Default settings must ensure
only necessary personal data is processed.

Practical requirements:
- Pseudonymisation and data minimisation built into architecture
- Least-privilege access controls implemented from the start
- Privacy-preserving settings as the default (not opt-out)
- Regular assessment of whether processing design still meets the purposes

## Art. 28 — Controller-processor agreements
Applies when: using a third-party service that processes personal data on your behalf
(e.g. Claude API with personal data, cloud storage, analytics providers).

Obligation: written contract must be in place before any data is transferred. The
contract must include the Art. 28.3 mandatory clauses: purpose limitation, processing
on documented instructions only, confidentiality, security measures, sub-processor
rules, assistance with data subject rights, deletion/return of data, audit rights.

For AI API usage: if personal data is sent to an AI API (Claude, GPT, etc.) in prompts
or context, a Data Processing Agreement (DPA) with the API provider is required.
Check whether the API provider's standard DPA covers your use case.

## Quick compliance checklist

- [ ] Legal basis documented for each processing activity (Art. 6)
- [ ] Special category data identified; separate Art. 9 basis documented if applicable
- [ ] Privacy notice provided to data subjects (Art. 13/14)
- [ ] Data retention periods defined and enforced
- [ ] Art. 22 assessed for any automated decision-making
- [ ] Privacy by design applied from architecture stage (Art. 25)
- [ ] DPA in place with all processors handling personal data (Art. 28)
- [ ] Security measures proportionate to risk (Art. 32)
- [ ] DPIA completed where required (Art. 35) — see gdpr-dpia-triggers.md
