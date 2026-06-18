# Legal Audit — Sources and Asset Template

Stable reference URLs for currency checks and framework extension, plus the structure every
obligation-cluster asset must follow.

## 1§ Reference URLs (stable)

EU-wide (EU AI Act + GDPR):
- EU AI Act: https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
- AI Act explorer: https://artificialintelligenceact.eu/ai-act-explorer/
- GDPR: https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
- EDPB AI guidance: https://www.edpb.europa.eu/our-work-tools/our-documents/topic/artificial-intelligence_en
- MiFID II: https://eur-lex.europa.eu/eli/dir/2014/65/oj/eng
- MiCA: https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng
- PRIIPs: https://eur-lex.europa.eu/eli/reg/2014/1286/oj/eng

Germany-specific:
- BaFin (Finanzmarktaufsicht): https://www.bafin.de
- BaFin FinTech: https://www.bafin.de/DE/Aufsicht/FinTech/fintech_artikel.html
- Gesetze im Internet (alle deutschen Gesetze): https://www.gesetze-im-internet.de
- KWG: https://www.gesetze-im-internet.de/kredwg/
- WpIG: https://www.gesetze-im-internet.de/wpig/
- TTDSG (Cookies): https://www.gesetze-im-internet.de/ttdsg/
- DDG (Impressumspflicht, ex-TMG): https://www.gesetze-im-internet.de/ddg/
- BFSG (Barrierefreiheit): https://www.gesetze-im-internet.de/bfsg/
- KSchG: https://www.gesetze-im-internet.de/kschg/
- ArbZG: https://www.gesetze-im-internet.de/arbzg/
- BetrVG: https://www.gesetze-im-internet.de/betrvg/
- RDG (Rechtsdienstleistungen): https://www.gesetze-im-internet.de/rdg/
- StBerG (Steuerberatung): https://www.gesetze-im-internet.de/stberg/
- EDPB Opinion 28/2024 (AI models): https://www.edpb.europa.eu/our-work-tools/our-documents/opinion-board-art-64/opinion-282024-certain-data-protection-aspects_en

## 2§ Asset file template
Every obligation-cluster asset follows this structure. Existing assets that deviate should be
brought into conformance when next updated.

### 2.1§ Required header (all comment lines)

```text
# <Jurisdiction> <Law domain> — <Topic>
# updated: YYYY-MM-DD
# check-interval-days: <number>
# sources:
#   <Law name or short description>: <stable URL>
#   [additional sources — one per line]
# Hinweis: Gilt für <Deutschland / EU-wide>. Keine Rechtsberatung.
```

The `updated:` date and `sources:` block are mandatory — they are read programmatically during the
currency check.

### 2.2§ check-interval-days guidance

| Domain | Interval |
|---|---|
| EU AI Act — actively evolving; EC delegated acts, EDPB guidance | 60 |
| Financial regulation — BaFin circulars, MiCA rollout, threshold changes | 60 |
| GDPR, German employment law, internet/app law, consulting law | 90 |
| Stable BGB framework or constitutional law | 180 |

### 2.3§ Source URL requirements
- Use canonical government or EU-law stable URLs: `gesetze-im-internet.de` for German law;
  `eur-lex.europa.eu/eli/...` for EU law. These URLs are permanent.
- At least one source URL per named statute referenced in the asset.
- For assets with numerical thresholds that change (amounts, dates, limits): include a secondary URL
  providing the current value directly — e.g. BMAS for Mindestlohn, BaFin for licensing thresholds.
  Mark these: `# <Law> (Betrag/Datum prüfen): <URL>`.

### 2.4§ Required body sections (in order)
1. `## Scope-Trigger` — one or two sentences; "Dieses Asset laden wenn das Projekt: ..."
2. `## 1. <Primary topic>` through `## N. <Last topic>` — numbered sections; tables for tabular law
   data (thresholds, obligation matrices, licensing requirements); prose for exceptions and grey areas.
3. `## Compliance-Checkliste` — bullet list using `- [ ]`; one item per verifiable obligation, phrased
   as an actionable yes/no check.

### 2.5§ Naming convention
File name: `<domain>-<topic>.md` in lowercase kebab-case. Examples: `financial-trading.md`,
`employment-law.md`, `consulting-law.md`. After creating a new asset, add a row to the 5§ loading
table in `SKILL.md`.
