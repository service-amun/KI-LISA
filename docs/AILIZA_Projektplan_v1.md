# AILIZA — Vollständiger Projektplan
## sicher im Kern · schnell im Alltag · einfach für KMU

**Produkt:** AILIZA — EU-orientierter KI-Assistent für KMU
**Stand:** 2026-06-19 | Version: 1.0
**Verantwortung:** Karola Fromm-Nasreldin (© 2026)
**Kritische Frist:** 02.08.2026 — EU AI Act Art. 50 vollständig anwendbar

---

## 1§ Kernprinzip und Bewertungsregel

### 1.1§ Die 4-Kriterien-Regel

Jedes neue Feature muss alle vier Kriterien bestehen, bevor es aufgenommen wird:

| Kriterium | Frage | Gewicht |
|-----------|-------|---------|
| Nutzerfreundlichkeit | Versteht ein KMU-Nutzer sofort, was passiert und was er tun muss? | 40% |
| Schnelligkeit | Verlangsamt es einfache Aufgaben? Gibt es einen Fast-Path, Cache oder Async-Verarbeitung? | 20% |
| DSGVO | Sind Daten minimiert, zweckgebunden, löschbar und nachvollziehbar? | 30% |
| Rechtssicherheit | Ist klar, wer verantwortlich ist, welcher Anbieter involviert ist und welche Freigabe/Rechtsgrundlage gilt? | 10% |

### 1.2§ Produktlinie

"sicher im Kern · schnell im Alltag · einfach für KMU"

### 1.3§ Prioritätsregel

Datenschutz + Rechtssicherheit zuerst — dann Nutzerführung so einfach wie möglich — dann Performance optimieren.

### 1.4§ DSGVO-Sprachregelung

Niemals "DSGVO-konform" für Einzelmaßnahmen. Immer:
- "DSGVO-orientiert"
- "unterstützt DSGVO-Anforderungen"
- "reduziert DSGVO-Risiken"

---

## 2§ Go-live-Gates

### 2.1§ Gate 1 — Testbetrieb (keine echten Nutzerdaten)

Alle folgenden Punkte müssen erfüllt und dokumentiert sein:

- Kill-Switch aktiv: `AILIZA_EXTERNAL_LLM_ENABLED=false`
- Secret-Blocker implementiert und getestet
- Policy-Gateway fail-closed implementiert
- Safe Defaults aktiv (externe KI aus; Memory aus; Logs ohne Inhalt; kurze Aufbewahrung; Strict Mode für neue Mandanten)
- LLM-Orchestrator Interface definiert und erster Adapter (Groq) implementiert
- Metadata-only-Audit-Log aktiv (kein Inhalt gespeichert)
- ADR-Dokument für Architekturentscheidungen angelegt
- Datenflussinventar erstellt (Dokument)
- Automatisierter Test `external_llm_disabled_blocks_all_routes` besteht
- Data Governance Layer implementiert (zwischen Nutzereingabe und Policy-Gateway)
- 11-Klassen-Klassifikations-Engine implementiert (lokal, pattern-basiert für Credentials/PII/Finance)

### 2.2§ Gate 2 — Pilot mit echten Daten

Alle Gate-1-Anforderungen plus:

- ProviderProfile für jeden genutzten Anbieter vorhanden
- AVV/DPA unterzeichnet für alle Anbieter (Groq, Railway)
- Redaction vor externen Aufrufen implementiert
- Rechtsgrundlagen-Matrix pro Use-Case erstellt
- Datenschutzhinweise nach DSGVO Art. 13/14 fertig und eingeblendet
- VVT-Entwurf (Art. 30) erstellt
- DSFA-Screening durchgeführt
- Mandantenfilter-Test bestanden
- Lösch- und Exporttest bestanden
- Freigabe-Dialog implementiert und getestet
- Onboarding-Flow "Start in 10 Minuten" implementiert
- Admin-Minimaldashboard verfügbar
- Cost-Hard-Limits aktiv
- Vector-DB-Governance implementiert
- Memory-Retrieval-Policy implementiert

### 2.3§ Gate 3 — Produktivbetrieb

Alle Gate-2-Anforderungen plus:

- RBAC (user/admin/dsb) vollständig implementiert
- Vollständige Betroffenenrechte (Art. 17, 20) inkl. Vector-DBs, Backups und Löschprotokoll
- Incident-Prozess dokumentiert und getestet
- Backup/Restore getestet (inkl. Mandantentrennung)
- Hosting-Prüfung EU-Region abgeschlossen und dokumentiert
- AI-Literacy-Nachweis pro Rolle dokumentiert
- Versionierung in Audit-Log (policy_version, prompt_version, provider_profile_version)
- Vollständige Observability (4 Log-Typen, Performance-Budgets, P95 pro Route)
- VVT vom DSB bestätigt

---

## 3§ RACI-Matrix

Legende: V = Verantwortlich (macht es) · M = Mitgewirkt · I = Informiert · P = Prüft/Berät

DSB ist Kontrollrolle (berät, prüft, empfiehlt, überwacht) — NICHT operativ.
Rot = blockiert; keine reguläre Genehmigung möglich.
Sonderfreigaben = dokumentierter Ausnahmeprozess außerhalb des Chat-Flows.

| Aufgabe | Nutzer | Admin Mandant | DSB/Privacy | Betreiber AILIZA |
|---------|--------|--------------|-------------|-----------------|
| Externe KI aktivieren | — | V | P | I |
| Provider freigeben | — | V | P | I |
| Daten löschen/exportieren | I | V | P | V (technisch) |
| Incident melden | V (meldet) | V (eskaliert) | P | V (Reaktion) |
| Kostenlimit setzen | — | V | — | I |
| Freigabe Orange | — | V | P | I |
| Freigabe Rot | — | — | — | Blockiert (Ausnahmeprozess) |
| Providerwechsel | — | M | P | V |
| Subprozessor-Änderung | — | I | P | V |
| Schulungsnachweis | V (absolviert) | V (verwaltet) | P | I |

---

## 4§ Datenklassifikation (11 Stufen)

| Stufe | Klasse | Beispiele (KMU-relevant, inkl. Innenarchitektur) | Extern erlaubt |
|-------|--------|--------------------------------------------------|----------------|
| 0 | Public | Öffentliche Webseiteninhalte; veröffentlichte Preislisten; allgemeine Unternehmensbeschreibungen | Ja |
| 1 | Internal | Interne Memos; Arbeitsprozesse; Meetingnotizen ohne Personenbezug; Grundrisse/Bauzeichnungen ohne Kundenbezug | Mit Freigabe |
| 2 | Confidential | Geschäftsstrategien; Angebote; Lieferantenkonditionen; Projektpläne; Raumkonzepte für Kunden (anonym) | Mit AVV + Admin-Freigabe |
| 3 | Personal Data (DSGVO Art. 4) | Namen; E-Mail-Adressen; Telefonnummern; Kundenadressen; Mitarbeiterstammdaten; IP-Adressen | Nur mit AVV + Rechtsgrundlage |
| 4 | Special Category (DSGVO Art. 9) | Gesundheitsdaten; Religionszugehörigkeit; Gewerkschaftsmitgliedschaft; biometrische Daten; barrierefreie Nutzungsanforderungen von Kunden | Grundsätzlich nicht; Ausnahme dokumentiert |
| 5 | Credentials | Passwörter; API-Keys (gsk_, sk-, tvly_); Tokens; Zugangsdaten; IBAN + Zugangs-PIN kombiniert | Sofort blockieren; niemals speichern |
| 6 | Financial | Rechnungsbeträge; Kontoumsätze; IBAN (allein); Kreditlimits; Budgetdaten; Projektkosten Innenausbau | Nur mit AVV + expliziter Freigabe |
| 7 | HR | Gehaltsabrechnungen; Personalakten; Beurteilungen; Krankheitstage; Bewerbungsunterlagen; Arbeitszeiterfassung | Nur mit AVV + Rechtsgrundlage |
| 8 | Legal | Verträge; Rechtsstreitigkeiten; anwaltliche Korrespondenz; Baugenehmigungen; NDA-Inhalte | Grundsätzlich nicht; anwaltliche Prüfung |
| 9 | Intellectual Property | Designentwürfe; unveröffentlichte Grundrisse/Bauzeichnungen; Kalkulationsformeln; proprietäre Workflows; Kunststücke/Moodboards | Grundsätzlich nicht ohne explizite Freigabe |
| 10 | Security Sensitive | Sicherheitslücken; Penetrationstest-Ergebnisse; Notfallpläne; Zugangsschemata zu Systemen | Niemals |

---

## 5§ Datenfluss-Matrix

| Datenklasse | Lokal | Groq | OpenAI | CRM | Memory |
|-------------|-------|------|--------|-----|--------|
| Public (0) | Ja | Ja | Ja | Ja | Ja |
| Internal (1) | Ja | Mit Freigabe | Mit Freigabe | Ja | Mit Freigabe |
| Confidential (2) | Ja | AVV + Admin | AVV + Admin | AVV | AVV + Admin |
| Personal Data (3) | Ja | AVV + Rechtsgrundlage | AVV + Rechtsgrundlage | AVV | Nein (Standardfall) |
| Special Category (4) | Ja | Nein | Nein | Nein | Nein |
| Credentials (5) | Blockiert | Blockiert | Blockiert | Blockiert | Blockiert |
| Financial (6) | Ja | AVV + Freigabe | AVV + Freigabe | AVV | Nein |
| HR (7) | Ja | AVV + Rechtsgrundlage | AVV + Rechtsgrundlage | AVV | Nein |
| Legal (8) | Ja | Nein | Nein | Nein | Nein |
| IP (9) | Ja | Explizite Freigabe | Explizite Freigabe | Nein | Nein |
| Security Sensitive (10) | Nur intern | Nein | Nein | Nein | Nein |

---

## 6§ Schnelligkeit — Vollständige Performance-Architektur

### 6.1§ Route-Performance-Ziele

| Route | Modell | Ziel-Latenz | Verarbeitung |
|-------|--------|-------------|--------------|
| Simple | Lokal (kein LLM) | < 200 ms | Synchron; Fast-Path-Router; kein externer Datenabfluss; interne Datenschutzregeln gelten weiter |
| Standard | Llama 8B via Groq | < 3 s | Synchron + Streaming |
| Komplex | Llama 70B via Groq | < 10 s | Streaming mit Satz-Pufferung bei Compliance/HR/Legal/Finance/PII |
| Dokument | Kleines Modell + Chunking | < 30 s | Async + Fortschrittsanzeige 0–100 %; intermediate summarization |
| Riskant | Llama 70B + Output-Check + Freigabe | Variabel | Freigabe-Dialog vor Ausführung; klare Statusanzeige; sichere Alternative anbieten |

### 6.2§ Performance-Maßnahmen

| Maßnahme | Wirkung | Aufwand |
|----------|---------|---------|
| Fast-Path-Router (Regex/Dictionary, 0 Token) | < 200 ms; spart ~30 % aller Anfragen | Niedrig |
| Token-Budget-Gateway vor Routing | Verhindert unnötige 70B-Aufrufe; ~40 % Kostenersparnis | Niedrig |
| Streaming via `fetch()` ReadableStream (kein `EventSource` — GET-only) | Gefühlte Latenz sinkt deutlich | Mittel |
| Async Dokumentenverarbeitung + Fortschritts-Endpoint | Kein Frontend-Freeze bei großen Dateien | Mittel |
| Datenklassifikation lokal/pattern-basiert — **kein externer LLM** für Klassifikation | Verhindert 500–2000 ms Zusatzlatenz je Anfrage | Mittel |
| Connection Pooling: SQLite `check_same_thread=False`; `httpx.AsyncClient` global | Reduziert Verbindungs-Overhead bei Last | Niedrig |
| Compliance-Kontext Lazy-Load (nur bei COMPLEX/CRITICAL Route) | Spart ~50 ms bei Simple/Standard | Niedrig |
| Hard Timeouts: Groq 90 s; danach deutsche Fehlermeldung ohne Stack-Trace | Keine hängenden Requests | Niedrig |
| Retry nur bei HTTP 408/429/503: Exponential Backoff (Base 100 ms, Max 32 s, ±50 % Jitter) | Kein Thundering Herd; stabile Erholung nach Groq-Engpässen | Niedrig |
| `asyncio.gather()` für parallele Tool-Ausführung (Web-Suche + Fetch gleichzeitig) | Multi-Tool-Latenz −40–60 % | Mittel |
| Preloading häufiger Compliance-Muster beim App-Start | Kein Kalt-Start bei erster Compliance-Anfrage | Niedrig |

### 6.3§ Performance-Monitoring

| Metrik | Schwellwert | Aktion |
|--------|-------------|--------|
| P50-Latenz je Route | Zielwert aus 6.1§ | Dashboard-Anzeige |
| P95-Latenz je Route | 2× Zielwert | Slow-Query-Log-Eintrag |
| P99-Latenz je Route | 5× Zielwert | Alert; manuelle Prüfung |
| Fehlerquote | > 1 % in 60 s | Circuit Breaker öffnet; Fallback-Nachricht |
| Provider-Verfügbarkeit | Fehler beim Start-Check | Dashboard: Provider-Status rot |

Slow-Query-Log: jede Anfrage > 5 s → Route, Modell, Tokens, Timestamp in `data/slow_queries.log`. Metriken in `data/metrics.db` (SQLite) — kein externer Monitoring-Dienst für MVP.

---

## 7§ Phase 0 — Sicherheit, Architektur, Data Governance (Woche 1)

Reihenfolge ist verbindlich. Kein Code außerhalb dieser Phase wird geschrieben, bevor alle P0-Items bestehen.

| ID | Beschreibung | 4-Kriterien-Note | Risiko/Aufwand |
|----|--------------|-----------------|----------------|
| 0I | Datenflussinventar + Datenkatalog + VVT-Entwurf (Dokument, kein Code): Alle Datenflüsse von Nutzereingabe bis LLM-Antwort und Speicherung erfassen; Datenarten, Zwecke, Empfänger, Speicherfristen dokumentieren; Grundlage für Gate-2-VVT und DSFA-Screening | Nutzer: nicht direkt sichtbar · Schnelligkeit: kein Einfluss · DSGVO Art. 30: Pflichtdokument · Rechtssicherheit: Basis aller Folgeentscheidungen | Risiko hoch wenn fehlend; Aufwand mittel |
| 0L | Controller/Processor-Modell dokumentieren: Kunde = Controller; AILIZA = Processor; Groq = Sub-Processor; Railway = Sub-Processor; AVV-Kette definieren; Haftungsabgrenzung festlegen | Nutzer: transparent wer verantwortlich · Schnelligkeit: kein Einfluss · DSGVO Art. 28: Pflicht · Rechtssicherheit: Haftungsklarheit | Risiko hoch wenn fehlend; Aufwand niedrig |
| ADR | Architecture Decision Records anlegen: Format {id, datum, titel, kontext, entscheidung, alternativen, konsequenzen}; mindestens ADR-001 für LLM-Anbieterauswahl; ADR-002 für Datenhaltung SQLite; jede signifikante Architekturentscheidung dokumentiert | Nutzer: nicht sichtbar · Schnelligkeit: kein Einfluss · DSGVO: Nachvollziehbarkeit · Rechtssicherheit: Entscheidungsdokumentation | Risiko mittel; Aufwand niedrig |
| 0M | Data Governance Layer implementieren: sitzt zwischen Nutzereingabe und Policy-Gateway; Aufgaben: 11-Klassen-Klassifikation; Data Lineage Metadata; Datenfluss-Matrix-Prüfung; Memory-Retrieval-Policy; Vector-DB-Governance; verhindert indirekten Datenleck durch Memory | Nutzer: transparent · Fast-Path unberührt · DSGVO Art. 5, 25: Privacy by Design · Rechtssicherheit: Kontrollpunkt vor jeder Verarbeitung | Risiko sehr hoch wenn fehlend; Aufwand hoch |
| 0P | 11-Klassen-Klassifikations-Engine implementieren: pattern-basiert für Credentials (Stufe 5)/PII (Stufe 3)/Financial (Stufe 6) — LOKAL, kein externer LLM-Aufruf für Klassifikation; LLM-gestützt nur für Confidential/Legal/IP nach Gate 2; Regex-Bibliothek für DE: IBAN, Steuer-ID, Sozialversicherung, Personalausweis, Telefon DE | Nutzer: unsichtbar · Schnelligkeit: lokal < 10 ms · DSGVO Art. 5(1)(c): Datensparsamkeit · Rechtssicherheit: Basis aller Freigabeentscheidungen | Risiko sehr hoch wenn fehlend; Aufwand mittel |
| 0F | Kill-Switch implementieren: Umgebungsvariable `AILIZA_EXTERNAL_LLM_ENABLED=false`; wenn false blockiert Policy-Gateway alle externen LLM-Aufrufe; automatisierter Test `external_llm_disabled_blocks_all_routes` muss bestehen; fail-closed | Nutzer: eindeutige Statusanzeige · Schnelligkeit: Fast-Path unberührt · DSGVO Art. 25: Safe Default · Rechtssicherheit: Betreiber kann jederzeit abschalten | Risiko hoch; Aufwand niedrig |
| 0A | Secret-Blocker implementieren: Credentials-Pattern (Stufe 5) erkennt gsk\_, sk-ant-, tvly\_, password=, token=, api\_key=; Aktion: sofort blockieren, niemals speichern, niemals an externen LLM senden; Sparse-Audit-Event: {event\_type: secret\_detected, action: blocked, data\_class: credential, content\_stored: false}; kein Inhalt im Log | Nutzer: klare Fehlermeldung ohne technische Details · Schnelligkeit: lokal < 5 ms · DSGVO Art. 5: Datensparsamkeit · Rechtssicherheit: Verhindert Credential-Leak | Risiko kritisch; Aufwand niedrig |
| 0N | LLM-Orchestrator Interface definieren: Methoden generate(), stream(), estimate\_cost(), classify\_capability(), count\_tokens(), redact\_or\_prepare(); Eigenschaften supports\_streaming, supports\_json\_mode, supports\_eu\_region, max\_context\_tokens, data\_residency, provider\_terms\_version; Groq als erster Adapter; Fallback-Kette konfigurierbar; Provider austauschbar ohne Architkturänderung | Nutzer: transparent bei Providerwechsel · Schnelligkeit: Fallback ohne Nutzerunterbrechung · DSGVO: Providerwechsel ohne Datenverlust · Rechtssicherheit: Klare Schnittstellendefinition | Risiko hoch; Aufwand mittel |
| 0B | ProviderProfile definieren: Felder provider, model, region, avv\_dpa\_status (pending/signed/expired), logging (none/metadata/full), training\_use (no/opt-out/yes), caching\_policy (none/provider-side/documented), data\_residency (EU/US/global), allowed\_data\_classes (Liste Stufen), retention (Stunden), provider\_terms\_version; Provider-Caching hier dokumentiert — kein blindes Vertrauen in "Groq regelt Caching"; Änderung löst Cache-Invalidierung aus | Nutzer: Providerstatus sichtbar im Dashboard · Schnelligkeit: Caching-Policy beeinflusst Latenz · DSGVO Art. 28: AVV-Status zentral · Rechtssicherheit: Rechtsgrundlage pro Provider | Risiko hoch; Aufwand mittel |
| 0C | Policy-Gateway implementieren: fail-closed (bei Fehler blockiert); empfängt data\_class von Data Governance Layer in PolicyContext; prüft: Kill-Switch-Status; ProviderProfile.allowed\_data\_classes; Rechtsgrundlage vorhanden; AVV-Status; Freigabe-Status; Ergebnis: erlaubt/warnen/orange/blockiert | Nutzer: klare Rückmeldung · Schnelligkeit: < 20 ms lokal · DSGVO Art. 5, 6: Zweckbindung und Rechtsgrundlage · Rechtssicherheit: Zentraler Kontrollpunkt | Risiko sehr hoch wenn fehlend; Aufwand mittel |
| 0E | Redaction vor externem Aufruf implementieren: Erkennte PII (Stufe 3) und Credentials (Stufe 5) werden durch Platzhalter ersetzt bevor Daten an externen LLM gehen; PII-Vault speichert Mapping lokal; Antwort wird re-substituted; TTL 30 Minuten; Thread-safe Cleanup | Nutzer: transparente Warnung dass Daten anonymisiert wurden · Schnelligkeit: + ~50 ms · DSGVO Art. 5(1)(c): Datensparsamkeit · Rechtssicherheit: Technische Maßnahme dokumentierbar | Risiko hoch; Aufwand mittel |
| 0G | Safe Defaults setzen: Neue Mandanten starten mit Strict Mode; externe KI deaktiviert; Memory deaktiviert; Logs ohne Inhalt; Audit-Retention 90 Tage; kein Semantic Cache ohne explizite Aktivierung; Einstellungen müssen aktiv geändert werden, nicht aktiv gesichert | Nutzer: sicherer Start ohne Konfigurationsaufwand · Schnelligkeit: Fast-Path immer verfügbar · DSGVO Art. 25: Privacy by Design · Rechtssicherheit: Haftung beim Betreiber bis Mandant explizit freigibt | Risiko mittel; Aufwand niedrig |
| Obs0 | 4 separate Log-Typen implementieren und NIEMALS mischen: Audit-Log (Entscheidungen/Freigaben; kein Inhalt); Security-Log (Missbrauch/Secrets/Incidents; kein Inhalt); Performance-Log (Latenz/Fehler/Tokens ohne Inhalt); Cost-Log (Tokens/Provider/Mandant/Use-Case); Jeder Log-Typ hat eigene Retention-Policy und Zugriffsrechte | Nutzer: nicht sichtbar · Schnelligkeit: async Logging · DSGVO Art. 30, 32: Audit-Trail und TOMs · Rechtssicherheit: Beweissicherung bei Incidents | Risiko hoch wenn gemischt; Aufwand mittel |
| 1W | Data Lineage Metadata implementieren: Jedes Datenobjekt trägt {data\_class, source, tenant\_id, created\_at, retention\_days, external\_allowed}; Source-Enum: user\_input / pdf\_upload / crm / calendar / web\_search / memory / tool; Grundlage für Löschkonzept und Betroffenenrechte | Nutzer: ermöglicht vollständige Löschung auf Anfrage · Schnelligkeit: Overhead < 5 ms · DSGVO Art. 5(1)(e): Speicherbegrenzung · Rechtssicherheit: Nachvollziehbarkeit Datenherkunft | Risiko mittel; Aufwand mittel |
| 0D | Textkorrektur-Pass durchführen: "orientiert" statt "konform"; Art. 50 (nicht Art. 52) für Transparenzpflicht KI-Interaktionen; Art. 13 nicht für allgemeine Freigaben verwenden; "Nutzerbestätigung"/"Admin-Freigabe" statt "Einwilligung" wo zutreffend; Alle Dokumente und UI-Texte prüfen | Nutzer: rechtssicherer Sprachgebrauch · Schnelligkeit: kein Einfluss · DSGVO: Korrekte Terminologie · Rechtssicherheit: Verhindert falsche Rechtsversprechen | Risiko mittel; Aufwand niedrig |
| 0H | RACI-Dokument erstellen und kommunizieren: Rollen definieren; Verantwortlichkeiten zuweisen; an Admin-Mandant und DSB kommunizieren; als Onboarding-Bestandteil | Nutzer: Klarheit über Verantwortung · Schnelligkeit: kein Einfluss · DSGVO Art. 24: Rechenschaftspflicht · Rechtssicherheit: Haftungsklarheit | Risiko mittel; Aufwand niedrig |

---

## 8§ Phase 0 Parallel (Woche 1)

Diese Items können parallel zu Phase 0 entwickelt werden, da sie keine Abhängigkeiten von 0M/0C haben.

| ID | Beschreibung | 4-Kriterien-Note | Risiko/Aufwand |
|----|--------------|-----------------|----------------|
| 1F | Fast-Path-Router implementieren: lokale Antworten für Begrüßungen/Datum-Uhrzeit/einfache Berechnungen/Hilfe-Anfragen; Regex + Keyword-Matching; kein externer Datenabfluss; interne Datenschutzregeln gelten weiter; Ergebnis < 200 ms; Kennzeichnung "lokal verarbeitet" in Antwort | Nutzer: sofortige Antwort bei einfachen Fragen · Schnelligkeit: < 200 ms · DSGVO Art. 5(1)(c): kein unnötiger Datentransfer · Rechtssicherheit: kein Provider involviert | Risiko niedrig; Aufwand niedrig |
| 1E | Token-Budget-Gateway + Hard-Cost-Limits implementieren: max\_input\_tokens; reserved\_output\_tokens; safety\_margin pro Route; Hard-Cost-Limit in Euro pro Monat pro Mandant; bei Erreichen des Limits: nur lokale Modelle und Fast-Path; keine Fehlermeldung sondern "Nur einfache Anfragen verfügbar"; Cost-Log Eintrag; Admin wird informiert | Nutzer: keine Überraschungskosten; transparente Statusanzeige · Schnelligkeit: Budget-Check < 5 ms · DSGVO Art. 5: Kostenkontrolle reduziert übermäßige Verarbeitung · Rechtssicherheit: Betreiber und Mandant vor unerwarteten Kosten geschützt | Risiko mittel; Aufwand mittel |

---

## 9§ Phase 1 — UX, Transparenz, Datenschutz (Woche 2–4)

| ID | Beschreibung | 4-Kriterien-Note | Risiko/Aufwand |
|----|--------------|-----------------|----------------|
| 0J | Rechtsgrundlagen-Matrix erstellen (Gate-2-Pflicht): Pro Use-Case: Rechtsgrundlage (Art. 6 DSGVO); betroffene Datenarten; involvierte Provider; Aufbewahrungsdauer; Löschkonzept; Tabelle in Dokumentation und als Grundlage für VVT | Nutzer: Transparenz pro Use-Case · Schnelligkeit: kein Einfluss · DSGVO Art. 6, 30: Pflichtdokument · Rechtssicherheit: Rechtsgrundlage explizit pro Use-Case | Risiko hoch wenn fehlend; Aufwand mittel |
| 0K | DSFA-Screening durchführen (Gate-2-Pflicht): WP-248-Kriterien prüfen; bei mindestens 2 Kriterien: vollständige DPIA nach Art. 35; Ergebnis dokumentieren; DSB einbinden; Entscheidung: keine DPIA nötig / DPIA nötig / DPIA abgeschlossen | Nutzer: schützt vor Compliance-Risiko · Schnelligkeit: kein Einfluss · DSGVO Art. 35: Pflicht bei hohem Risiko · Rechtssicherheit: DSB-Bestätigung | Risiko hoch; Aufwand mittel |
| 1T | Tool-Manifest implementieren: Jedes Tool deklariert name, purpose, target\_system, data\_classes (Liste Stufen), permissions (read/write/send/delete/external), approval\_required (boolean), audit\_fields (Liste); manifest wird vor Ausführung geprüft; undeklarierte Tools können nicht ausgeführt werden | Nutzer: "Welche Tools hat AILIZA?" sichtbar im Dashboard · Schnelligkeit: Manifest-Check < 10 ms · DSGVO Art. 5: Zweckbindung pro Tool · Rechtssicherheit: Klare Erlaubnisstruktur | Risiko mittel; Aufwand mittel |
| 1U | Memory-Retrieval-Policy implementieren: Memory-Fact → data\_class prüfen → Datenfluss-Matrix prüfen → Provider-Check → Freigabe-Check → erst dann in Prompt einfügen; verhindert indirekten Datenleck durch Memory; Retrieval-Entscheidung im Audit-Log | Nutzer: Memory-Nutzung transparent · Schnelligkeit: Policy-Check < 20 ms · DSGVO Art. 5: Zweckbindung für gespeicherte Fakten · Rechtssicherheit: Kein unbemerkter Datentransfer via Memory | Risiko hoch; Aufwand mittel |
| 1A | Streaming implementieren: fetch() ReadableStream für POST (nicht native EventSource die nur GET unterstützt); Output-Sicherheitsmodell: Green/Simple → Token-Streaming direkt; Compliance/HR/Legal/Finance/PII → Sentence-Buffering mit check\_output() vor Ausgabe; Policy-Verletzung → Stream abbrechen + sichere Ersatzmeldung anzeigen | Nutzer: sichtbarer Schreibfortschritt bei langen Antworten · Schnelligkeit: First-Token < 1,5 s · DSGVO: Output-Check vor Anzeige · Rechtssicherheit: Kein Policy-verletzender Inhalt erreicht UI | Risiko mittel; Aufwand mittel |
| 1B | PII-Vault mit TTL implementieren: Jeder Platzhalter-Eintrag trägt expires\_at (Standard: 30 Minuten); Thread-safe Cleanup bei jedem Chat-Request; nach Ablauf automatische Löschung aus RAM; Löschung im Security-Log ohne Inhalt; kein Persist auf Disk | Nutzer: automatische Bereinigung ohne Nutzeraktion · Schnelligkeit: Cleanup < 5 ms async · DSGVO Art. 5(1)(e): Speicherbegrenzung · Rechtssicherheit: Nachweisbare automatische Löschung | Risiko mittel; Aufwand niedrig |
| 1C | IP-Hash implementieren: HMAC + täglich rotierender Salt; nur speichern wenn notwendig; kurze Retention (7 Tage); Zweck: Sicherheit/Missbrauchserkennung; Zugriff: nur Admin; kein Rückschluss auf Person möglich ohne aktuellen Salt | Nutzer: nicht sichtbar · Schnelligkeit: < 2 ms · DSGVO Art. 4(1), 25: Pseudonymisierung · Rechtssicherheit: Missbrauchserkennung ohne Personenzuordnung | Risiko mittel; Aufwand niedrig |
| 1D | Output-Guardrail erweitern: PII-Erkennung in Ausgabe; unzulässige Rechtsberatung (Formulierungen wie "Sie müssen rechtlich..." ohne Prüfhinweis); HR-/Kredit-/Finanzentscheidungen ("Sie sollten entlassen..."); diskriminierende Aussagen; erfundene Quellen (Halluzinationen mit Quellenangabe); riskante Handlungsaufforderungen; fehlender Prüfhinweis bei Compliance-Themen; bei Erkennung: Antwort ersetzen oder Hinweis anfügen | Nutzer: schützt vor Haftungsrisiken · Schnelligkeit: sentence-buffered; + ~200 ms · DSGVO Art. 5: keine unbeabsichtigte Weitergabe · Rechtssicherheit: Verhindert unzulässige automatisierte Entscheidungen | Risiko hoch; Aufwand mittel |
| 1G | Risikoampel Grün/Gelb/Orange/Rot implementieren: Textlabel immer anzeigen (nicht nur Farbe); WCAG 2.1 AA Kontrast; Bedeutung: Grün = lokal/sicher; Gelb = Warnung/Hinweis; Orange = Admin-Freigabe erforderlich; Rot = blockiert; Ampel sichtbar in jeder Antwort die nicht Grün ist | Nutzer: sofort erkennbar was passiert · Schnelligkeit: kein Einfluss · DSGVO Art. 13: Transparenz · Rechtssicherheit: Klarer Handlungsbedarf erkennbar | Risiko mittel; Aufwand niedrig |
| 1H | Fehlermeldungen kartieren: alle Exceptions werden an API-Boundary gemappt; Nutzer sieht immer plain-German-Text; kein Stack-Trace; kein interner Pfad; "Warum blockiert?"-Erklärung verfügbar (einfaches Deutsch); technische Details nur in Security-Log für Admin | Nutzer: verständliche Fehlermeldungen · Schnelligkeit: kein Einfluss · DSGVO Art. 5: keine unbeabsichtigte Systeminfo-Weitergabe · Rechtssicherheit: Keine technische Offenlegung | Risiko mittel; Aufwand niedrig |
| 1I | Mandanten-DB-Modelle implementieren: company\_id; user\_id; policy\_profile\_id; provider\_profile\_id; retention\_profile\_id; Mandantenfilter als Middleware vor jeder DB-Abfrage; Mandantenfilter-Test muss vor Gate 2 bestehen; kein Tenant kann Daten anderer Tenants sehen | Nutzer: Datentrennung garantiert · Schnelligkeit: Overhead < 5 ms · DSGVO Art. 25, 32: Technische Maßnahme · Rechtssicherheit: Mandanten-Isolation als Vertragsbedingung | Risiko hoch; Aufwand mittel |
| 1J | Dynamische Token-Budgets implementieren: max\_input\_tokens; reserved\_output\_tokens; safety\_margin pro Route (Simple/Standard/Komplex/Dokument/Riskant); Dokumente: Chunking + intermediate Summarization wenn Dokument > max\_input\_tokens; Fortschrittsanzeige bei Chunk-Verarbeitung | Nutzer: Fortschrittsanzeige bei langen Dokumenten · Schnelligkeit: Chunking ermöglicht Dokumente > Kontextlimit · DSGVO: Minimiert Datenmenge pro Aufruf · Rechtssicherheit: Kostenkontrolle durch Budget | Risiko mittel; Aufwand mittel |
| 1K | Freigabe-Bundles implementieren: gleicher Zweck + gleiche Datenklasse + gleicher Provider + kurze Dauer (15–60 Minuten); risikobasiert: Grün = nie Freigabe nötig; Gelb = Hinweis; Orange = Admin-Freigabe; Rot = blockiert (Ausnahme nur mit dokumentiertem Prozess außerhalb Chat-Flow); "Immer anonymisieren" als Standard-Vorschlag; Freigabe-Verlauf im Admin-Dashboard sichtbar; Freigabe-Dialog in einfachem Deutsch | Nutzer: einmalige Freigabe für ähnliche Aktionen · Schnelligkeit: Bundle reduziert Freigabe-Unterbrechungen · DSGVO Art. 6: Freigabe = keine Einwilligung sondern Nutzerbestätigung · Rechtssicherheit: Dokumentierter Freigabeprozess | Risiko mittel; Aufwand mittel |
| 1L | Quellen- und Unsicherheitsmodus implementieren: AILIZA kennzeichnet: Fakten (mit Quelle+Datum); Annahmen; offene Punkte; "keine Rechtsberatung"-Hinweis bei Rechtsthemen; Quellenangabe bei Web-Suche immer; Halluzinations-Risiko durch Output-Guardrail (1D) reduziert | Nutzer: Vertrauensgrundlage für KMU-Entscheidungen · Schnelligkeit: kein Einfluss · DSGVO Art. 13: Transparenz der Entscheidungsgrundlage · Rechtssicherheit: Haftungsschutz durch Prüfhinweise | Risiko mittel; Aufwand niedrig |
| 1M | Freigabe-Dialog implementieren: plain-German-Dialog; Fragen: "Was wird verarbeitet?"; "Wohin werden die Daten gesendet?"; "Wie lange?"; Buttons: [Anonymisieren] [Lokal bearbeiten] [Abbrechen] [Freigeben]; sichere Alternative immer anbieten; "Nutzerbestätigung" verwenden, nicht "Einwilligung"; Freigabe läuft ab nach Bundle-Dauer | Nutzer: versteht genau was passiert · Schnelligkeit: Dialog nur bei Orange; Fast-Path unberührt · DSGVO Art. 13: Informierte Entscheidung · Rechtssicherheit: Dokumentierte Nutzerbestätigung | Risiko mittel; Aufwand mittel |
| 1N | Kosten- und Antwortmodus implementieren: Modi Schnell/Gründlich/Datensparsam wählbar; jede Antwort zeigt: "lokal verarbeitet" / "externe KI verwendet" / "keine Speicherung" / "Freigabe aktiv"; Hard-Cost-Limit: bei Erreichen nur lokale/kleine Modelle; keine Fehlermeldung; "Zur Zeit nur einfache Anfragen verfügbar" | Nutzer: Kontrolle über Kosten und Datensparsamkeit · Schnelligkeit: Datensparsam-Modus oft schneller · DSGVO Art. 5(1)(c): Datensparsamkeit wählbar · Rechtssicherheit: Transparente Verarbeitungsanzeige | Risiko niedrig; Aufwand mittel |
| 1O | Onboarding "Start in 10 Minuten" implementieren: 5 Fragen zum Anwendungsfall; automatischer Profil-Vorschlag; "Externe KI aus" als sicherer Start; Beispiel-Workflows (E-Mail verfassen; Zusammenfassung; Recherche; Datenschutzprüfung); Admin-Checkliste; Konfiguration importierbar/exportierbar | Nutzer: sofort einsatzbereit ohne IT-Kenntnisse · Schnelligkeit: Profil vermeidet manuelle Konfiguration · DSGVO Art. 13: Datenschutzhinweis in Onboarding · Rechtssicherheit: Rechtsgrundlage im Onboarding klären | Risiko niedrig; Aufwand mittel |
| 1P | Verarbeitungsstatus pro Antwort anzeigen: "lokal verarbeitet" / "extern verarbeitet (Provider: X)" / "mit Freigabe" / "ohne Speicherung"; Provider-Status sichtbar: aktiv/gesperrt/ungeprüft; Änderung des Provider-Status löst Nutzerhinweis aus | Nutzer: immer transparent was passiert · Schnelligkeit: kein Einfluss · DSGVO Art. 13: Transparenz · Rechtssicherheit: Provider-Status als Risikoindikator | Risiko niedrig; Aufwand niedrig |
| 1Q | Barrierefreiheit implementieren: Tastaturnavigation; aria-label/role für alle interaktiven Elemente; WCAG 2.1 AA Kontrast (mindestens 4,5:1); Mobile Input über Tastatur (viewport-meta, scroll-into-view); keine farb-alleinige Risikokommunikation (immer Textlabel + Icon) | Nutzer: zugänglich für alle KMU-Mitarbeiter · Schnelligkeit: kein Einfluss · DSGVO: nicht direkt · Rechtssicherheit: reduziert Barrierefreiheitspflicht-Risiken | Risiko niedrig; Aufwand mittel |
| 1R | Modulare Service-Grenzen definieren: Policy/Provider/Document/Memory/Audit/Cost/Admin als Module im Monolith; Interfaces für zukünftige Microservice-Extraktion definiert; keine zirkulären Abhängigkeiten; jedes Modul hat eigene DB-Tabellen und Logs | Nutzer: nicht sichtbar · Schnelligkeit: Monolith behält Performance · DSGVO Art. 25: Privacy by Design in Architektur · Rechtssicherheit: Klare Modulverantwortung | Risiko mittel; Aufwand mittel |
| 1S | Performance-Budgets definieren: First-Token < 1,5 s extern; Fast-Path < 200 ms; P95 pro Route (Simple/Standard/Komplex/Dokument/Riskant); Timeouts pro Provider; bei Timeout: Fallback-Kette oder "Anfrage dauert länger als erwartet"-Meldung; Monitoring für P95-Verletzungen | Nutzer: verlässliche Antwortzeiten · Schnelligkeit: Monitoring erkennt Verschlechterungen früh · DSGVO: kein Einfluss · Rechtssicherheit: SLA-Grundlage | Risiko mittel; Aufwand mittel |
| 1V | Versionierung in Audit-Log implementieren: policy\_version; prompt\_version; provider\_profile\_version bei jedem Audit-Log-Eintrag; ermöglicht Nachvollziehbarkeit bei Incidents ("welche Policy war aktiv?") | Nutzer: nicht sichtbar · Schnelligkeit: kein Einfluss · DSGVO Art. 30: Nachvollziehbarkeit · Rechtssicherheit: Beweissicherung bei Incidents | Risiko mittel; Aufwand niedrig |
| DashMin | Admin-Minimaldashboard implementieren (Gate-2-Pflicht): offene Freigaben; Provider-Status (aktiv/gesperrt/ungeprüft); aktuelle Kosten (Monat); ausstehende Löschanfragen; einfache Navigation; Mobile-tauglich | Nutzer (Admin): Überblick ohne IT-Kenntnisse · Schnelligkeit: Dashboard-Load < 2 s · DSGVO Art. 17: Löschanfragen sichtbar · Rechtssicherheit: Admin-Kontrollpflicht erfüllt | Risiko mittel; Aufwand mittel |
| 2H | Abuse-/Rate-Limits implementieren: pro Nutzer und Mandant; Anfragen-Limit pro Minute/Stunde; Datei- und Prompt-Größenlimits; Kosten-Explosion-Schutz; Hard-Stop bei Limit-Erreichen; Security-Log-Eintrag; Admin-Benachrichtigung bei wiederholtem Missbrauch | Nutzer: transparent über Limit-Erreichen · Schnelligkeit: Limits schützen alle Nutzer · DSGVO Art. 32: Sicherheitsmaßnahme · Rechtssicherheit: Verhindert Kosten-Haftung | Risiko mittel; Aufwand niedrig |

---

## 10§ Phase 2 — Qualität, Zugang, Governance (Monat 1–2)

| ID | Beschreibung | 4-Kriterien-Note | Risiko/Aufwand |
|----|--------------|-----------------|----------------|
| 2A | Login/RBAC implementieren: Rollen user/admin/dsb; OAuth/OIDC Vorbereitung; 2FA-Ready für Admin und DSB; Session-Token kryptografisch zufällig (128 Bit); Session-Rotation bei Rollen-Wechsel; RBAC-Check vor jeder sensitiven Operation | Nutzer: einfacher Login · Schnelligkeit: Token-Prüfung < 5 ms · DSGVO Art. 32: Zugangskontrolle · Rechtssicherheit: Rollenbasierte Haftungsklarheit | Risiko hoch; Aufwand mittel |
| 2B | Orange-Tier Guardrail implementieren: vollständige Ampel grün/gelb/orange/rot; Orange = Admin-Freigabe erforderlich vor Ausführung; Rot = blockiert (Ausnahme nur mit dokumentiertem Prozess außerhalb Chat-Flow, nicht im Chat lösbar); Freigabe-Anfrage an Admin gesendet; Status für Nutzer: "Anfrage wartet auf Admin-Freigabe" | Nutzer: klarer Prozess bei Orange · Schnelligkeit: Freigabe-Weg klar · DSGVO Art. 6, 24: Rechtsgrundlage für risikoreiche Verarbeitung · Rechtssicherheit: Dokumentierte Freigabekette | Risiko mittel; Aufwand mittel |
| 2C | Use-Case-Katalog als YAML implementieren: jeder Use-Case mit Status BLOCKIERT/FREIGABE\_NÖTIG/ADMIN\_ONLY; Kategorien: Rechtsberatung (BLOCKIERT); Kreditentscheidung (BLOCKIERT); HR-Scoring (BLOCKIERT); externe E-Mail mit PII (FREIGABE\_NÖTIG); Vertragsanalyse (ADMIN\_ONLY); katalogisierte Use-Cases durch Policy-Gateway automatisch geroutet | Nutzer: Use-Case-Katalog im Dashboard sichtbar · Schnelligkeit: Katalog-Lookup < 5 ms · DSGVO Art. 5: Zweckbindung · Rechtssicherheit: Explizite Use-Case-Zulassung | Risiko mittel; Aufwand niedrig |
| 2D | Audit-Log-Retention + Löschprotokoll implementieren: Standard-Cleanup nach 365 Tagen (DSGVO Art. 5(1)(e) + Art. 25 + Art. 32); Löschprotokoll-Schema: {user\_id, deleted\_at, systems:[sessions, memory, vector\_db, audit\_log\_anonymized], data\_classes, success}; Audit-Log nach Löschung anonymisiert (nicht komplett gelöscht für Nachvollziehbarkeit) | Nutzer: Löschbestätigung sichtbar · Schnelligkeit: async Cleanup · DSGVO Art. 5(1)(e), 17: Speicherbegrenzung und Löschrecht · Rechtssicherheit: Löschnachweis | Risiko mittel; Aufwand mittel |
| 2E | Qualitätssicherung implementieren: Goldset mit 30–50 Anfragen + Erwartungsantworten; automatische Regression bei jedem Release; Kriterien: korrekt/kurz/hilfreich/risikobewusst/keine unzulässige Rechtsberatung; Nutzerfeedback im Chat (Daumen rauf/runter + optional Freitext); Prompt-Injection-Testset (mindestens 20 Angriffsmuster) | Nutzer: konsistente Antwortqualität · Schnelligkeit: Regression erkennt Performance-Regression · DSGVO: Feedback ohne Pflicht zur Personenzuordnung · Rechtssicherheit: Qualitätsnachweis für Audits | Risiko mittel; Aufwand hoch |
| 2F | UX-Verbesserungen: Drag & Drop für Dokumente; Mobile UI Fixes (Tastatur überdeckt Eingabefeld gelöst); Session-Suche (lokal im Browser, kein Server-Aufruf); Touch-Gesten für Mobile | Nutzer: deutlich einfacherer Alltag · Schnelligkeit: lokale Suche < 100 ms · DSGVO Art. 5: minimale Datenübertragung bei lokaler Suche · Rechtssicherheit: kein Einfluss | Risiko niedrig; Aufwand mittel |
| 2G | Betroffenenrechte vollständig implementieren: Datenexport (Art. 20) als JSON-Download; vollständige Datenlöschung (Art. 17) inkl. Sessions/Memory/Vector-DBs/Backups mit Ablauf/Löschprotokoll; 1-Monats-Frist automatisch getrackt; DSB-Benachrichtigung bei Anfrage; Löschnachweis an Betroffenen | Nutzer: einfacher Antrag per Klick · Schnelligkeit: Export < 30 s async · DSGVO Art. 17, 20: Pflichtrecht · Rechtssicherheit: Fristtracking und Nachweis | Risiko hoch; Aufwand hoch |
| 2I | Dokumenten-Governance implementieren: Whitelist erlaubter Dateitypen; Größenlimits; Malware-Scan vor Verarbeitung; 11-Klassen-Klassifikation; PII-Scan; Secret-Scan; Risikolevel-Bestimmung; Entscheidung: erlaubt/anonymisieren/Freigabe nötig/blockieren; Löschung nach Retention-Periode; Preview vor externem Processing | Nutzer: Entscheidung vor externem Senden · Schnelligkeit: Scan < 5 s lokal · DSGVO Art. 5(1)(c): Datensparsamkeit bei Uploads · Rechtssicherheit: Kein ungeprüftes Dokument geht extern | Risiko hoch; Aufwand mittel |
| 2J | Incident-Prozess implementieren: "Datenleck vermutet?"-Button im Dashboard; Incident-Log ohne Inhalt (nur Metadaten); Eskalationskette Admin → DSB → Betreiber AILIZA; Incident-Report exportierbar; Status-Page für Mandanten; Subprozessor-Änderungsprozess wenn Groq/Railway Sub-Prozessoren wechseln | Nutzer (Admin): einfache Incident-Meldung · Schnelligkeit: Incident-Meldung < 1 min · DSGVO Art. 33/34: Meldefrist 72h · Rechtssicherheit: 72h-Frist-Tracking ab Meldung | Risiko hoch; Aufwand mittel |
| 2K | Memory-Governance implementieren: standardmäßig deaktiviert; vor Speicherung: Nutzerbestätigung (nicht Einwilligung); Kategorien was gespeichert werden darf: Firma/Präferenzen/Projekte; Kategorie "niemals": Credentials/PII/Gesundheit/HR; Ablaufzeit pro Fakt; keine sensiblen Daten in Memory | Nutzer: Kontrolle was AILIZA sich merkt · Schnelligkeit: Memory off by default = schneller Start · DSGVO Art. 5: Zweckbindung für Memory · Rechtssicherheit: Explizite Nutzerbestätigung dokumentiert | Risiko mittel; Aufwand mittel |
| 2L | Kosten-Administration implementieren: monatliches Budget in Euro pro Mandant; Forecast (Projektion auf Monatsende); Kosten aufgeschlüsselt nach Nutzer/Mandant/Provider/Use-Case; Top-10 teuerste Anfragen; Export für Controlling (CSV); Benachrichtigung bei 80%/100% des Budgets | Nutzer (Admin): Kostenkontrolle ohne IT-Kenntnisse · Schnelligkeit: Dashboard-Aggregation < 2 s · DSGVO: Kostendaten ohne Anfrageinhalte · Rechtssicherheit: Budgetüberschreitungs-Haftung minimiert | Risiko mittel; Aufwand mittel |
| 2M | AI-Literacy-Training implementieren (EU AI Act Art. 4, Pflicht seit 02.02.2025): 20-Minuten-Nutzertraining (Was kann AILIZA? Was nicht? Was ist verboten?); Admin-Training (Konfiguration, Freigaben, Incidents); Do/Don't-Liste sichtbar im UI; "AILIZA ersetzt keine Rechtsberatung" prominent; Nachweis pro Rolle dokumentiert und exportierbar | Nutzer: schützt vor Fehlanwendung · Schnelligkeit: Training einmalig · DSGVO: Schulungsdaten minimal · Rechtssicherheit: Art.-4-Nachweis für Audits | Risiko hoch; Aufwand mittel |
| 2O | Safe Cache Policy dokumentieren: kein eigener semantischer Cache ohne Mandantentrennung; Provider-Caching im ProviderProfile dokumentiert (Groq: metadata-only, kein Input-Caching dokumentiert); Cache-Invalidierung bei Policy- oder Provider-Änderung; Option für zukünftigen eigenen Cache offen gehalten | Nutzer: kein Cache-bedingte Datenleck · Schnelligkeit: Provider-Cache kann Latenz reduzieren · DSGVO Art. 5: Caching-Verhalten muss bekannt sein · Rechtssicherheit: Provider-Vertrag muss Caching regeln | Risiko mittel; Aufwand niedrig |
| 2P | Generative UI Controls implementieren: Action Cards für häufige Aufgaben; bearbeitbare Formulare aus Antworten; Dokumenten-Preview mit hervorgehobenen sensiblen Bereichen; Voice als P3 (nicht MVP); keine unaufgeforderten UI-Aktionen | Nutzer: direkte Aktionen aus Antworten · Schnelligkeit: Action Cards ohne zusätzliche Anfrage · DSGVO Art. 13: Transparenz was die Aktion tut · Rechtssicherheit: Nutzerbestätigung vor Aktion | Risiko niedrig; Aufwand hoch |
| 2Q | Bias-Monitoring einrichten: Prompt-Bias / Tool-Bias / Output-Bias / Use-Case-Bias überwachen (NICHT Trainings-Bias — AILIZA nutzt externe Modelle); manuelle Stichproben aus Goldset; Automation als P3; Befunde in Quality-Review | Nutzer: fairere Antworten · Schnelligkeit: kein Einfluss · DSGVO Art. 22: Schutz vor diskriminierenden automatisierten Entscheidungen · Rechtssicherheit: EU AI Act Art. 9 Risikomonitoring | Risiko mittel; Aufwand mittel |
| 2R | Migration/Rollback definieren: Rollback-Kriterien definiert (wann wird ein Release zurückgezogen); Provider-Wechsel offline getestet vor Live-Gang; Policy-Migration dokumentiert (alte Policy → neue Policy ohne Datenverlust); Tool-Deaktivierung ohne Server-Neustart möglich | Nutzer: kein Datenverlust bei Updates · Schnelligkeit: Rollback < 30 min · DSGVO Art. 25, 32: Integrität bei Änderungen · Rechtssicherheit: Change-Management-Dokumentation | Risiko mittel; Aufwand mittel |
| 2S | GPAI-Klarstellung dokumentieren: AILIZA nutzt externe Modelle → ProviderProfile + Due-Diligence ausreichend; GPAI-Provider-Pflichten liegen beim Modellanbieter (Groq/Meta); eigene GPAI-Pflichten nur wenn AILIZA ein eigenes Basismodell bereitstellt (nicht geplant); Klarstellung in ADR und Compliance-Paket | Nutzer: nicht sichtbar · Schnelligkeit: kein Einfluss · DSGVO: GPAI-Pflichten richtig zugeordnet · Rechtssicherheit: EU AI Act GPAI-Abgrenzung dokumentiert | Risiko mittel; Aufwand niedrig |
| 2T | Vector-Database-Governance implementieren: pro Embedding-Eintrag: source, tenant\_id, data\_class, created\_at, retention\_days, user\_id; Löschung auf Betroffenenrechte-Anfrage (Art. 17); Mandantentrennung in Vector-DB erzwungen; SQLite-basiert für KMU; Retrieval nur nach Memory-Retrieval-Policy (1U) | Nutzer: Löschrecht auch für Memory-Inhalte · Schnelligkeit: Retrieval-Filter < 10 ms · DSGVO Art. 17: Löschrecht in Vector-DB · Rechtssicherheit: Tenant-Isolation in Vector-DB | Risiko hoch; Aufwand mittel |
| 2U | VVT vollständig nach DSGVO Art. 30: pro Use-Case: Zweck/Datenarten/Betroffene/Rechtsgrundlage/Empfänger/Speicherfrist/Löschkonzept/TOMs; separates Dokument (nicht Audit-Log); Update bei Provider- oder Prozessänderung; DSB bestätigt vor Gate 3 | Nutzer: nicht sichtbar · Schnelligkeit: kein Einfluss · DSGVO Art. 30: Pflichtdokument · Rechtssicherheit: Grundlage für Behördenanfragen | Risiko hoch wenn fehlend; Aufwand hoch |

---

## 11§ Phase 3 — Multi-Tenant, Produktion (Monat 2–4)

| ID | Beschreibung | 4-Kriterien-Note | Risiko/Aufwand |
|----|--------------|-----------------|----------------|
| 3A | Multi-Tenant nach company\_id: vollständige Datentrennung; company\_id in jeder DB-Abfrage als Pflichtfilter; kein Cross-Tenant-Datenzugriff technisch möglich; Mandantenfilter-Test in automatischer Testsuite | Nutzer: Datentrennung selbstverständlich · Schnelligkeit: Index auf company\_id · DSGVO Art. 25, 32: Technische Mandantentrennung · Rechtssicherheit: Haftungstrennung zwischen Mandanten | Risiko hoch; Aufwand mittel |
| 3B | Provider-Policy pro Mandant: jeder Mandant kann eigene erlaubte Provider konfigurieren; Konfiguration importierbar/exportierbar; Providerwechsel ohne Datenverlust; Policy-Inheritance von Betreiber-Ebene | Nutzer (Admin): Kontrolle über Provider · Schnelligkeit: Policy-Lookup < 5 ms · DSGVO Art. 28: AVV pro Provider · Rechtssicherheit: Mandanten-spezifische Rechtsgrundlagen | Risiko mittel; Aufwand mittel |
| 3C | Admin-Dashboard vollständig: RACI-Übersicht; Kostenauswertung; Incident-Übersicht; Provider-Status; Freigabe-Historie; Lösch-Protokoll; AI-Literacy-Nachweise; Export für DSB; Multi-Tenant-Übersicht für Betreiber | Nutzer (Admin/DSB): vollständige Kontrolle · Schnelligkeit: Dashboard < 3 s · DSGVO Art. 30: Nachweisführung · Rechtssicherheit: DSB-Zugang zu allen Kontrollinformationen | Risiko mittel; Aufwand hoch |
| 3D | EU AI Act Art. 50 Transparenzpflichten umsetzen (Frist: 02.08.2026): KI-Interaktion immer offenlegen wenn Nutzer mit KI kommuniziert; KI-generierte Inhalte kennzeichnen; Hinweis in jeder AILIZA-Antwort; Art. 52 nur wenn juristisch spezifisch nachgewiesen; Timeline: Art. 4 (AI-Literacy) seit 02.02.2025 · GPAI seit 02.08.2025 · Art. 50 ab 02.08.2026 | Nutzer: immer klar dass KI antwortet · Schnelligkeit: Disclaimer < 1 ms hinzufügen · EU AI Act Art. 50: Pflicht ab 02.08.2026 · Rechtssicherheit: Frist eingehalten | Risiko hoch (Frist!); Aufwand niedrig |
| 3E | Railway Go-live: nur nach Gate 3 + AVV mit Railway + Controller/Processor-Modell vollständig + EU-Region bestätigt; PORT aus Umgebungsvariable; CORS-Konfiguration für Produktions-URL; HTTPS erzwungen; keine Debug-Infos in Produktion | Nutzer: kein Unterschied zu lokalem Betrieb · Schnelligkeit: EU-Region minimiert Latenz · DSGVO Art. 44ff: Drittlandübertragung geprüft · Rechtssicherheit: AVV und Hosting-Vereinbarung vollständig | Risiko hoch; Aufwand mittel |
| 3F | Backup/Restore: verschlüsselt; Mandantentrennung in Backups; Restore-Test alle 3 Monate mit Protokoll; Backup-Expiry gemäß Retention-Policy; überschriebene Backups werden vollständig gelöscht (für Betroffenenrechte) | Nutzer: Datenverfügbarkeit · Schnelligkeit: Backup async · DSGVO Art. 32: Verfügbarkeit und Integrität · Rechtssicherheit: Restore-Test-Nachweis für Audits | Risiko hoch; Aufwand mittel |
| 3G | Proaktiver Assistent (opt-in): nur nach expliziter Aktivierung; keine stillen Hintergrundaktionen; Hinweise nur innerhalb aktiv verbundener Tools; Preview + Freigabe vor jeder externen Aktion; jederzeit deaktivierbar; kein Datensammeln ohne aktive Sitzung | Nutzer: Assistent als Helfer nicht als Überwacher · Schnelligkeit: opt-in reduziert unerwünschte Aktionen · DSGVO Art. 5: Zweckbindung für proaktive Aktionen · Rechtssicherheit: Nutzerbestätigung vor jeder Aktion | Risiko mittel; Aufwand hoch |
| 3N | Tool Plugin Contract: Manifest (name/purpose/permissions/data\_classes); Sandbox für Plugin-Ausführung; Versionierung; automatische Tests gegen Prompt-Injection + Daten-Exfiltration; Dry-Run für schreibende Aktionen vor Ausführung | Nutzer: klare Beschreibung jedes Tools · Schnelligkeit: Manifest-Prüfung < 10 ms · DSGVO Art. 5: Zweckbindung per Tool-Manifest · Rechtssicherheit: Plugin-Sicherheit nachweisbar | Risiko mittel; Aufwand hoch |

---

## 12§ Produktpakete

### 12.1§ Starter

Zielgruppe: Kleinstunternehmen, Einstieg ohne IT-Abteilung.

- Lokal/Strict-Modus; keine externe KI ohne Admin-Aktivierung
- Fast-Path für Alltagsaufgaben
- Vollständiges Onboarding "Start in 10 Minuten"
- Safe Defaults ab Werk
- AI-Literacy-Training Basis

### 12.2§ Business

Zielgruppe: KMU mit regelmäßigem KI-Einsatz.

- Externe KI mit ProviderProfile + Freigabe-System
- Streaming-Antworten
- Kosten-Administration und Hard-Limits
- Generative UI Controls (Action Cards, Formulare)
- Memory-Governance (opt-in)
- Vollständiges Admin-Dashboard

### 12.3§ Audit Ready

Zielgruppe: KMU mit Datenschutzbeauftragtem oder in regulierten Branchen.

- DSB-Workflow und DSB-Zugang
- Vollständiger Audit-Trail (4 Log-Typen)
- Betroffenenrechte vollständig (Export, Löschung inkl. Backups + Vector-DBs)
- Reports für Behörden und DSB
- AI-Literacy-Nachweis pro Rolle exportierbar
- Vertragspaket (AVV-Templates, TOMs, Provider-Liste)
- RBAC vollständig

Hinweis: Das Audit-Ready-Paket unterstützt Audit- und Nachweisanforderungen und reduziert DSGVO-Risiken. Es ersetzt keine rechtliche Freigabe durch einen Datenschutzbeauftragten oder Anwalt.

---

## 13§ Betrieb, SLA und Support

| Bereich | Vorgabe |
|---------|---------|
| Backup-Zeitplan | Täglich; 30 Tage rolling; verschlüsselt |
| Restore-Test | Alle 3 Monate mit Protokoll |
| Status-Page | Öffentlich erreichbar; zeigt aktuellen Provider-Status |
| Wartungsfenster | Ankündigung 48h vorher; bevorzugt Wochenende 02:00–05:00 Uhr |
| Support-Kontakt | Im Dashboard sichtbar; E-Mail und Ticketsystem |
| Kritischer Incident | Reaktionszeit 4 Stunden nach Meldung |
| Versions- und Änderungslog | Pro Release; öffentlich im Repository |
| Observability-Dashboard | Für Betreiber: P95 pro Route; Cost-Log; Error-Rate; Provider-Status |
| AI-Literacy-Nachweis | Pro Nutzer-Rolle exportierbar für Audits |

---

## 14§ Compliance-Paket

Das Compliance-Paket enthält folgende Vorlagen und Dokumente. Alle Vorlagen müssen vor Gate 2 ausgefüllt und unterschrieben vorliegen.

| Dokument | Beschreibung | Frist |
|----------|-------------|-------|
| AVV/DPA-Vorlage Railway | Auftragsverarbeitungsvertrag für Hosting | Vor Gate 2 |
| AVV/DPA-Vorlage Groq | Auftragsverarbeitungsvertrag für LLM-Verarbeitung | Vor Gate 2 |
| TOMs | Technisch-organisatorische Maßnahmen (Verschlüsselung, Zugang, Backup, Löschung) | Vor Gate 2 |
| Provider-Liste | Alle Provider mit AVV-Status + GPAI-Klassifikation | Vor Gate 2 |
| Sub-Prozessor-Register | Groq, Railway + deren Sub-Prozessoren | Vor Gate 2 |
| Löschkonzept | Inkl. Vector-DBs, Backups, Audit-Logs anonymisiert | Vor Gate 2 |
| Rollen-/Berechtigungskonzept | RACI + RBAC-Dokumentation | Vor Gate 2 |
| EU AI Act Use-Case-Bewertung | AILIZA = Limited Risk (Art. 50); kein Hochrisiko (Art. 6) | Vor Gate 3 |
| Datenschutzhinweise Endnutzer | DSGVO Art. 13/14 für alle Verarbeitungszwecke | Vor Gate 2 |
| AI-Literacy-Nachweis | Pro Rolle: Nutzer/Admin/DSB | Vor Gate 3 |
| VVT vollständig | DSGVO Art. 30; DSB-bestätigt | Vor Gate 3 |
| DSFA-Ergebnis | Art. 35 DSGVO; bei Hochrisiko DPIA vollständig | Vor Gate 2 |

---

## 15§ Implementierungsreihenfolge

### 15.1§ P0 — Vor der ersten Codezeile (Tag 1–5)

Kein Feature-Code wird geschrieben bevor alle P0-Items abgeschlossen sind.

| Tag | Aufgabe | Gate |
|-----|---------|------|
| 1 | 0I Datenflussinventar (Dokument) | Gate 1 |
| 1 | 0L Controller/Processor-Modell (Dokument) | Gate 1 |
| 1 | ADR-Repository anlegen; ADR-001 LLM-Auswahl | Gate 1 |
| 1 | 0H RACI-Dokument erstellen | Gate 1 |
| 2 | 0D Textkorrektur-Pass (alle Texte) | Gate 1 |
| 2 | 0P 11-Klassen-Klassifikations-Engine (lokal, pattern-basiert) | Gate 1 |
| 2 | 0M Data Governance Layer (Architektur + erste Implementierung) | Gate 1 |
| 3 | 0F Kill-Switch + automatisierter Test | Gate 1 |
| 3 | 0A Secret-Blocker | Gate 1 |
| 3 | 0G Safe Defaults | Gate 1 |
| 3 | Obs0 4 Log-Typen (Struktur + Rotation) | Gate 1 |
| 4 | 0N LLM-Orchestrator Interface + Groq-Adapter | Gate 1 |
| 4 | 0B ProviderProfile Groq + Railway | Gate 1 |
| 4 | 0C Policy-Gateway (fail-closed) | Gate 1 |
| 5 | 0E Redaction + PII-Vault | Gate 1 |
| 5 | 1W Data Lineage Metadata | Gate 1 |
| 5 | Gate-1-Checkliste abarbeiten und dokumentieren | Gate 1 |

### 15.2§ P1 — Vor dem Pilot (Woche 2–4)

| Woche | Aufgabe | Gate |
|-------|---------|------|
| 2 | 1F Fast-Path-Router | Gate 2 |
| 2 | 1E Token-Budget-Gateway + Hard-Cost-Limits | Gate 2 |
| 2 | 1B PII-Vault TTL + Cleanup | Gate 2 |
| 2 | 1C IP-Hash | Gate 2 |
| 2 | 1I Mandanten-DB-Modelle + Mandantenfilter-Test | Gate 2 |
| 2 | 0J Rechtsgrundlagen-Matrix (Dokument) | Gate 2 |
| 2 | 0K DSFA-Screening | Gate 2 |
| 3 | 1U Memory-Retrieval-Policy | Gate 2 |
| 3 | 1T Tool-Manifest | Gate 2 |
| 3 | 1A Streaming mit Output-Sicherheitsmodell | Gate 2 |
| 3 | 1D Output-Guardrail erweitert | Gate 2 |
| 3 | 1G Risikoampel | Gate 2 |
| 3 | 1H Fehlermeldungen kartiert | Gate 2 |
| 3 | 1L Quellen-/Unsicherheitsmodus | Gate 2 |
| 4 | 1M Freigabe-Dialog | Gate 2 |
| 4 | 1K Freigabe-Bundles | Gate 2 |
| 4 | 1N Kosten-/Antwortmodus + Verarbeitungsstatus | Gate 2 |
| 4 | 1O Onboarding "Start in 10 Minuten" | Gate 2 |
| 4 | 1P Verarbeitungsstatus pro Antwort | Gate 2 |
| 4 | 1Q Barrierefreiheit (WCAG 2.1 AA) | Gate 2 |
| 4 | 1R Modulare Service-Grenzen | Gate 2 |
| 4 | 1S Performance-Budgets + Monitoring | Gate 2 |
| 4 | 1V Versionierung im Audit-Log | Gate 2 |
| 4 | DashMin Admin-Minimaldashboard | Gate 2 |
| 4 | 2H Abuse/Rate-Limits | Gate 2 |
| 4 | AVV Railway + Groq unterzeichnet | Gate 2 |
| 4 | Gate-2-Checkliste abarbeiten und dokumentieren | Gate 2 |

### 15.3§ Phase 2 — Monat 1–2 (Richtung Gate 3)

2A Login/RBAC · 2B Orange-Tier Guardrail · 2C Use-Case-Katalog YAML · 2D Audit-Retention + Löschprotokoll · 2E Qualitätssicherung + Goldset · 2F UX-Verbesserungen · 2G Betroffenenrechte vollständig · 2I Dokumenten-Governance · 2J Incident-Prozess · 2K Memory-Governance · 2L Kosten-Administration · 2M AI-Literacy-Training + Nachweis · 2O Safe Cache Policy · 2P Generative UI Controls · 2Q Bias-Monitoring (manuell) · 2R Migration/Rollback-Konzept · 2S GPAI-Klarstellung dokumentiert · 2T Vector-DB-Governance · 2U VVT vollständig (DSB-Bestätigung)

### 15.4§ Phase 3 — Monat 2–4 (Gate 3 und Produktion)

3A Multi-Tenant company\_id vollständig · 3B Provider-Policy pro Mandant · 3C Admin-Dashboard vollständig · 3D EU AI Act Art. 50 Kennzeichnung (Frist: 02.08.2026) · Backup/Restore-Test mit Protokoll · 3E Railway Go-live (nur nach Gate 3) · 3F Backup/Restore-Prozess vollständig · 3G Proaktiver Assistent (opt-in) · 3N Tool Plugin Contract · Gate-3-Checkliste mit DSB-Bestätigung

---

---

## 16§ Eigenständige Verbesserungen des Agenten

Kernprinzip: Alle Lernmechanismen sind transparent, mandantenisoliert, löschbar, opt-in und ausschließlich prompt-basiert. Kein Modell-Finetuning. Kein Training mit PII oder Unternehmensdaten.

### 16.1§ Reflection Skill (`reflection_skill.py`) — Funktion

Der Reflection Skill ist der RAG-Memory-Manager von AILIZA. Er speichert unternehmensinternes Wissen in SQLite und reichert Prompts bei Bedarf mit relevantem Kontext an.

| Kategorie | Beispiel | data_class | Löschbar |
|-----------|----------|------------|---------|
| Firmenvokabular | „Unser Produkt heißt ABI-3000" | vocabulary | Ja |
| Häufige Anfragen | FAQ-Muster ohne PII | pattern | Ja |
| Nutzer-Korrekturen | „Schreibe immer 'Sie', nicht 'du'" | correction | Ja |
| Projekt-Kontext | Aktive Projekte, Zuständigkeiten | context | Ja |

SQLite-Schema: `id, company_id, user_id, data_class, content, quality_score REAL DEFAULT 1.0, created_at, expires_at, opt_in_confirmed INTEGER DEFAULT 0`

Retrieval-Policy — vor jedem Prompt-Inject müssen alle 4 Bedingungen erfüllt sein: `opt_in_confirmed = 1`; `data_class` für aktuellen Provider in Datenfluss-Matrix freigegeben; `expires_at` in der Zukunft; kein PII im Fakt (GuardrailSkill-Pre-Check). Nur dann → Top-K-Kontext in Prompt.

### 16.2§ Feedback-Loop

```
Antwort → ✓ hilfreich / ✗ nicht hilfreich (+ optionaler Freitext)
  ✓ → quality_score +0,1 (max 2,0)
  ✗ → quality_score −0,2 (min 0,0); bei score < 0,3 → Fakt nicht mehr abgerufen
  ≥ 3 negative Bewertungen desselben Fragetyps → Routing-Anpassungsvorschlag im Admin-Dashboard
  Admin bestätigt manuell → Änderung aktiviert; versioniert mit policy_version + reason + changed_by
```

Admin kann erfolgreiche Antworten per Klick zum internen Goldenset hinzufügen. Kein automatisches Modell-Finetuning — Verbesserungen wirken ausschließlich über Prompt-Kontext.

### 16.3§ Adaptives Routing

| Schritt | Automatisch |
|---------|-------------|
| Negatives Feedback akkumuliert je Fragetyp + Route | Ja |
| Schwellwert ≥ 3 erreicht → Vorschlag generiert | Ja |
| Admin sieht Vorschlag im Dashboard + Begründung | — |
| Admin bestätigt oder verwirft | Nein — manuell |
| Änderung aktiviert + versioniert | Ja, nach Bestätigung |

Jede Routing-Änderung: `policy_version, changed_by, reason, previous_route, new_route, timestamp` in `data/routing_policy.db`.

### 16.4§ Grenzen — Was AILIZA nicht lernt

Kein Training mit PII; GuardrailSkill prüft vor Speicherung. Keine mandantenübergreifende Verbesserung; `company_id` ist mandatory. Kein Zugriff auf externe Datenquellen ohne explizite Admin-Freigabe. Kein unsichtbares Lernen; alle Facts im Dashboard sichtbar. Kein Lernen von Credentials; Stufe-5-Pattern blockiert Speicherung hart ohne Audit-Log-Eintrag. Kein automatisches Finetuning weder intern noch über externe Anbieter.

### 16.5§ DSGVO-Compliance des Lernens

| Anforderung | Umsetzung |
|-------------|-----------|
| Opt-in je Mandant | `opt_in_confirmed = 0` als Safe Default; Aktivierung nur durch explizite Admin-Bestätigung |
| Transparenz | Memory-Ansicht im Dashboard zeigt alle Facts je Mandant |
| Löschung Einzelfakt | `DELETE /memory/{fact_id}` |
| Löschung gesamtes Memory | `DELETE /memory?company_id=X` (DSGVO Art. 17) |
| VVT-Eintrag | Memory als eigener Verarbeitungsvorgang: Zweck, Rechtsgrundlage Art. 6 Abs. 1 lit. a (aktive Einwilligung), Speicherdauer |
| Retention | `expires_at` je Fakt konfigurierbar; Standard: 90 Tage; automatische Löschung bei Ablauf |

### 16.6§ Phasen-Zuordnung

| Phase | Umfang |
|-------|--------|
| P0 | `reflection_skill.py` Grundgerüst: SQLite-Schema mit `company_id`-Isolation, Opt-in-Flag, TTL `expires_at`, PII-Pre-Check vor Speicherung |
| P1 | Memory-Retrieval-Policy: `data_class` + Provider-Check vor Prompt-Inject; verhindert indirekten Datenleck |
| P2 | Feedback-Loop UI (✓/✗-Buttons im Chat), Goldenset-Erweiterung durch Admin, `quality_score`-Mechanismus |
| P3 | Adaptive Routing-Vorschläge (Schwellwert-basiert, Admin-Bestätigung); Bias-Monitoring auf Memory-Daten |

---

*AILIZA Projektplan v1.0 · 2026-06-19 · sicher im Kern · schnell im Alltag · einfach für KMU*
*© 2026 Karola Fromm-Nasreldin — Alle Rechte vorbehalten*
