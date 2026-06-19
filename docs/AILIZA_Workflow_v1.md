# AILIZA Workflow v1.0

sicher im Kern · schnell im Alltag · einfach für KMU

## 1§ Zielbild & Bewertungsregel

AILIZA verarbeitet jede Anfrage — schnell, verständlich, datensparsam, nachvollziehbar, mandantensicher, mit klarer Freigabe bei Risiko und ohne ungeprüften externen Datenabfluss.

### 1.1§ Bewertungsregel für jede Änderung

Jede Änderung am System wird anhand von vier Kriterien bewertet. Die strengste Anforderung gewinnt.

| Kriterium | Frage | Bestanden wenn |
|---|---|---|
| Nutzerfreundlichkeit | Versteht ein KMU-Mitarbeiter ohne IT-Kenntnisse sofort, was passiert? | Ja — keine technischen Begriffe, keine offene Frage ohne Antwort |
| Schnelligkeit | Gibt es einen Fast-Path für einfache Anfragen? | Ja — Simple-Route < 200 ms; Standard-Route < 3 s |
| DSGVO | Sind Daten minimiert, zweckgebunden und löschbar? | Ja — Lineage vorhanden, Retention definiert, Löschfunktion getestet |
| Rechtssicherheit | Ist die Verantwortung klar, der Provider bekannt, die Freigabe dokumentiert? | Ja — ProviderProfile, AVV-Status, Audit-Log, RACI gepflegt |

### 1.2§ Prioritätsregel

1. Datenschutz und Rechtssicherheit zuerst — keine Funktion geht live ohne Datenflussinventar und Rechtsgrundlage.
2. Nutzerführung so einfach wie möglich — KMU-Mitarbeiter dürfen keinen technischen Schritt machen müssen.
3. Performance optimieren — erst wenn Schritt 1 und 2 erfüllt sind.

### 1.3§ Sprachregelung (DSGVO und Einwilligung)

Wichtig: "DSGVO-konform" ist eine rechtliche Gesamtaussage, die eine vollständige Prüfung aller 99 DSGVO-Artikel voraussetzt. Für einzelne technische Maßnahmen gelten folgende Formulierungen:

- Erlaubt: "DSGVO-orientiert", "unterstützt DSGVO-Anforderungen", "reduziert DSGVO-Risiken"
- Nicht erlaubt für Einzelmaßnahmen: "DSGVO-konform"

Wichtig: "Einwilligung" ist ein spezifischer DSGVO-Rechtsbegriff (Art. 6 Abs. 1 lit. a) mit strengen formalen Anforderungen (freiwillig, informiert, spezifisch, widerrufbar). In der Produkt-UI und im Nutzer-Dialog gelten folgende Formulierungen:

- Erlaubt: "Freigabe", "Nutzerbestätigung"
- Nicht erlaubt in der UI: "Einwilligung" — dieser Begriff darf nur in rechtlichen Dokumenten (Datenschutzhinweise, VVT, DSFA) verwendet werden.

---

## 2§ Gesamtarchitektur — Datenfluss

### 2.1§ Hauptfluss

```
Input (Chat / Datei / Memory / Tool / CRM / Websuche)
  |
  v
Stufe 1: Anfrage-Eingang (Sofortprüfung)
  |
  v
Stufe 2: Data Governance Layer (Klassifikation + Lineage)
  |
  v
Stufe 3: Policy-Gateway (Entscheidung: erlauben / warnen / anonymisieren / Freigabe / blockieren)
  |
  | (wenn nicht blockiert)
  v
Stufe 4: Routing & Performance (Route wählen)
  |
  v
Stufe 5: Provider-Orchestrator (wenn extern nötig)
  |
  v
Stufe 6: Redaction & Prompt-Building
  |
  v
Stufe 7: Antwort-Erzeugung (LLM / Lokal / Tool)
  |
  v
Stufe 8: Output-Guardrail (PII + Compliance-Check vor Ausgabe)
  |
  v
Stufe 9: Logging (4 getrennte Log-Typen — niemals Inhalte)
  |
  v
Stufe 10: Nutzeranzeige (lokal/extern/Freigabe/Risikoampel)
```

### 2.2§ Parallele Threads

Die folgenden Threads laufen parallel zum Hauptfluss:

| Thread | Startet | Beschreibung |
|---|---|---|
| Freigabe-Dialog | Wenn Policy-Gateway "Freigabe nötig" entscheidet | Zeigt Nutzer was, wohin, warum, wie lange; wartet auf Bestätigung |
| Memory-Retrieval | Vor Stufe 6 (Prompt-Building) | Ruft relevante Memory-Fakten ab — nur nach Retrieval-Policy |
| Feedback-Loop | Nach Stufe 10 (Nutzeranzeige) | Nutzer bewertet Antwort; quality_score wird aktualisiert |
| Kostenkontrolle | Vor Stufe 5 (Schätzung) und nach Stufe 7 (Actual) | Token-Budget prüfen; Hard-Limit durchsetzen |

---

## 3§ Stufe 1 — Anfrage-Eingang

### 3.1§ Input-Quellen

| Quelle | Beispiel | Besonderheit |
|---|---|---|
| Chat-Eingabe | Text; Frage | Direkt; häufigster Pfad |
| Datei-Upload | PDF; DOCX; XLSX | Eigener Dokumenten-Workflow (Stufe 13); riskanter als Chat |
| Memory | Gespeicherte Facts aus früheren Sessions | Retrieval-Policy muss erfüllt sein (Stufe 12) |
| Tool-Ergebnis | Web-Suche; CRM-Abfrage | Quelle wird in Lineage eingetragen |
| CRM / Kalender / Notion / API | Externe Systeme | Explizite Freigabe durch Admin nötig |
| Websuche | Tavily | Öffentliche Quellen; trotzdem klassifizieren — Ergebnis kann PII enthalten |

### 3.2§ Sofortprüfung (vor Data Governance Layer)

Alle sechs Prüfungen müssen bestanden werden. Reihenfolge ist verbindlich.

1. Mandant vorhanden und aktiv? — Kein Mandant gefunden: sofortige Fehlermeldung, kein Logging von Inhalt.
2. Nutzer authentifiziert und Session gültig? — Session abgelaufen: neue Anmeldung anbieten.
3. Rate-Limit eingehalten (pro Nutzer + pro Mandant)? — Überschritten: Wartezeit in einfachem Deutsch nennen.
4. Dateigröße und Promptgröße innerhalb der Limits? — Zu groß: Aufteilung vorschlagen.
5. Kill-Switch `AILIZA_EXTERNAL_LLM_ENABLED` aktiv (True)? — Deaktiviert: lokale Weiterarbeit anbieten.
6. Externe KI für diesen Mandanten grundsätzlich aktiviert? — Nicht aktiviert: Onboarding-Assistent starten.

Wenn eine Prüfung fehlschlägt: sofortige klare Fehlermeldung in einfachem Deutsch, kein Stack-Trace, sichere Alternative nennen. Kein Logging von Prompt-Inhalten im Fehlerfall.

Hinweis: Der Fast-Path (Simple-Route) darf nur starten, wenn keine sensiblen Muster erkannt wurden. Auch lokale Verarbeitung ist DSGVO-relevant — interne Datenschutzregeln, Mandantenfilterung und Logging-Vorgaben gelten immer, unabhängig davon ob ein externer Provider beteiligt ist.

---

## 4§ Stufe 2 — Data Governance Layer

Der Data Governance Layer (DGL) sitzt zwischen Anfrage-Eingang und Policy-Gateway. Er läuft vor jeder Policy-Entscheidung und vor jedem Modell-Aufruf. Kein externer LLM-Aufruf findet vor dem DGL statt.

### 4.1§ Multi-Label-Klassifikation (11 Stufen)

Ein Datenobjekt kann mehrere Klassen gleichzeitig tragen. Die strengste Regel gewinnt.

| Stufe | Klasse | Beispiele (KMU-relevant; Innenarchitektur-spezifisch) | Standard-Zielsystem |
|---|---|---|---|
| 0 | Public | Webseiten; Pressemitteilungen; Produktbeschreibungen | Alle erlaubt |
| 1 | Internal | Organigramme; Meetingnotizen ohne PII; Vorlagen | Lokal + geprüfte Provider |
| 2 | Confidential | Umsätze; Margen; Angebote; Grundrisse; Bauzeichnungen; Kalkulationen; Lieferantenverträge | Nur anonymisiert extern |
| 3 | Personal Data | Name; Adresse; E-Mail; Telefon; IP; Session-ID (DSGVO Art. 4) | Nur nach Freigabe extern |
| 4 | Special Category | Gesundheit; Religion; Ethnie; Gewerkschaft; Biometrie; Sexualität (DSGVO Art. 9) | Niemals extern |
| 5 | Credentials | Passwörter; API-Keys; Tokens; SSH-Keys — sofort blockieren | Niemals speichern oder senden |
| 6 | Financial | IBAN; Kreditkarte; Steuerdaten; Gehaltslisten; Buchhaltung | Niemals extern |
| 7 | HR | Bewerbungen; Leistungsbewertungen; Abmahnungen | Niemals extern |
| 8 | Legal | Verträge; Rechtsgutachten; Streitfälle | Niemals extern |
| 9 | Intellectual Property | Quellcode; Prompts; Architektur; Produkt-Roadmaps | Niemals extern |
| 10 | Security Sensitive | Netzwerkpläne; Schwachstellenberichte; Penetrationstests | Niemals extern |

### 4.2§ Erweiterte Zielsystem-Matrix

Die Matrix zeigt, in welchem System welche Datenklasse gespeichert oder verarbeitet werden darf. "Ja" bedeutet erlaubt; "Nein" bedeutet verboten; Einschränkungen sind benannt.

| Datenklasse | RAM | Session | Audit-Log | File Storage | Memory | Vector DB | External LLM | CRM | E-Mail | Admin UI |
|---|---|---|---|---|---|---|---|---|---|---|
| Public (0) | Ja | Ja | Meta only | Ja | Ja | Ja | Ja | Ja | Ja | Ja |
| Internal (1) | Ja | Ja | Meta only | Ja | Ja | Ja | Nach Prüfung | Ja | Ja | Ja |
| Confidential (2) | Ja | Ja | Meta only | Ja | Pseudonymisiert | Pseudonymisiert | Nur anonymisiert | Ja | Nein | Ja |
| Personal Data (3) | Ja | Ja | Meta only | Temporär | Mit TTL | Mit TTL | Nach Freigabe | Ja | Nein | Eingeschränkt |
| Special Category (4) | Temporär | Ja | Nein | Nein | Nein | Nein | Nein | Nein | Nein | Nein |
| Credentials (5) | Nein | Nein | Event only | Nein | Nein | Nein | Nein | Nein | Nein | Nein |
| Financial (6) | Ja | Ja | Meta only | Temporär | Nein | Nein | Nein | Nein | Nein | Eingeschränkt |
| HR (7) | Ja | Ja | Meta only | Temporär | Nein | Nein | Nein | Nein | Nein | Nein |
| Legal (8) | Ja | Ja | Meta only | Temporär | Nein | Nein | Nein | Nein | Nein | Nein |
| IP (9) | Ja | Ja | Meta only | Ja | Nein | Nein | Nein | Nein | Nein | Ja |
| Security (10) | Ja | Ja | Meta only | Ja | Nein | Nein | Nein | Nein | Nein | Eingeschränkt |

### 4.3§ Lineage-Metadaten

Jedes Datenobjekt erhält beim Eingang einen Lineage-Eintrag. Dieser begleitet das Objekt durch alle Stufen.

```
{
  data_class: [list],
  source: user_input | pdf_upload | crm | calendar | web_search | memory | tool,
  tenant_id: str,
  user_id: str (gehasht),
  created_at: ISO-8601,
  retention_days: int,
  external_allowed: bool,
  purposes: [list]
}
```

### 4.4§ Klassifikations-Methoden nach Phase

| Phase | Methode | Wann | Begründung |
|---|---|---|---|
| P0 | Pattern-basiert lokal (Regex) | Immer; vor jedem anderen Schritt | Credentials; PII; IBAN; Steuernummer; Telefon-DE — kein externer LLM-Aufruf; verhindert 500–2000 ms Latenz |
| P2 | LLM-gestützt | Nur nach Gate 2; nur wenn Pattern nicht ausreicht | Confidential; Legal; IP — nur wenn Kontextverständnis nötig ist |

Hinweis: LLM-gestützte Klassifikation ist selbst ein externer Aufruf und unterliegt denselben Governance-Regeln. Sie darf niemals zur Klassifikation von Stufe-5-Daten eingesetzt werden.

---

## 5§ Stufe 3 — Policy-Gateway

Das Policy-Gateway ist die zentrale Entscheidungsinstanz. Es empfängt den vollständigen PolicyContext vom Data Governance Layer und entscheidet, was mit der Anfrage geschieht.

Fail-closed: Wenn das Policy-Gateway einen Fehler wirft, kein Mandantenprofil findet oder die Datenklasse unbekannt ist, wird die Anfrage blockiert. Kein Fallback auf "erlauben".

### 5.1§ Entscheidungsgrundlagen (PolicyContext)

Der PolicyContext enthält alle Felder, die für eine Entscheidung nötig sind:

```
policy_version
data_classes (Multi-Label-Liste vom DGL)
purposes
provider_profile
user_role
tenant_id
tool_capability
redaction_status
approval_status
cost_remaining
kill_switch_status
```

### 5.2§ Entscheidungsmatrix

| Situation | Entscheidung | Nutzeranzeige |
|---|---|---|
| Alle Klassen <= Internal; Provider OK; Budget OK | Erlauben | Grüne Ampel |
| PII erkannt; Provider hat AVV; Freigabe liegt vor | Erlauben mit Hinweis | Gelbe Ampel + "externe KI verwendet" |
| PII oder Vertraulich erkannt; kein Redaction-Status | Anonymisieren + Hinweis | Gelbe Ampel + "Daten werden anonymisiert" |
| Klasse >= Confidential (2); kein explizites OK | Freigabe nötig | Orange Ampel + Freigabe-Dialog |
| Klasse >= Special Category (4) oder Credentials (5) oder kein Provider-AVV | Blockieren | Rote Ampel + Begründung + sichere Alternative |
| Kill-Switch aktiv | Blockieren | "Externe KI nicht verfügbar — lokal weiterarbeiten" |

### 5.3§ Rote Ampel — kein normaler Freigabe-Pfad

Rot wird nicht im normalen Chat-Flow freigegeben. Ausnahmen laufen ausschließlich über einen dokumentierten Ausnahmeprozess außerhalb des Chat-Flows. Anforderungen an den Ausnahmeprozess:

- Admin und Datenschutzbeauftragter (DSB) werden informiert und müssen zustimmen.
- Ausnahme wird protokolliert, versioniert und begründet.
- Ausnahme ist zeitlich befristet.
- Kein Nutzer kann eine Rot-Blockierung eigenständig aufheben.

---

## 6§ Stufe 4 — Routing & Performance

Nach der Freigabe durch das Policy-Gateway wählt der Router die schnellste sichere Route.

### 6.1§ Route-Tabelle

| Route | Trigger | Modell | Ziel-Latenz | Verarbeitung | Output-Modus |
|---|---|---|---|---|---|
| Simple | Begrüßung; Datum; einfache Rechnung; Hilfetext | Lokal (kein LLM) | < 200 ms | Synchron; Fast-Path-Router | Direkt |
| Standard | Allgemeine Anfragen; kein Compliance-Bezug | Llama 3.1-8B via Groq | < 3 s | Synchron + Streaming | Token-Streaming |
| Komplex | Compliance; Analyse; Code; Legal | Llama 3.3-70B via Groq | < 10 s | Streaming mit Satz-Pufferung | Gepuffert |
| Dokument | PDF/DOCX-Upload; langer Text | Llama 3.1-8B + Chunking | < 30 s | Async + Fortschrittsanzeige 0–100% | Ergebnis + Quellenhinweis |
| Riskant | HR; Kredit; Medizin; Hochrisiko | Llama 3.3-70B + Output-Check + Freigabe | Variabel | Freigabe vor Ausführung | Gepuffert + Prüfhinweis |

### 6.2§ Performance-Maßnahmen

| Maßnahme | Zweck | Phase |
|---|---|---|
| Fast-Path-Router (Regex/Dict; 0 Token) | Simple-Route < 200 ms | P0 |
| Token-Budget-Gateway (Schätzung vor Routing) | Modellklasse wirtschaftlich wählen | P0 |
| Datenklassifikation lokal/pattern-basiert (kein ext. LLM) | Kein Klassifikations-Overhead | P0 |
| Compliance-Kontext Lazy-Load (nur COMPLEX/CRITICAL) | Latenz bei Simple/Standard reduzieren | P0 |
| Hard Timeouts: Groq 90 s → deutsche Fehlermeldung | Keine hängenden Requests | P0 |
| Retry nur HTTP 408/429/503: Exp. Backoff 100 ms; max 32 s; +-50% Jitter | Kein Thundering Herd | P0 |
| Connection Pooling (SQLite + httpx.AsyncClient global) | Verbindungsaufbau-Overhead reduzieren | P0 |
| asyncio.gather() für parallele Tool-Ausführung | Multi-Tool-Latenz senken | P1 |
| Streaming via fetch() ReadableStream (kein EventSource — GET-only) | Gefühlte Latenz senken | P1 (nach Schritt 8+9) |
| Async Dokumentenverarbeitung + Fortschritts-Endpoint | Kein Frontend-Freeze | P1 |
| Preloading häufiger Compliance-Muster beim App-Start | Kein Kalt-Start | P0 |

Hinweis: Hypothetische Einsparungswerte (z.B. "30% weniger Anfragen durch Cache") sind Schätzungen und dürfen erst nach echten Messdaten kommuniziert werden.

### 6.3§ Performance-Monitoring (Metriken ohne Inhaltslogs)

Erfasste Metriken: P50/P95/P99 Latenz je Route; Fehlerquote; Provider-Verfügbarkeit; Slow-Query-Log (> 5 s).

Speicherort: `data/metrics.db` (SQLite). Kein externer Monitoring-Dienst für MVP. Kein Prompt-Inhalt in Metriken.

---

## 7§ Stufe 5 — Provider-Orchestrator

Keine Geschäftslogik ruft Groq oder einen anderen externen Provider direkt auf. Alle externen Calls laufen durch den Provider-Orchestrator.

### 7.1§ LLMProvider Interface

Methoden:

```
generate(prompt, config) -> Response
stream(prompt, config) -> AsyncGenerator
count_tokens(text) -> int
estimate_cost(tokens, model) -> float
redact_or_prepare(text, data_classes) -> RedactedText
```

Properties:

```
supports_streaming: bool
supports_json_mode: bool
supports_eu_region: bool
max_context_tokens: int
data_residency: str
provider_profile_version: str
provider_region: str
```

### 7.2§ Ausführungs-Ablauf — 5 Pflicht-Checks

Alle fünf Checks müssen positiv sein, bevor ein externer Aufruf stattfindet:

1. Kill-Switch: `AILIZA_EXTERNAL_LLM_ENABLED = true`?
2. Policy-Gateway: `PolicyContext.decision = erlaubt`?
3. ProviderProfile: `avv_dpa_status = signed` und `allowed_data_classes` enthält alle aktuellen Klassen?
4. Daten: `redaction_status = complete`?
5. Kostenlimit: `cost_remaining > estimate_cost()`?

Wenn alle fünf bestanden: Provider wählen, Aufruf ausführen, Antwort empfangen. Wenn ein Check fehlschlägt: Fallback-Kette (7.3§).

### 7.3§ Fallback-Kette

```
Lokal (Fast-Path)
  -> kleines Modell (Llama 3.1-8B via Groq)
  -> großes Modell (Llama 3.3-70B via Groq)
  -> Abbruch mit sicherer Meldung in einfachem Deutsch
```

Kein stiller Fallback. Nutzer wird informiert, welche Route aktiv ist.

Groq ist der erste Adapter. Spätere Adapter: OpenAI-kompatible EU-Provider; lokale Modelle (für Klassifikation; Routing; PII-Erkennung).

### 7.4§ ProviderProfile Felder

| Feld | Typ | Beschreibung |
|---|---|---|
| provider | str | Name des Providers (z.B. "Groq") |
| model | str | Modell-ID (z.B. "llama-3.3-70b-versatile") |
| region | str | Serverstandort (z.B. "US"; "EU") |
| avv_dpa_status | enum | pending / signed / expired |
| logging | enum | none / metadata / full |
| training_use | enum | no / opt-out / yes |
| caching_policy | str | Dokumentiert; nicht blind vertrauen |
| data_residency | enum | EU / US / global |
| allowed_data_classes | list[int] | Erlaubte Stufen (z.B. [0, 1, 2, 3]) |
| retention_hours | int | Wie lange speichert Provider Daten |
| provider_terms_version | str | Version der geprüften AGB/DPA |

Wichtig: Provider-Caching darf nicht blind vertraut werden ("Groq regelt das"). Die `caching_policy` muss im ProviderProfile dokumentiert sein. Bei Änderung der Provider-AGB: Cache invalidieren und ProviderProfile versionieren.

---

## 8§ Stufe 6 — Redaction & Prompt-Building

### 8.1§ Redaction-Schritte (in dieser Reihenfolge — Reihenfolge ist verbindlich)

1. Credentials (Stufe 5): sofort blockieren — nicht ersetzen, kein Platzhalter, Sparse-Security-Event schreiben. Keine weiteren Schritte.
2. Special Category (Stufe 4): blockieren wenn extern — Anfrage an Policy-Gateway zurückgeben.
3. PII (Stufe 3): Platzhalter einsetzen (Format: `[EMAIL_001]`); Vault-Mapping in RAM; TTL 30 Minuten; thread-safe; Session-isoliert.
4. Confidential (Stufe 2): nur anonymisierte Zusammenfassung senden — kein Originaltext extern.
5. Financial/HR/Legal (Stufen 6–8): blockieren wenn extern.
6. Nur relevante Chunks senden — nicht die vollständige Konversationshistorie.
7. Memory-Fakten nur nach Retrieval-Policy (Stufe 12) injizieren — nicht automatisch.
8. Quellen und Kontext als separate System-Message trennen — nicht in User-Message mischen.

### 8.2§ Memory-Fakten als abgeleitete Daten

Memory-Fakten sind abgeleitete Daten und erhalten eigene Lineage-Metadaten:

```
{
  data_class: [list],
  source: str (aus welchem Dokument oder welcher Eingabe),
  tenant_id: str,
  created_at: ISO-8601,
  expires_at: ISO-8601,
  external_allowed: bool
}
```

Löschlogik: Wenn das Quelldokument oder die Quelleingabe gelöscht wird, werden alle abhängigen Memory-Fakten ebenfalls gelöscht — auch wenn ihr eigenes `expires_at` noch nicht erreicht ist.

---

## 9§ Stufe 7 — Antwort-Erzeugung

### 9.1§ Output-Modus je Route

| Route | Output-Modus | Besonderheit |
|---|---|---|
| Simple | Direkte lokale Antwort; < 200 ms | Kein LLM; kein externer Aufruf |
| Standard | Token-Streaming via fetch() ReadableStream | Stream startet nach Output-Guardrail-Init |
| Komplex | Satz-Pufferung: check_output() vor jeder Satz-Ausgabe | Stream pausiert bei Verstoß |
| Dokument | Fortschrittsanzeige 0–100% — dann Ergebnis + Quellenhinweis + Unsicherheitsvermerk | Async; keine Blockierung des Frontends |
| Riskant | Vollständige Pufferung — Output-Guardrail — dann Anzeige | Kein Token-for-Token-Streaming |
| Blockiert | Klare Begründung in einfachem Deutsch + sichere Alternative | Keine technische Fehlermeldung |

### 9.2§ Output-Guardrail (check_output) — Prüfliste

Der Output-Guardrail prüft jede Antwort vor der Ausgabe auf folgende Verstöße:

- PII im Output (Name; E-Mail; Telefon; IBAN; etc.)
- Unzulässige Rechtsberatung (automatisierte Rechtsauskunft ohne Prüfhinweis)
- HR-/Kredit-/Finanzentscheidungen automatisiert (EU AI Act Art. 6; Anhang III)
- Diskriminierende Aussagen
- Erfundene Quellen oder Halluzinationen ohne Unsicherheitsvermerk
- Riskante Handlungsaufforderungen ohne Prüfhinweis
- Fehlender Prüfhinweis bei Compliance-Themen

Bei Verstoß: Stream abbrechen; sichere Ersatzmeldung ausgeben; Security-Log-Eintrag schreiben. Kein stilles Verwerfen.

### 9.3§ Nutzeranzeige je Antwort

Jede Antwort zeigt eine kompakte Metadaten-Zeile (CSS-Klasse `msg-meta`):

| Information | Anzeige |
|---|---|
| Verarbeitungsort | "lokal verarbeitet" oder "externe KI verwendet: [Provider-Name]" |
| Speicherung | "gespeichert" oder "keine Speicherung" |
| Freigabe-Status | "Freigabe aktiv bis [Zeit]" oder "kein Freigabe-Schutz" |
| Risikoampel | Grün / Gelb / Orange / Rot — immer mit Textlabel (WCAG 2.1 AA — nie nur Farbe) |
| Quellangabe | Quelle und Stand bei Compliance-Aussagen |

EU AI Act Art. 50 Transparenzpflicht: Klare Kennzeichnung KI-generierter Inhalte ist Pflicht. Frist: 02.08.2026.

---

## 10§ Stufe 8 — Freigaben

### 10.1§ Freigabe-Dialog

Der Freigabe-Dialog wird in einfachem Deutsch ohne Fachbegriffe angezeigt. Kein Juridisch-Deutsch.

Anzuzeigende Informationen:

| Frage | Inhalt |
|---|---|
| Was wird verarbeitet? | Kurze Zusammenfassung der erkannten Datenklassen in einfacher Sprache |
| Wohin geht es? | Provider-Name + Region (z.B. "Groq; USA") |
| Warum ist Freigabe nötig? | Datenklasse + Risikogrund in einem Satz (z.B. "Ihre Anfrage enthält eine E-Mail-Adresse") |
| Wie lange gilt sie? | z.B. "Diese Freigabe gilt 30 Minuten für ähnliche Anfragen dieses Typs" |
| Welche Alternative gibt es? | Immer anbieten — lokal bearbeiten oder anonymisieren |

Buttons (in dieser Reihenfolge): Abbrechen | Anonymisieren | Lokal bearbeiten | Freigeben

Wichtig: In der UI niemals "Einwilligung" verwenden. Das ist ein DSGVO-Rechtsbegriff (Art. 6 Abs. 1 lit. a) mit strengen Anforderungen (freiwillig; informiert; spezifisch; widerrufbar). In der UI gilt: "Freigabe" oder "Nutzerbestätigung".

### 10.2§ Freigabe-Bundles

Freigaben können gebündelt werden, wenn Zweck, Datenklasse, Provider und Laufzeit übereinstimmen.

| Risikoampel | Bundle-Regel |
|---|---|
| Grün | Kein Bundle nötig — kein Freigabe-Dialog |
| Gelb | Bundle mit Hinweis erlaubt (15–60 Minuten) |
| Orange | Bundle nur mit Admin-Freigabe |
| Rot | Kein Bundle — blockiert; Ausnahmeprozess (5.3§) |

### 10.3§ Freigabe-Verlauf

Sichtbar im Admin-Dashboard: Zeitpunkt; Nutzer (pseudonymisiert); Datenklasse; Provider; Laufzeit; Ergebnis (freigegeben/abgelehnt/abgebrochen).

Admin kann Freigaben retroaktiv einsehen. DSB hat Lesezugriff auf Freigabe-Verlauf.

---

## 11§ Stufe 9 — Logging & Nachweis

### 11.1§ Vier getrennte Log-Typen

Die vier Log-Typen werden in getrennten SQLite-Tabellen gespeichert, haben getrennte Zugriffsrechte und getrennte Retention-Fristen.

| Log-Typ | Inhalt | Explizit NICHT | Retention | Zugriff |
|---|---|---|---|---|
| Audit-Log | policy_version; rule_id; data_class; action; provider; approval_status; user_role | Keine Prompts; keine Antworten; keine PII | 365 Tage | Admin; DSB |
| Security-Log | event_type; action; data_class; timestamp — kein Inhalt | Keine Secrets; keine Daten; keine Passwörter | 90 Tage | Security; DSB |
| Performance-Log | latency_ms; route; model; error_code; tokens_estimated | Keine Texte; keine Nutzerinformationen | 30 Tage | Admin; Betreiber |
| Cost-Log | tokens_actual; provider; model; tenant_id; use_case; cost_eur | Keine Inhalte; keine personenbezogenen Daten | 365 Tage | Admin; GF |

Niemals mischen. Getrennte Zugriffsrechte. Getrennte Retention.

### 11.2§ Löschprotokoll

Für jede Löschanfrage wird ein Nachweis erstellt:

```
{
  request_id: str,
  user_id: str (gehasht),
  deleted_at: ISO-8601,
  systems: [sessions, memory, vector_db, audit_log_anonymized, file_storage],
  data_classes: [list],
  success: bool
}
```

Hinweis: Löschprotokolle können selbst personenbezogene Daten enthalten. Sie sind daher minimal zu halten, zugriffsbeschränkt (nur DSB und Admin) und haben eine eigene Retention-Frist (empfohlen: 3 Jahre für DSGVO-Nachweiszwecke).

### 11.3§ Metadaten-Only-Prinzip

Kein Vollprompt im Log. Kein Secret im Log. Keine vollständige Antwort im Log.

Für kritische Incident-Fälle: opt-in gesicherter Incident-Snapshot — nur mit expliziter Aktivierung durch Admin und DSB. Eigene Retention: 30 Tage. Eigener Zugriffsschutz.

---

## 12§ Stufe 10 — Memory & Reflection

### 12.1§ Was gespeichert werden darf

| Kategorie | Beispiel | data_class | Extern erlaubt |
|---|---|---|---|
| Firmenvokabular | "Unser Produkt heißt ABI-3000" | vocabulary | Nach Providerprüfung |
| Nutzer-Präferenzen | "Schreibe immer 'Sie'" | correction | Nein |
| Nicht-sensitive FAQ-Muster | Interne Fragen ohne PII | pattern | Nach Prüfung |
| Projektkontext | Aktive Projekte (wenn admin-freigegeben) | context | Nur anonymisiert |

### 12.2§ Was nicht gespeichert werden darf

- Credentials (Stufe 5)
- Special Category (Stufe 4)
- HR-Daten (Stufe 7)
- Rechtsstreitigkeiten (Stufe 8)
- Sicherheitsdaten (Stufe 10)
- Sensible Finanzdaten (Stufe 6)
- Ungeprüfte personenbezogene Daten (Stufe 3)

### 12.3§ Retrieval-Policy — 7 Bedingungen (alle müssen erfüllt sein)

1. `opt_in_confirmed = 1` für diesen Mandanten
2. Mandant (`company_id`) stimmt überein — kein mandantenübergreifender Abruf
3. Nutzer und Zweck passen zum gespeicherten Fakt
4. `data_class` in der Zielsystem-Matrix (4.2§) für aktuellen Provider erlaubt
5. Provider erlaubt: `ProviderProfile.allowed_data_classes` enthält diese `data_class`
6. `expires_at` in der Zukunft (TTL Standard: 90 Tage)
7. PII-Pre-Check des Facts durch GuardrailSkill bestanden

### 12.4§ Feedback-Loop

| Aktion | Auswirkung |
|---|---|
| Nutzer bewertet: hilfreich | quality_score +0,1 (max 2,0) |
| Nutzer bewertet: nicht hilfreich + optionaler Freitext | quality_score -0,2 (min 0,0) |
| quality_score < 0,3 | Fakt wird nicht mehr abgerufen |
| >= 3 negative Bewertungen desselben Fragetyps | Routing-Anpassungsvorschlag wird generiert |
| Admin sieht Vorschlag im Dashboard | Admin bestätigt manuell; Änderung wird versioniert |

Kein automatisches Finetuning. Kein mandantenübergreifendes Lernen. Kein Training mit PII.

### 12.5§ Rechtsgrundlage für Memory

Hinweis: Art. 6 Abs. 1 lit. a DSGVO (Einwilligung) ist nicht automatisch die richtige Rechtsgrundlage für alle Memory-Anwendungsfälle. Bei Beschäftigten kann Einwilligung aufgrund des Ungleichgewichts im Arbeitsverhältnis problematisch sein (DSGVO Art. 88; nationale Gesetze wie §26 BDSG).

Anforderungen:

- Rechtsgrundlage je Mandant und Use Case mit DSB prüfen — nicht pauschal festlegen.
- Produkt-Opt-in ist nicht automatisch eine DSGVO-Einwilligung.
- Für Memory gilt: Opt-in dokumentieren, Zweck spezifizieren, Widerruf ermöglichen.

---

## 13§ Dokumenten-Workflow

### 13.1§ Schritte (in Reihenfolge — Reihenfolge ist verbindlich)

1. Upload empfangen: Dateityp gegen Whitelist prüfen (PDF; DOCX; XLSX; TXT); Dateigröße prüfen.
2. Malware-Scan soweit technisch möglich durchführen.
3. Multi-Label-Klassifikation: ein Dokument kann gleichzeitig Legal + Confidential + Personal Data sein — alle Klassen gleichzeitig prüfen.
4. PII-Scan + Secret-Scan (pattern-basiert lokal, kein externer LLM).
5. Vorschau generieren: sensible Stellen dem Nutzer anzeigen — nie den Vollinhalt extern schicken.
6. Entscheidung treffen: lokal bearbeiten / anonymisieren / Freigabe nötig / blockieren.
7. Chunking: wenn extern erlaubt, nur relevante Chunks senden — nicht den Volltext.
8. Verarbeitung async starten + Fortschrittsanzeige 0–100% im Frontend.
9. Ergebnis anzeigen: mit Quellenhinweis + Unsicherheitsvermerk.
10. Retention: Aufbewahrungsfrist aus Lineage-Metadaten des Dokuments übernehmen.
11. Löschung: nach Fristablauf automatisch; bei Betroffenenanfrage sofort — inkl. aller abhängigen Memory-Fakten (8.2§).

Wichtig: Dokumenten-Governance muss vor Gate 2 (Pilot mit echten Daten) vollständig implementiert und getestet sein. Datei-Uploads sind oft riskanter als Chat-Eingaben — ein PDF kann mehrere Datenklassen gleichzeitig enthalten.

---

## 14§ Kostenkontrolle

### 14.1§ Vor jeder Ausführung

1. Input-Tokens schätzen (±15% Toleranz ist akzeptabel).
2. Modellklasse wählen: Llama 3.1-8B / Llama 3.3-70B / lokal — nach Komplexität und Budget.
3. Verbleibendes Monatsbudget prüfen.
4. Nutzer informieren wenn Aufgabe viele Tokens benötigt: "Diese Anfrage nutzt voraussichtlich viele Tokens — Weiter?"
5. Hard Limit: bei Überschreitung automatisch auf lokal oder kleines Modell wechseln — kein Fehler, kein Abbruch ohne sichere Alternative.

### 14.2§ Admin-Kostensicht

| Ansicht | Inhalt |
|---|---|
| Echtzeit-Dashboard | Laufende Kosten heute; Provider-Status; offene Freigaben |
| Monatsübersicht | Kosten nach Mandant / Provider / Use Case / Nutzer |
| Prognose | "Bei aktuellem Verbrauch reicht Budget bis [Datum]" |
| Top-Anfragen | 10 teuerste Anfragen der letzten 30 Tage |
| Export | CSV für Buchhaltung und Controlling |

### 14.3§ Kostenbremsen

| Stufe | Trigger | Aktion |
|---|---|---|
| Warnung | 80% des Monatsbudgets erreicht | Admin-Benachrichtigung; Nutzerhinweis |
| Automatischer Fallback | 95% des Monatsbudgets erreicht | Kleines Modell (Llama 3.1-8B) für alle Anfragen |
| Vollstopp extern | 100% des Monatsbudgets erreicht | Keine externen Calls mehr; lokale Weiterarbeit möglich |

Hinweis: Hard Limits sind pro Mandant konfigurierbar. Admin kann Limit in EUR setzen. Änderungen am Limit werden versioniert und im Audit-Log erfasst.

---

## 15§ Betrieb & Go-live Gates

### 15.1§ Gate 1 — Testbetrieb (nur synthetische Daten)

Alle Pflicht-Items müssen abgehakt und dokumentiert sein, bevor der erste Test mit synthetischen Daten startet.

| Pflicht-Item | Nachweis |
|---|---|
| Kill-Switch implementiert | Automatischer Test `external_llm_disabled_blocks_all_routes` bestanden |
| Data Governance Layer (Klassifikation + Lineage) aktiv | Unit-Tests für alle 11 Datenklassen bestanden |
| Secret-Blocker mit Sparse-Audit-Event aktiv | Test: Credential-Input wird blockiert und geloggt |
| Policy-Gateway fail-closed | Test: unbekannte Datenklasse führt zu Blockierung |
| LLM-Orchestrator Interface + Groq-Adapter | Integration-Test mit Test-API-Key bestanden |
| Safe Defaults: ext. KI off; Memory off; kurze Retention | Default-Konfiguration dokumentiert |
| 4 getrennte Log-Typen (Metadaten-Only) | Kein Prompt-Inhalt im Log nachweisbar |
| Datenflussinventar + VVT-Entwurf als Dokument | Dokument vorhanden und versioniert |

### 15.2§ Gate 2 — Pilot mit echten Daten

Gate 1 vollständig bestanden plus folgende zusätzliche Items:

| Pflicht-Item | Nachweis |
|---|---|
| AVV/DPA mit Groq und Railway unterzeichnet | Unterzeichnete Dokumente archiviert |
| Rechtsgrundlagen-Matrix je Pilot-Use-Case | Dokument vom DSB bestätigt |
| Datenschutzhinweise nach DSGVO Art. 13/14 veröffentlicht | URL erreichbar; Inhalt geprüft |
| DSFA-Screening abgeschlossen (HR; Profiling; sensible Daten) | Screening-Ergebnis dokumentiert |
| Redaction aktiv | Test: PII-Input → Platzhalter im Prompt nachweisbar |
| Freigabe-Dialog implementiert (plain German; keine Legalese) | UI-Review durch nicht-technische Person bestanden |
| Onboarding-Assistent fertig | Test mit Pilot-Nutzer abgeschlossen |
| Admin-Minimaldashboard (Freigaben; Kosten; Provider-Status) | Screenshots vorhanden |
| Lösch- und Exporttest bestanden | Protokoll vorhanden |
| Mandantenfilter-Test bestanden | Test: Tenant A sieht keine Daten von Tenant B |
| Cost-Hard-Limits konfiguriert | Pro Pilot-Mandant gesetzt |
| Vector-DB-Governance aktiv (Lineage je Embedding) | Lineage-Abfrage funktioniert |
| Memory-Retrieval-Policy aktiv (7 Bedingungen) | Test: alle 7 Bedingungen werden geprüft |
| Dokumenten-Governance implementiert | Upload-Workflow mit Klassifikation und Chunking getestet |

### 15.3§ Gate 3 — Produktivbetrieb

Gate 2 vollständig bestanden plus folgende zusätzliche Items:

| Pflicht-Item | Nachweis |
|---|---|
| RBAC Login (user / admin / dsb); 2FA vorbereitet | Rollentest bestanden |
| Incident-Prozess dokumentiert und geübt | Übungsprotokoll vorhanden |
| Backup/Restore getestet | Restore-Test-Protokoll vorhanden |
| AI-Literacy-Schulung durchgeführt | Nachweis je Rolle (EU AI Act Art. 4; Pflicht seit 02.02.2025) |
| EU AI Act Art. 50 Kennzeichnungspflicht implementiert | Frist: 02.08.2026; Nachweis vorhanden |
| Cross-Tenant-Isolationstest bestanden | Testprotokoll vorhanden |
| Prompt-Injection-Testset durchgelaufen | Kein kritischer Befund offen |
| Keine kritischen Sicherheits-Findings offen | Sicherheits-Review dokumentiert |
| VVT vollständig und vom DSB bestätigt | Unterschrift des DSB vorhanden |

---

## 16§ Implementierungsreihenfolge

### 16.1§ 20 Schritte

| Schritt | Maßnahme | Gate | Phase |
|---|---|---|---|
| 1 | Datenflussinventar + VVT-Entwurf + Controller/Processor-Modell | Gate 1 | P0 |
| 2 | Data Governance Layer Grundgerüst (Klassifikation + Lineage-Schema) | Gate 1 | P0 |
| 3 | Kill-Switch + automatischer Test | Gate 1 | P0 |
| 4 | Secret-Blocker (Stufe-5-Pattern; Sparse-Audit-Event) | Gate 1 | P0 |
| 5 | LLM-Orchestrator Interface + Groq-Adapter | Gate 1 | P0 |
| 6 | ProviderProfile (inkl. caching_policy) | Gate 1 | P0 |
| 7 | Policy-Gateway fail-closed (empfängt data_classes von DGL) | Gate 1 | P0 |
| 8 | Redaction (PII-Vault; TTL 30 min; thread-safe) | Gate 1 | P0 |
| 9 | 4 getrennte Log-Typen (Metadaten-Only) | Gate 1 | P0 |
| 10 | Fast-Path-Router + Token-Budget-Gateway + Hard-Limits | Gate 1 | P0 |
| 11 | Onboarding-Assistent (5 Fragen; Safe Defaults als Start) | Gate 2 | P1 |
| 12 | Freigabe-Dialog (plain German; Anonymisieren / Lokal / Freigeben) | Gate 2 | P1 |
| 13 | Dokumenten-Governance (Upload-Pipeline; Klassifikation; Chunks) | Gate 2 | P1 |
| 14 | Memory-Governance (opt-in; Retrieval-Policy; TTL 90 Tage) | Gate 2 | P1 |
| 15 | Kosten-Dashboard + Hard-Limit-Enforcement | Gate 2 | P1 |
| 16 | Feedback-Loop (hilfreich/nicht hilfreich; quality_score; Admin-Vorschläge) | Gate 3 | P2 |
| 17 | Streaming (erst wenn Output-Guardrail + Redaction stabil) | Gate 3 | P1 (nach Schritt 8+9) |
| 18 | Admin-Dashboard vollständig (RACI; Kosten; Incident; Provider) | Gate 3 | P2 |
| 19 | RBAC + AI-Literacy + Prompt-Injection-Tests | Gate 3 | P2 |
| 20 | Pilot Gate 2 → Produktiv Gate 3 | — | P3 |

### 16.2§ Wichtigste Reihenfolge-Entscheidung

Streaming (Schritt 17) kommt nach Output-Guardrail (Schritt 9) und Redaction (Schritt 8). Streaming vor diesen beiden Schritten wäre eine schnellere Möglichkeit, Compliance-Fehler für Nutzer sichtbar zu machen — das ist kein akzeptabler Trade-off.

---

## 17§ RACI-Matrix

### 17.1§ Rollen

| Rolle | Beschreibung |
|---|---|
| Nutzer | KMU-Mitarbeiter ohne IT-Kenntnisse — bedient AILIZA täglich |
| Admin Mandant | IT-verantwortliche Person im KMU — konfiguriert Mandant; setzt Limits |
| DSB/Privacy | Datenschutzbeauftragter oder Privacy-Berater — Kontrollinstanz; keine operative Betriebsrolle |
| Betreiber AILIZA | Technisches Team hinter AILIZA — stellt Plattform bereit; führt Änderungen durch |

### 17.2§ RACI-Zuordnung

| Aufgabe | Nutzer | Admin Mandant | DSB/Privacy | Betreiber AILIZA |
|---|---|---|---|---|
| Externe KI aktivieren | — | Entscheidet | Berät; überwacht | Stellt bereit |
| Provider freigeben | — | Beantragt + entscheidet | Prüft; empfiehlt | Dokumentiert |
| Daten löschen / exportieren | Beantragt | Bearbeitet | Überwacht | Unterstützt |
| Incident melden | Meldet | Bewertet | Berät; prüft | Eskaliert |
| Kostenlimit setzen | — | Entscheidet | — | Stellt bereit |
| Freigabe Orange | Je Rolle konfigurierbar | Entscheidet | — | Protokolliert |
| Freigabe Rot | — | Blockiert | Informiert bei Ausnahme | Dokumentiert Ausnahmeprozess |
| Providerwechsel | — | Beantragt | Prüft | Führt durch |
| Subprozessor-Änderung (Groq / Railway) | — | Wird informiert | Prüft; empfiehlt | Informiert + handelt |
| Schulungsnachweis | Nimmt teil | Organisiert | Prüft Nachweis | Stellt Material bereit |

Hinweis: Der DSB ist Kontrollinstanz — er berät, prüft, empfiehlt und überwacht. Er hat keine operative Betriebsrolle und trifft keine Konfigurationsentscheidungen im Tagesgeschäft.

---

*AILIZA Workflow v1.0 · Stand: 2026-06-19 · sicher im Kern · schnell im Alltag · einfach für KMU*
*© 2026 Karola Fromm-Nasreldin — Alle Rechte vorbehalten*
*Hinweis: Dieses Dokument beschreibt DSGVO-orientierte Maßnahmen. Einzelne technische Maßnahmen begründen keine vollständige DSGVO-Konformität. Rechtliche Prüfung durch Datenschutzbeauftragte empfohlen.*
