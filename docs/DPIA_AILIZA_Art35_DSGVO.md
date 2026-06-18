# Datenschutz-Folgenabschätzung (DPIA)
## nach Art. 35 DSGVO — AILIZA KI-Assistent

**Dokument-Status:** Vorlage v1.1 — auszufüllen vor Go-Live  
**Erstellt:** 2026-06-18  
**Zuletzt überarbeitet:** 2026-06-18 (juristische Überarbeitung: Art. 9, Art. 22, TIA, R6)  
**Verantwortlicher:** [FIRMENNAME EINTRAGEN]  
**Datenschutzbeauftragter (falls bestellt):** [DSB-NAME EINTRAGEN]  
**Versionierung:** v1.1 — vor Inbetriebnahme abzuschließen  

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

AILIZA trifft keine automatisierten Entscheidungen mit Rechtswirkung (Art. 22 DSGVO). KI-Ausgaben werden ausschließlich als Entscheidungshilfe bereitgestellt. Entscheidungen mit rechtlicher oder vergleichbarer erheblicher Wirkung werden stets durch natürliche Personen getroffen.

### 2.3§ Verarbeitete Datenkategorien

| Kategorie | Beispiel | Rechtsgrundlage |
|-----------|----------|-----------------|
| Gewöhnliche personenbezogene Daten | Namen, E-Mail-Adressen in Nachrichten | Art. 6 Abs. 1 lit. b/f DSGVO |
| Berufliche Kommunikation | E-Mail-Entwürfe, Dokumentinhalte | Art. 6 Abs. 1 lit. b DSGVO |

Besondere Kategorien personenbezogener Daten (Art. 9 DSGVO) sind nicht Gegenstand der vorgesehenen Verarbeitung. Nutzer werden angewiesen, keine besonderen Kategorien personenbezogener Daten einzugeben. Erfolgt dennoch eine Eingabe durch den Nutzer, erfolgt die Verarbeitung ausschließlich im Rahmen der jeweiligen Nutzeranfrage und unter Anwendung der vorhandenen technischen Schutzmaßnahmen (PII-Tokenisierung, Warnhinweise). Eine wirksame Einwilligung nach Art. 9 Abs. 2 lit. a DSGVO wird durch die bloße Eingabe nicht begründet.

Keine systematische Verarbeitung besonderer Kategorien. AILIZA ist nicht für Personalentscheidungen, Kreditentscheidungen oder medizinische Diagnosen vorgesehen.

### 2.4§ Betroffene Personen

- Mitarbeitende des Unternehmens (interne Nutzer)
- Kunden, Lieferanten und Geschäftspartner, deren Daten in Nachrichten oder Dokumenten erwähnt werden
- Bewerber, sofern das System für HR-bezogene Aufgaben genutzt wird
- Sonstige Dritte, deren personenbezogene Daten in Freitexteingaben vorkommen

### 2.5§ Datenübermittlungen und Auftragsverarbeiter

| Empfänger | Land | Zweck | Rechtsgrundlage |
|-----------|------|-------|-----------------|
| Groq Inc. | USA | LLM-Inferenz (KI-Verarbeitung) | Art. 46 DSGVO — Standardvertragsklauseln (SCC) + Auftragsverarbeitungsvertrag (AVV) + Transfer Impact Assessment (TIA) |
| Tavily Inc. (optional) | USA | Echtzeit-Websuche | Art. 46 DSGVO — SCC + AVV + TIA (nur wenn TAVILY_API_KEY gesetzt) |

**AVV mit Groq:** Muss vor Go-Live unterzeichnet sein (console.groq.com → Legal).  
**AVV mit Tavily:** Muss vor Aktivierung der Websuche unterzeichnet sein.  
**Transfer Impact Assessment (TIA):** Nach Schrems II (EuGH C-311/18) sind SCC allein nicht ausreichend. Für jeden US-Empfänger ist ein TIA zu dokumentieren, der die tatsächlichen Zugriffsmöglichkeiten US-amerikanischer Behörden (insb. nach FISA 702, EO 12333) bewertet und ggf. ergänzende technische Maßnahmen festlegt (z.B. Verschlüsselung vor Übermittlung).

### 2.6§ Speicherfristen

| Datenkategorie | Speicherort | Inhalt | Frist | Grundlage |
|----------------|-------------|--------|-------|-----------|
| Chat-Nachrichten | Lokale SQLite-DB | Tokenisierte Texte (kein PII-Klartext) | 90 Tage (konfigurierbar: `AILIZA_DATA_RETENTION_DAYS`) | Art. 5 Abs. 1 lit. e DSGVO |
| Audit-Logs | Lokale SQLite-DB | Ausschließlich technische Metadaten: Zeitpunkt, Nutzer-ID, Fehlercodes, Systemereignisse — keine vollständigen Prompt- oder Antwortinhalte | 90 Tage | Art. 30 DSGVO |
| Sitzungs-Metadaten | RAM (kein Persist) | Session-ID, Compliance-Status | Bis Sitzungsende | — |
| PII-Tokens im Vault | RAM (kein Persist) | Tokenisierungs-Map | 30 Minuten oder Sitzungsende | Art. 25 DSGVO (Privacy by Design) |

---

## 3§ Notwendigkeit und Verhältnismäßigkeit

### 3.1§ Ist die Verarbeitung notwendig?

Ja. Der Einsatz eines KI-Assistenten verfolgt legitime betriebliche Zwecke (Effizienzsteigerung, Unterstützung bei Compliance-Fragen) und ist verhältnismäßig zur wirtschaftlichen Tätigkeit eines KMU.

### 3.2§ Datensparsamkeit (Art. 5 Abs. 1 lit. c)

- Keine Pflicht zur Eingabe personenbezogener Daten
- PII-Erkennung warnt Nutzer vor unbeabsichtigter Dateneingabe
- PII wird vor LLM-Übertragung tokenisiert (Vault-Architektur)
- Keine dauerhafte Speicherung von Klartext-PII
- Audit-Logs enthalten keine Prompt- oder Antwortinhalte

### 3.3§ Zweckbindung (Art. 5 Abs. 1 lit. b)

Daten werden ausschließlich für die vom Nutzer initiierte Anfrage verarbeitet. Kein Training von Modellen mit Nutzerdaten (Groq-Vertragsbedingungen prüfen und im TIA dokumentieren).

### 3.4§ Transparenz (Art. 13 DSGVO)

- Informationsdialog beim ersten Start gemäß Art. 13 DSGVO
- KI-Disclosure bei jeder Antwort gemäß den Transparenzpflichten des EU AI Act
- Datenschutzerklärung: [LINK EINTRAGEN — noch zu erstellen]

### 3.5§ Technische und organisatorische Maßnahmen (Art. 32 DSGVO)

- HTTPS / TLS 1.2+ für alle Netzwerkverbindungen
- Zugriffsschutz durch konfigurierbaren PIN (`AILIZA_ACCESS_PIN`)
- Admin-Endpoints durch separates Admin-Token geschützt
- Rate Limiting (20 Anfragen/Minute pro IP)
- Input-Validierung gegen Injection-Angriffe
- SQLite-Datenbank lokal, kein externer Datenbankzugriff
- Regelmäßiges Löschen alter Sessions (automatisierter Retention-Daemon)
- Backups der SQLite-Datenbank: verschlüsselt aufbewahren und Zugriff auf berechtigte Personen beschränken

---

## 4§ Risikoanalyse

### 4.1§ Risikobewertung

| # | Risiko | Eintrittsw. | Schwere | Risiko gesamt | Maßnahme |
|---|--------|-------------|---------|---------------|----------|
| R1 | Unbeabsichtigte PII-Übermittlung an Groq | Mittel | Mittel | **Mittel** | PII-Tokenisierung, Warnhinweise |
| R2 | Drittland-Transfer ohne ausreichende Garantien (Groq/USA) | Mittel | Hoch | **Hoch** | SCC + AVV + TIA — vor Go-Live abschließen |
| R3 | Unberechtigter Zugriff auf Audit-Logs | Niedrig | Hoch | **Mittel** | Admin-Token-Schutz |
| R4 | Datenpanne durch Sicherheitslücke | Niedrig | Hoch | **Mittel** | HTTPS, Rate Limiting, Input-Validierung |
| R5 | Nutzer vertraut KI-Entscheidung blind | Mittel | Mittel | **Mittel** | KI-Disclosure, Human Oversight Banner |
| R6 | Eingabe besonderer Kategorien (Gesundheit, Gehalt, HR) durch Nutzer | Mittel | Sehr hoch | **Hoch** | Nutzerwarnungen, Anweisung zur Nicht-Eingabe, technische PII-Erkennung |
| R7 | Datenverlust bei SQLite-Korruption | Niedrig | Niedrig | **Niedrig** | Regelmäßige Backups |
| R8 | Zugriff auf unverschlüsselte Backups | Niedrig | Hoch | **Mittel** | Verschlüsselung aller Backups, Zugriffskontrollen |

### 4.2§ Verbleibende Risiken nach Maßnahmen

- **R2 (Drittland-Transfer):** Verbleibt erhöht solange TIA nicht abgeschlossen. Nach vollständigem Abschluss (AVV + SCC + TIA mit ggf. ergänzenden TOMs): vertretbar.
- **R5 (Blinde KI-Vertrauung):** Strukturelles Restrisiko — durch Pflicht-Disclosure und Human Oversight Banner reduziert, nicht vollständig eliminierbar.
- **R6 (Besondere Kategorien):** Verbleibt solange Freitexteingabe möglich. Reduzierung durch Nutzerschulung und technische Warnhinweise.

**Gesamtbewertung nach Maßnahmen:** Vertretbares Restrisiko, keine Konsultationspflicht nach Art. 36 DSGVO — vorausgesetzt AVV mit Groq, SCC und TIA sind abgeschlossen.

---

## 5§ Geplante Maßnahmen und Verantwortlichkeiten

| Maßnahme | Verantwortlich | Frist | Status |
|----------|---------------|-------|--------|
| AVV mit Groq unterzeichnen | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| AVV mit Tavily (falls genutzt) | [GESCHÄFTSFÜHRUNG] | Vor Aktivierung | ☐ Offen |
| Transfer Impact Assessment (TIA) für Groq dokumentieren | [DSB] | Vor Go-Live | ☐ Offen |
| Transfer Impact Assessment (TIA) für Tavily (falls genutzt) | [DSB] | Vor Aktivierung | ☐ Offen |
| Datenschutzerklärung veröffentlichen | [DSB / ANWALT] | Vor Go-Live | ☐ Offen |
| Impressum prüfen (DDG §5) | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| `AILIZA_COMPANY_NAME` und `AILIZA_DSB_EMAIL` in `.env` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| `AILIZA_ACCESS_PIN` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| Backups verschlüsseln und Zugriffskonzept dokumentieren | IT-Admin | Vor Go-Live | ☐ Offen |
| Mitarbeitende gemäß Art. 13 DSGVO informieren | HR / DSB | Vor Inbetriebnahme | ☐ Offen |
| Nutzungsrichtlinie: keine besonderen Kategorien eingeben | HR / DSB | Vor Inbetriebnahme | ☐ Offen |
| Regelmäßige DPIA-Überprüfung | DSB | Jährlich | ☐ Wiederkehrend |

---

## 6§ Konsultation Datenschutzbehörde (Art. 36)

Eine vorherige Konsultation der zuständigen Aufsichtsbehörde ist nicht erforderlich, sofern:
- AVV mit Groq unterzeichnet ist
- TIA für alle Drittlandübermittlungen dokumentiert ist
- Keine automatisierten Entscheidungen mit Rechtswirkung getroffen werden
- Mitarbeitende gemäß Art. 13 DSGVO informiert wurden

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

*Diese DPIA-Vorlage wurde auf Basis der AILIZA-Systemarchitektur (Stand 18.06.2026) erstellt und juristisch überarbeitet (v1.1). Sie ersetzt keine individuelle Rechtsberatung. Bei Unsicherheiten einen auf Datenschutzrecht spezialisierten Rechtsanwalt oder den betrieblichen Datenschutzbeauftragten hinzuziehen.*

*Regulatorischer Kontext: DSGVO (EU) 2016/679 · EU AI Act (EU) 2024/1689 · BDSG 2018 · DDG 2024 · TTDSG 2021 · EuGH C-311/18 (Schrems II)*
