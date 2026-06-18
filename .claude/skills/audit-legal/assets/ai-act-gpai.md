# EU AI Act — General-Purpose AI (GPAI) Obligations (Art. 51–56)
# updated: 2026-06-11
# check-interval-days: 60
# sources:
#   EU AI Act (Art. 53–56): https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
#   AI Act explorer: https://artificialintelligenceact.eu/ai-act-explorer/
#   EC GPAI Code of Practice: https://digital-strategy.ec.europa.eu/en/policies/ai-act-gpai-codes-practice
# Hinweis: EU-wide. Keine Rechtsberatung.

## Who is a GPAI provider?
A provider that trains and places a general-purpose AI model on the market.
A GPAI model is trained on large amounts of data, is general in purpose, and
can serve a significant variety of downstream tasks.

Threshold indicators (non-exhaustive):
- Training compute: ≥10^23 floating-point operations (FLOP)
- Parameters: typically >1 billion (not a hard legal threshold — context-dependent)

Key distinction:
- Anthropic (Claude), OpenAI (GPT), Google (Gemini) → GPAI providers; obligations fall on them
- A developer using Claude API to build a product → DEPLOYER of a GPAI model; most GPAI obligations do not apply
- A developer fine-tuning a GPAI model and releasing it → may become a GPAI provider for the modified model

## Standard GPAI obligations (Art. 53) — from 2025-08-02
Applies to all GPAI providers (not deployers):

1. Technical documentation: prepare and maintain documentation per Annex XI before placing on market
2. Copyright policy: implement a policy complying with Directive 2019/790 (Copyright in Digital Single Market); respect opt-outs under Art. 4(3)
3. Training data summary: publish a sufficiently detailed summary of training data used; include categories of data, geographic sources, and any filtering applied
4. Downstream provider support: provide information and technical access to allow providers building on the GPAI model to comply with their own obligations
5. GDPR data requests: implement procedures to address requests from persons wishing to exercise GDPR rights regarding training data (erasure, access, rectification)

## Free and open-source GPAI exception (Art. 53.2)
Providers of GPAI models with publicly released weights (truly open-source):
- Exempt from Art. 53.1 obligations EXCEPT:
  - Copyright policy requirement (Art. 53.1.c) still applies
  - Systemic risk models remain fully subject (exception does not apply if >10^25 FLOP)

## Systemic risk GPAI (Art. 55) — high compute or EC designation
Applies when: training compute ≥10^25 FLOP OR model is designated by the European Commission.

Additional obligations:
- Adversarial testing and red-teaming before release
- Incident reporting to the AI Office (serious incidents, malfunctions)
- Cybersecurity protection measures
- Energy consumption reporting

## Relevance assessment for typical harness users
Most users of this harness build tooling ON TOP of GPAI models (Claude, GPT, etc.)
rather than developing GPAI models themselves. In this case:
- GPAI provider obligations belong to Anthropic/OpenAI/Google — not to the harness user
- Harness user obligations: deployer obligations (Art. 29), Art. 50 transparency if user-facing
- Exception: if the user fine-tunes and redistributes a model, re-assess provider status
