# Datenschutz-Folgenabschätzung (DPIA)
## nach Art. 35 DSGVO — AILIZA KI-Assistent

**Dokument-Status:** Vorlage — auszufüllen vor Go-Live  
**Erstellt:** 2026-06-18  
**Verantwortlicher:** [FIRMENNAME EINTRAGEN]  
**Datenschutzbeauftragter (falls bestellt):** [DSB-NAME EINTRAGEN]  
**Versionierung:** v1.0 — vor Inbetriebnahme abzuschließen  

---

## 1§ Warum diese DPIA Pflicht ist

AILIZA erfüllt mindestens zwei der neun WP-248-Kriterien der Datenschutzbehörden, ab zwei ist eine DPIA Pflicht:

- **Kriterium 7 — Beschäftigte als Betroffene:** Mitarbeitende in KMU nutzen das System im Arbeitskontext. Arbeitgeberseitige KI-Systeme, die Arbeitnehmer betreffen, lösen regelmäßig DPIA-Pflicht aus.
- **Kriterium 8 — Innovative Technologie:** Einsatz von Large Language Models (Groq / Meta LLaMA) als neue Technologie mit unvorhersehbaren Folgerisiken.
- **Kriterium 4 (potenziell) — Sensible Daten:** Freitexteingaben können Gesundheitsdaten, Finanzdaten oder HR-bezogene Informationen enthalten.

---

## 2§ Beschreibung der Verarbeitung

### 2.1§ Verantwortlicher

| Feld | Wert |
|------|------|
| Unternehmen | [FIRMENNAME] |
| Adresse | [ADRESSE] |
| E-Mail | [E-MAIL] |
| Datenschutzbeauftragter | [DSB NAME + KONTAKT] (falls nach Art. 37 DSGVO bestellt) |

### 2.2§ Zweck der Verarbeitung

AILIZA ist ein KI-gestützter Assistent für Büroaufgaben in kleinen und mittleren Unternehmen. Verarbeitungszwecke:

- Beantwortung von Mitarbeiterfragen zu Compliance, DSGVO, allgemeinen Geschäftsprozessen
- Erstellung von Texten, E-Mails, Dokumenten und Analysen
- Zusammenfassung und Recherche

AILIZA trifft **keine automatisierten Entscheidungen** mit Rechtswirkung (Art. 22 DSGVO). Alle KI-Ausgaben sind Arbeitshilfen, keine verbindlichen Entscheidungen.

### 2.3§ Verarbeitete Datenkategorien

| Kategorie | Beispiel | Rechtsgrundlage |
|-----------|----------|-----------------|
| Gewöhnliche personenbezogene Daten | Namen, E-Mail-Adressen in Nachrichten | Art. 6 Abs. 1 lit. b/f DSGVO |
| Berufliche Kommunikation | E-Mail-Entwürfe, Dokumentinhalte | Art. 6 Abs. 1 lit. b DSGVO |
| Potenziell besondere Kategorien (Art. 9) | Nur wenn Nutzer diese freiwillig eingibt — technisch nicht erzwungen | Einwilligung Art. 9 Abs. 2 lit. a DSGVO |

**Keine systematische Verarbeitung** besonderer Kategorien. AILIZA ist nicht für Personalentscheidungen, Kreditentscheidungen oder medizinische Diagnosen vorgesehen.

### 2.4§ Betroffene Personen

- Mitarbeitende des Unternehmens (interne Nutzer)
- Potenziell: Dritte, deren Daten in Nachrichten erwähnt werden (z.B. Kundennamen in E-Mail-Entwürfen)

### 2.5§ Datenübermittlungen und Auftragsverarbeiter

| Empfänger | Land | Zweck | Rechtsgrundlage |
|-----------|------|-------|-----------------|
| Groq Inc. | USA | LLM-Inferenz (KI-Verarbeitung) | Art. 46 DSGVO — Standardvertragsklauseln (SCC) + Auftragsverarbeitungsvertrag (AVV) |
| Tavily Inc. (optional) | USA | Echtzeit-Websuche | Art. 46 DSGVO — SCC + AVV (nur wenn TAVILY_API_KEY gesetzt) |

**AVV mit Groq:** Muss vor Go-Live unterzeichnet sein (console.groq.com → Legal).  
**AVV mit Tavily:** Muss vor Aktivierung der Websuche unterzeichnet sein.

### 2.6§ Speicherfristen

| Datenkategorie | Speicherort | Frist | Grundlage |
|----------------|-------------|-------|-----------|
| Chat-Nachrichten | Lokale SQLite-DB | 90 Tage (konfigurierbar: `AILIZA_DATA_RETENTION_DAYS`) | Art. 5 Abs. 1 lit. e DSGVO |
| Audit-Logs | Lokale SQLite-DB | 90 Tage | Art. 30 DSGVO, gesetzliche Aufbewahrung |
| Sitzungs-Metadaten | RAM (kein Persist) | Bis Sitzungsende | — |
| PII-Tokens im Vault | RAM (kein Persist) | 30 Minuten oder Sitzungsende | Art. 25 DSGVO (Privacy by Design) |

---

## 3§ Notwendigkeit und Verhältnismäßigkeit

### 3.1§ Ist die Verarbeitung notwendig?

Ja. Der Einsatz eines KI-Assistenten verfolgt legitime betriebliche Zwecke (Effizienzsteigerung, Unterstützung bei Compliance-Fragen) und ist verhältnismäßig zur wirtschaftlichen Tätigkeit eines KMU.

### 3.2§ Datensparsamkeit (Art. 5 Abs. 1 lit. c)

- Keine Pflicht zur Eingabe personenbezogener Daten
- PII-Erkennung warnt Nutzer vor unbeabsichtigter Dateneingabe
- PII wird vor LLM-Übertragung tokenisiert (Vault-Architektur)
- Keine dauerhafte Speicherung von Klartext-PII

### 3.3§ Zweckbindung (Art. 5 Abs. 1 lit. b)

Daten werden ausschließlich für die vom Nutzer initiierte Anfrage verarbeitet. Kein Training von Modellen mit Nutzerdaten (Groq-Vertragsbedingungen prüfen und dokumentieren).

### 3.4§ Transparenz (Art. 13 DSGVO)

- Einwilligungs-Dialog beim ersten Start informiert über Verarbeitung
- KI-Disclaimer bei jeder Antwort (EU AI Act Art. 52)
- Datenschutzerklärung: **[LINK EINTRAGEN — noch zu erstellen]**

---

## 4§ Risikoanalyse

### 4.1§ Risikobewertung

| # | Risiko | Eintrittsw. | Schwere | Risiko gesamt | Maßnahme |
|---|--------|-------------|---------|---------------|----------|
| R1 | Unbeabsichtigte PII-Übermittlung an Groq | Mittel | Mittel | **Mittel** | PII-Tokenisierung, Warnhinweise |
| R2 | Drittland-Transfer ohne ausreichende Garantien (Groq/USA) | Mittel | Hoch | **Hoch** | SCC + AVV — vor Go-Live abschließen |
| R3 | Unberechtigter Zugriff auf Audit-Logs | Niedrig | Hoch | **Mittel** | Admin-Token-Schutz |
| R4 | Datenpanne durch Sicherheitslücke | Niedrig | Hoch | **Mittel** | HTTPS, Rate Limiting, Input-Validierung |
| R5 | Nutzer vertraut KI-Entscheidung blind | Mittel | Mittel | **Mittel** | Art. 52 Disclaimer, Human Oversight Banner |
| R6 | Verarbeitung besonderer Kategorien ohne Einwilligung | Niedrig | Sehr hoch | **Mittel** | Nutzer-Warnung, keine Erzwingung |
| R7 | Datenverlust bei SQLite-Korruption | Niedrig | Niedrig | **Niedrig** | Regelmäßige Backups empfohlen |

### 4.2§ Verbleibende Risiken nach Maßnahmen

- **R2 (Drittland-Transfer):** Verbleibt solange kein AVV mit Groq unterzeichnet. Nach Unterzeichnung: akzeptabel.
- **R5 (Blinde KI-Vertrauung):** Verbleibt strukturell — reduziert durch Pflicht-Disclaimer, nicht eliminierbar.

**Gesamtbewertung nach Maßnahmen:** Akzeptables Restrisiko, keine Konsultationspflicht nach Art. 36 DSGVO — vorausgesetzt AVV mit Groq ist unterzeichnet.

---

## 5§ Geplante Maßnahmen und Verantwortlichkeiten

| Maßnahme | Verantwortlich | Frist | Status |
|----------|---------------|-------|--------|
| AVV mit Groq unterzeichnen | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| AVV mit Tavily (falls genutzt) | [GESCHÄFTSFÜHRUNG] | Vor Aktivierung | ☐ Offen |
| Datenschutzerklärung veröffentlichen | [DSB / ANWALT] | Vor Go-Live | ☐ Offen |
| Impressum prüfen (DDG §5) | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| `AILIZA_COMPANY_NAME` und `AILIZA_DSB_EMAIL` in `.env` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| `AILIZA_ACCESS_PIN` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| Mitarbeitende über AILIZA-Nutzung informieren | HR / DSB | Vor Inbetriebnahme | ☐ Offen |
| Regelmäßige DPIA-Überprüfung | DSB | Jährlich | ☐ Wiederkehrend |

---

## 6§ Konsultation Datenschutzbehörde (Art. 36)

Eine vorherige Konsultation der zuständigen Aufsichtsbehörde ist **nicht erforderlich**, sofern:
- AVV mit Groq unterzeichnet ist
- Keine automatisierten Entscheidungen mit Rechtswirkung getroffen werden
- Mitarbeitende informiert und eingewilligt haben

Zuständige Behörde: [BUNDESLAND-DATENSCHUTZBEHÖRDE EINTRAGEN]

---

## 7§ Freigabe und Dokumentation

| Rolle | Name | Datum | Unterschrift |
|-------|------|-------|--------------|
| Verantwortlicher / Geschäftsführung | | | |
| Datenschutzbeauftragter (falls bestellt) | | | |
| IT-Verantwortlicher | | | |

**Nächste Überprüfung:** [DATUM — spätestens 12 Monate nach Go-Live]

---

*Diese DPIA-Vorlage wurde auf Basis der AILIZA-Systemarchitektur (Stand 18.06.2026) erstellt. Sie ersetzt keine Rechtsberatung. Bei Unsicherheiten einen auf Datenschutzrecht spezialisierten Anwalt oder den betrieblichen Datenschutzbeauftragten hinzuziehen.*

*Regulatorischer Kontext: DSGVO (EU) 2016/679 · EU AI Act (EU) 2024/1689 · BDSG 2018 · DDG 2024 · TTDSG 2021*
