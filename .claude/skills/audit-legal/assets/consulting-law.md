# Deutsches Beratungsrecht — Überblick
# updated: 2026-06-11
# check-interval-days: 90
# sources:
#   RDG: https://www.gesetze-im-internet.de/rdg/
#   StBerG: https://www.gesetze-im-internet.de/stberg/
#   WPO: https://www.gesetze-im-internet.de/wpo/
#   BRAO: https://www.gesetze-im-internet.de/brao/
#   GewO (§34f/d/h): https://www.gesetze-im-internet.de/gewo/
#   BGB (§§280/311/675): https://www.gesetze-im-internet.de/bgb/
#   Heilpraktikergesetz: https://www.gesetze-im-internet.de/heilprg/
# Hinweis: Gilt für Deutschland. Keine Rechtsberatung.

## Scope-Trigger
Dieses Asset laden wenn das Projekt: Beratungsdienstleistungen anbietet oder abbildet,
KI-Empfehlungen in regulierten Bereichen gibt, Nutzer bei rechtlichen, steuerlichen,
medizinischen, finanziellen oder technischen Entscheidungen unterstützt.

## 1. Rechtsdienstleistungsgesetz (RDG)

### Was ist eine Rechtsdienstleistung? (§ 2 RDG)
Jede Tätigkeit in konkreten fremden Angelegenheiten, sobald sie eine rechtliche Prüfung
des Einzelfalls erfordert. Nicht darunter fällt: allgemeine rechtliche Information,
die keine individuelle Prüfung enthält.

### Wer darf Rechtsdienstleistungen erbringen? (§ 3 RDG)
Ausschließlich:
- Rechtsanwälte (BRAO)
- Steuerberater und Wirtschaftsprüfer (im steuerrechtlichen Bereich)
- Notare (im notariellen Bereich)
- Rentenberater (§ 10 RDG: registrierungspflichtig, beschränkter Bereich)
- Registrierte Personen für spezifische Bereiche (§ 10 RDG)

### Erlaubte Nebenleistungen (§ 5 RDG)
Nicht-Anwälte dürfen Rechtsdienstleistungen als Nebenleistung erbringen wenn:
- die Tätigkeit ihrem Berufsfeld entspricht (z.B. Unternehmensberater erstellt Vertragsklausel
  als Annexleistung zur Unternehmensberatung)
- die rechtliche Beurteilung von untergeordneter Bedeutung ist
- keine eigenständige Rechtsberatung im Mittelpunkt steht

### Relevanz für Software/KI-Tools
Graubereich: Tools die konkrete juristische Prüfung des Einzelfalls vornehmen
(z.B. "Ist meine Kündigung rechtswirksam?") können unter RDG fallen.
Zulässig: Bereitstellung von Rechtsinformationen, Formularen, allgemeinen Erklärungen.
Unzulässig ohne Anwalts-/Steuerberaterintegration: individuelle Vertragsprüfung,
individuelles Rechtsgutachten, Klageschrift-Erstellung für konkrete Parteien.

Rechtsfolge bei Verstoß: Ordnungswidrigkeit; Abmahnung durch Anwaltskammer; zivilrechtliche
Nichtigkeit der erbrachten Leistung.

## 2. Steuerberatungsgesetz (StBerG)

### Vorbehaltene Tätigkeiten (§ 4 StBerG)
Nur Steuerberater, Steuerbevollmächtigte, Wirtschaftsprüfer und Rechtsanwälte dürfen:
- Steuerberatung (Deklarationsberatung: Steuererklärungen erstellen)
- Steuerplanung und -gestaltung für konkrete Mandanten
- Vertretung gegenüber Finanzbehörden und Finanzgerichten

### Erlaubte Tätigkeiten ohne Zulassung (§ 4 StBerG)
- Buchhalter/Buchführungshelfer: laufende Buchführung (nicht Jahresabschluss)
- Lohnabrechnung: Unternehmer für eigene Mitarbeiter
- Selbstauskunft: eigene Steuern ohne fremde Hilfe

### Relevanz für Software/KI-Tools
Steuersoftware (ELSTER, Steuererklärungsprogramme): Graubereich; zulässig als
Werkzeug das Nutzer bei der eigenen Steuererklärung unterstützt, ohne konkrete
individuelle Steuerberatung zu leisten.
Unzulässig: Software die als Steuerberater auftritt und für konkrete Kunden
Steuergestaltung empfiehlt (ohne lizenzierte Person dahinter).

## 3. Wirtschaftsprüfung (WPO)

Vorbehalten Wirtschaftsprüfern (§§ 2, 49 WPO):
- Gesetzliche Jahresabschlussprüfung von Kapitalgesellschaften (ab bestimmten Schwellen)
- Prüfung von Konzernabschlüssen
- Sonderprüfungen nach HGB/AktG

Nicht vorbehalten:
- Unternehmensberatung ohne Prüfungsauftrag
- Due-Diligence-Beratung (ohne Testat)
- Interne Revision

## 4. Medizinische und Heilberufe

### Wer darf Heilkunde ausüben?
Ausschließlich: Ärzte (Approbation), Zahnärzte, Psychotherapeuten, und registrierte
Heilpraktiker (eingeschränkt; Heilpraktikergesetz).

Heilkunde = jede berufs- oder gewerbsmäßig vorgenommene Tätigkeit zur Feststellung,
Heilung oder Linderung von Krankheiten, Leiden, Körperschäden.

### Relevanz für Gesundheits-Apps und KI-Medizin
- Diagnosesoftware: als Medizinprodukt (MDR/IVDR) klassifiziert wenn klinische Zweckbestimmung
- Symptom-Checker (allgemein): Graubereich; darf keine Diagnose treffen, nur informieren
- Telemedizin: Fernbehandlung nur über zugelassene Ärzte; Ärztliches Fernbehandlungsverbot
  gelockert (2019 MBO-Ä), aber weiterhin reguliert
- Digitale Gesundheitsanwendungen (DiGA): müssen beim BfArM als DiGA gelistet sein für
  GKV-Erstattung

## 5. Architekten und Ingenieure

Bauvorhaben: Planungsleistungen (Entwurf, Baugenehmigungsplanung) sind in den meisten
Bundesländern Architekten und Ingenieuren vorbehalten (Architekten- und Ingenieurkammergesetze
der Länder; Schutz der Berufsbezeichnung).
HOAI (Honorarordnung): regelt Mindest- und Höchsthonorare für Planungsleistungen; seit
2021 nur noch als Preisgrundlage, Unterschreitung nach EuGH-Urteil zulässig.

## 6. Unternehmensberatung (nicht reglementiert)

Der Beruf "Unternehmensberater" ist in Deutschland nicht reglementiert. Keine
Zulassungsvoraussetzungen für allgemeine Managementberatung, Prozessberatung, IT-Beratung,
Strategieberatung.

Grenzen: sobald steuerliche, rechtliche oder finanzielle Einzelfallberatung den Kern der
Leistung bildet → Abgrenzung zu RDG, StBerG, WpIG (s.o.).

Vertragsrecht: Werkvertrag (§ 631 BGB) oder Dienstvertrag (§ 611 BGB) je nach Ausgestaltung.
Werkvertrag: schuldrechtlicher Erfolg; bei Mängeln: Nacherfüllungs- und Gewährleistungsansprüche.
Dienstvertrag: kein Erfolg geschuldet; Abrechnung nach Zeit.

Haftung: Beraterhaftung aus §§ 280, 311 BGB; bei Vorsatz/grober Fahrlässigkeit unbegrenzt;
vertragliche Haftungsbeschränkung möglich (nicht für Vorsatz; für grobe FL bei Verbrauchern eingeschränkt).
Berufshaftpflicht: gesetzlich nicht für allgemeine Unternehmensberater vorgeschrieben;
empfohlen und von Auftraggebern oft gefordert.

## 7. Allgemeine Beraterhaftung

| Grundlage | Inhalt |
|---|---|
| § 280 BGB | Schadensersatz bei Pflichtverletzung aus Schuldverhältnis |
| § 311 Abs. 2 BGB | Vorvertragliches Schuldverhältnis (culpa in contrahendo); haftet schon bei Vertragsanbahnung |
| § 675 BGB | Entgeltlicher Geschäftsbesorgungsvertrag; Grundlage für Beratungsverträge |
| Expertenhaftung | Wer sich als Experte geriert, haftet nach dem Maßstab des Experten |
| Drittschadensliquidation | Haftung auch gegenüber Dritten bei erkennbarer Drittbezogenheit der Beratung |

## Compliance-Checkliste

- [ ] Bietet das Projekt Rechtsberatung an? → RDG: nur mit Anwälten im Hintergrund zulässig
- [ ] Bietet das Projekt Steuerberatung an? → StBerG: nur mit Steuerberatern/WP im Hintergrund
- [ ] Bietet das Projekt medizinische Diagnose oder Heilkunde an? → Approbation erforderlich; MDR/IVDR prüfen
- [ ] Ist die Tätigkeit als Unternehmensberatung abgegrenzt? → Überschneidungen mit RDG/StBerG/WpIG prüfen
- [ ] Haftungsbeschränkung in AGB/Vertrag enthalten? → AGB-Konformität nach BGB §307 prüfen
- [ ] Berufshaftpflichtversicherung vorhanden (für regulierte Berufe: gesetzlich; allgemein: empfohlen)?
- [ ] KI-Tools die Beratungsleistungen simulieren: Hinweis auf fehlende Zulassung + Empfehlung zugelassener Fachkräfte?
- [ ] Honorarvereinbarung schriftlich fixiert; Werkvertrag vs. Dienstvertrag bewusst gewählt?
