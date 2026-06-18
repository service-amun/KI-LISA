# Datenschutz-Folgenabschätzung (DPIA)
## nach Art. 35 DSGVO — AILIZA KI-Assistent

**Dokument-Status:** Vorlage v1.3 — auszufüllen vor Go-Live  
**Erstellt:** 2026-06-18  
**Zuletzt überarbeitet:** 2026-06-18 (v1.3: §26 BDSG, Art. 9 präzisiert, DPF-Checkliste, EU AI Act Reg.-Nr., Art. 36 vorsichtiger)  
**Verantwortlicher:** [FIRMENNAME EINTRAGEN]  
**Datenschutzbeauftragter (falls bestellt):** [DSB-NAME EINTRAGEN]  
**Versionierung:** v1.3 — vor Inbetriebnahme abzuschließen  

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
| Personenbezogene Daten von Mitarbeitenden | Namen, dienstliche E-Mail-Adressen, Arbeitskorrespondenz | Art. 6 Abs. 1 lit. b DSGVO i.V.m. **§ 26 Abs. 1 BDSG** (Beschäftigtendatenschutz) |
| Personenbezogene Daten von Dritten | Kundennamen, Kontaktdaten in E-Mail-Entwürfen | Art. 6 Abs. 1 lit. f DSGVO (berechtigtes Interesse) |
| Berufliche Kommunikation | E-Mail-Entwürfe, Dokumentinhalte | Art. 6 Abs. 1 lit. b DSGVO |

Hinweis zu Beschäftigtendaten: Bei der Verarbeitung von Daten eigener Mitarbeitender ist stets § 26 BDSG als spezialgesetzliche Grundlage vorrangig zu prüfen. Insbesondere für Überwachungsmaßnahmen oder die Auswertung von Kommunikationsinhalten gelten verschärfte Anforderungen. AILIZA ist nicht als Überwachungswerkzeug konzipiert.

**Besondere Kategorien personenbezogener Daten nach Art. 9 DSGVO**

Die Verarbeitung besonderer Kategorien personenbezogener Daten ist nicht Zweck des Systems. Aufgrund freier Texteingaben kann eine unbeabsichtigte Eingabe solcher Daten jedoch nicht vollständig ausgeschlossen werden.

Das System ist nicht für Gesundheitsdaten, Personalentscheidungen, Kreditwürdigkeitsprüfungen, medizinische Diagnosen oder vergleichbare Hochrisiko-Anwendungen vorgesehen. Nutzer werden vor und während der Nutzung darauf hingewiesen, keine besonderen Kategorien personenbezogener Daten einzugeben.

Bei erkannten sensiblen Inhalten oder PII-Mustern wird der Nutzer gewarnt. Inhalte werden vor einer weiteren Verarbeitung soweit technisch möglich tokenisiert oder minimiert. Klartextdaten werden nicht dauerhaft gespeichert.

### 2.4§ Betroffene Personen

- Mitarbeitende des Unternehmens (interne Nutzer)
- Kunden, Lieferanten und Geschäftspartner, deren Daten in Nachrichten oder Dokumenten erwähnt werden
- Bewerber, sofern das System für HR-bezogene Aufgaben genutzt wird
- Sonstige Dritte, deren personenbezogene Daten in Freitexteingaben vorkommen

### 2.5§ Datenübermittlungen und Auftragsverarbeiter

Vor Go-Live ist für jeden eingesetzten US-Dienstleister zu prüfen und zu dokumentieren:

- Besteht eine gültige Zertifizierung im EU-US Data Privacy Framework (DPF)? Prüfung unter dataprivacyframework.gov. Falls zertifiziert: Rechtsgrundlage Art. 45 DSGVO (Angemessenheitsbeschluss 2023/1795) — SCC und TIA sind dann nicht zwingend, aber als Fallback empfohlen.
- Liegt ein Auftragsverarbeitungsvertrag (AVV) vor?
- Falls keine DPF-Zertifizierung besteht: Sind Standardvertragsklauseln (SCC, Art. 46 DSGVO) und ein Transfer Impact Assessment (TIA nach Schrems II, EuGH C-311/18) abgeschlossen?
- Ist vertraglich ausgeschlossen, dass Eingaben und Ausgaben zu Trainingszwecken verwendet werden?

| Empfänger | Land | Zweck | Zu prüfende Rechtsgrundlage |
|-----------|------|-------|---------------------------|
| Groq Inc. | USA | LLM-Inferenz | Art. 45 DSGVO (DPF), sofern zertifiziert — sonst Art. 46 + SCC + AVV + TIA |
| Tavily Inc. (optional) | USA | Echtzeit-Websuche | Art. 45 DSGVO (DPF), sofern zertifiziert — sonst Art. 46 + SCC + AVV + TIA |

### 2.6§ Speicherfristen

| Datenkategorie | Speicherort | Inhalt | Frist | Grundlage |
|----------------|-------------|--------|-------|-----------|
| Chat-Nachrichten | Lokale SQLite-DB | Tokenisierte Texte (kein PII-Klartext) | 90 Tage (konfigurierbar: `AILIZA_DATA_RETENTION_DAYS`) | Art. 5 Abs. 1 lit. e DSGVO |
| Audit-Logs | Lokale SQLite-DB | Ausschließlich technische Metadaten: Zeitpunkt, Nutzer-ID, Fehlercodes, Systemereignisse — keine Prompt- oder Antwortinhalte | 90 Tage | Art. 30 DSGVO |
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

Daten werden ausschließlich für die vom Nutzer initiierte Anfrage verarbeitet. Kein Training von Modellen mit Nutzerdaten (vertraglich mit Groq/Tavily auszuschließen und zu dokumentieren).

### 3.4§ Transparenz (Art. 13 DSGVO)

- Informationsdialog beim ersten Start gemäß Art. 13 DSGVO
- KI-Disclosure bei jeder Antwort gemäß den Transparenzpflichten der Verordnung (EU) 2024/1689 (EU AI Act): Nutzer müssen erkennen können, dass sie mit einem KI-System interagieren
- Datenschutzerklärung: [LINK EINTRAGEN — noch zu erstellen]

### 3.5§ Technische und organisatorische Maßnahmen (Art. 32 DSGVO)

- HTTPS / TLS 1.2+ für alle Netzwerkverbindungen
- Zugriffsschutz durch konfigurierbaren PIN (`AILIZA_ACCESS_PIN`)
- Admin-Endpoints durch separates Admin-Token geschützt
- Rate Limiting (20 Anfragen/Minute pro IP)
- Input-Validierung gegen Injection-Angriffe
- SQLite-Datenbank lokal, kein externer Datenbankzugriff
- Automatisierter Retention-Daemon löscht Sessions nach konfigurierter Frist
- Backups der SQLite-Datenbank: verschlüsselt aufbewahren, Zugriff auf berechtigte Personen beschränken; Backups werden nach spätestens 90 Tagen (bzw. der konfigurierten `AILIZA_DATA_RETENTION_DAYS`-Frist) überschrieben oder gelöscht — die Backup-Aufbewahrungsfrist darf die Datenspeicherfrist nicht überschreiten (Art. 5 Abs. 1 lit. e DSGVO)

---

## 4§ Risikoanalyse

### 4.1§ Risikobewertung

| # | Risiko | Eintrittsw. | Schwere | Risiko gesamt | Maßnahme |
|---|--------|-------------|---------|---------------|----------|
| R1 | Unbeabsichtigte PII-Übermittlung an Groq | Mittel | Mittel | **Mittel** | PII-Tokenisierung, Warnhinweise |
| R2 | Drittland-Transfer ohne ausreichende Garantien (Groq/USA) | Mittel | Hoch | **Hoch** | DPF-Prüfung + ggf. SCC + AVV + TIA — vor Go-Live abschließen |
| R3 | Unberechtigter Zugriff auf Audit-Logs | Niedrig | Hoch | **Mittel** | Admin-Token-Schutz |
| R4 | Datenpanne durch Sicherheitslücke | Niedrig | Hoch | **Mittel** | HTTPS, Rate Limiting, Input-Validierung |
| R5 | Nutzer vertraut KI-Entscheidung blind | Mittel | Mittel | **Mittel** | KI-Disclosure nach EU AI Act (EU) 2024/1689, Human Oversight Banner |
| R6 | Eingabe besonderer Kategorien (Gesundheit, Gehalt, HR) durch Nutzer | Mittel | Sehr hoch | **Hoch** | Nutzerwarnungen, Nutzungsrichtlinie, technische PII-Erkennung |
| R7 | Datenverlust bei SQLite-Korruption | Niedrig | Niedrig | **Niedrig** | Regelmäßige Backups |
| R8 | Zugriff auf unverschlüsselte Backups | Niedrig | Hoch | **Mittel** | Verschlüsselung aller Backups, Zugriffskontrollen, Löschkonzept |

### 4.2§ Verbleibende Risiken nach Maßnahmen

- **R2 (Drittland-Transfer):** Verbleibt hoch solange DPF-Status unklar und AVV/TIA nicht abgeschlossen. Nach vollständigem Nachweis: vertretbar.
- **R5 (Blinde KI-Vertrauung):** Strukturelles Restrisiko — reduziert durch Pflicht-Disclosure, nicht vollständig eliminierbar.
- **R6 (Besondere Kategorien):** Verbleibt solange Freitexteingabe möglich. Reduziert durch Nutzerschulung und technische Warnhinweise, aber nicht vollständig ausschließbar.

**Gesamtbewertung:** Vertretbares Restrisiko nach vollständiger Umsetzung aller Maßnahmen. Ob eine Konsultationspflicht nach Art. 36 DSGVO entfällt, ist im Einzelfall zu prüfen — insbesondere für R2 und R6 (siehe §6).

---

## 5§ Geplante Maßnahmen und Verantwortlichkeiten

| Maßnahme | Verantwortlich | Frist | Status |
|----------|---------------|-------|--------|
| DPF-Zertifizierung Groq prüfen (dataprivacyframework.gov) | [DSB / IT-Admin] | Vor Go-Live | ☐ Offen |
| DPF-Zertifizierung Tavily prüfen (falls genutzt) | [DSB / IT-Admin] | Vor Aktivierung | ☐ Offen |
| AVV mit Groq unterzeichnen | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| AVV mit Tavily (falls genutzt) | [GESCHÄFTSFÜHRUNG] | Vor Aktivierung | ☐ Offen |
| TIA für Groq dokumentieren (falls kein DPF) | [DSB] | Vor Go-Live | ☐ Offen |
| TIA für Tavily dokumentieren (falls kein DPF) | [DSB] | Vor Aktivierung | ☐ Offen |
| Kein Modell-Training durch Groq/Tavily vertraglich sicherstellen | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| Datenschutzerklärung veröffentlichen | [DSB / ANWALT] | Vor Go-Live | ☐ Offen |
| Impressum prüfen (DDG §5) | [GESCHÄFTSFÜHRUNG] | Vor Go-Live | ☐ Offen |
| `AILIZA_COMPANY_NAME` und `AILIZA_DSB_EMAIL` in `.env` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| `AILIZA_ACCESS_PIN` setzen | IT-Admin | Vor Go-Live | ☐ Offen |
| Backups verschlüsseln, Zugriffskonzept und Löschkonzept dokumentieren | IT-Admin | Vor Go-Live | ☐ Offen |
| Mitarbeitende gemäß Art. 13 DSGVO informieren | HR / DSB | Vor Inbetriebnahme | ☐ Offen |
| Nutzungsrichtlinie: keine besonderen Kategorien eingeben | HR / DSB | Vor Inbetriebnahme | ☐ Offen |
| Beschäftigtendatenschutz §26 BDSG prüfen (Betriebsrat falls vorhanden) | [GESCHÄFTSFÜHRUNG / DSB] | Vor Inbetriebnahme | ☐ Offen |
| Regelmäßige DPIA-Überprüfung | DSB | Jährlich | ☐ Wiederkehrend |

---

## 6§ Konsultation Datenschutzbehörde (Art. 36)

Eine vorherige Konsultation der zuständigen Aufsichtsbehörde ist nicht erforderlich, wenn nach Umsetzung aller Maßnahmen kein hohes Restrisiko verbleibt.

Bleibt insbesondere beim Drittlandtransfer (R2), bei besonderen Kategorien personenbezogener Daten (R6) oder bei Beschäftigtendaten ein hohes Restrisiko bestehen — etwa weil AVV/TIA nicht abgeschlossen werden können oder der DPF-Status negativ ausfällt — ist eine vorherige Konsultation der zuständigen Aufsichtsbehörde nach Art. 36 DSGVO zu prüfen.

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

*Diese DPIA-Vorlage wurde auf Basis der AILIZA-Systemarchitektur (Stand 18.06.2026) erstellt und juristisch überarbeitet (v1.3). Sie ersetzt keine individuelle Rechtsberatung. Bei Unsicherheiten einen auf Datenschutzrecht spezialisierten Rechtsanwalt oder den betrieblichen Datenschutzbeauftragten hinzuziehen.*

*Regulatorischer Kontext: DSGVO (EU) 2016/679 · Verordnung (EU) 2024/1689 (EU AI Act) · BDSG 2018 · DDG · TDDDG · EuGH C-311/18 (Schrems II) · Angemessenheitsbeschluss (EU) 2023/1795 (EU-US DPF)*
