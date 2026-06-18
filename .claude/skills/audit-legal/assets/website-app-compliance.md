# Deutsches Internet- und App-Recht — Überblick
# updated: 2026-06-11
# check-interval-days: 90
# sources:
#   DDG (Impressum §5): https://www.gesetze-im-internet.de/ddg/
#   TTDSG (Cookies §25): https://www.gesetze-im-internet.de/ttdsg/
#   UWG: https://www.gesetze-im-internet.de/uwg_2004/
#   BGB (AGB §305 ff; Fernabsatz §312 ff): https://www.gesetze-im-internet.de/bgb/
#   UrhG: https://www.gesetze-im-internet.de/urhg/
#   BFSG: https://www.gesetze-im-internet.de/bfsg/
#   DSGVO (EU): https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng
# Hinweis: Gilt für Deutschland. EU-Recht (DSGVO) ist direkt anwendbar. Keine Rechtsberatung.

## Scope-Trigger
Dieses Asset laden wenn das Projekt eine öffentlich zugängliche Website, Web-App,
mobile App oder ein SaaS-Produkt ist bzw. beinhaltet.

## 1. Impressumspflicht (DDG § 5, ex-TMG § 5)

Seit Mai 2023 gilt das Digitale-Dienste-Gesetz (DDG) als nationales Umsetzungsgesetz des DSA.
§ 5 DDG entspricht inhaltlich dem bisherigen § 5 TMG.

Pflichtangaben für geschäftsmäßige Telemedien (alle kommerziellen Websites/Apps):

| Angabe | Details |
|---|---|
| Name und Rechtsform | Natürliche oder juristische Person vollständig |
| Anschrift | Physische Adresse — kein Postfach |
| Schnelle elektronische Kontaktmöglichkeit | E-Mail-Adresse; Kontaktformular allein nicht ausreichend |
| Handelsregisternummer | Wenn eingetragen: Register + Nummer + zuständiges Gericht |
| USt-ID oder Wirtschafts-ID | Wenn vorhanden |
| Aufsichtsbehörde | Wenn erlaubnispflichtige Tätigkeit (BaFin, IHK etc.) |
| Berufsbezeichnung + Kammer | Bei reglementierten Berufen (Rechtsanwalt, Arzt etc.) |
| Verantwortlicher für redaktionelle Inhalte (§ 18 MStV) | Bei journalistisch-redaktionellen Angeboten |

Impressumspflicht gilt auch für: Apps (im Store und/oder in der App), Instagram/LinkedIn-Profile
mit kommerziellem Charakter, Sub-Domains, alle Sprach-Versionen.

Rechtsfolge bei Fehlen: Abmahnung durch Wettbewerber oder Verbraucherverbände (UWG §3a i.V.m. §5 DDG).

## 2. Datenschutzerklärung (DSGVO Art. 13/14 + BDSG)

Pflichtinhalt wenn personenbezogene Daten verarbeitet werden:
- Name und Kontaktdaten des Verantwortlichen + ggf. Datenschutzbeauftragter
- Zwecke und Rechtsgrundlagen der Verarbeitung (Art. 6 DSGVO)
- Empfänger oder Kategorien von Empfängern
- Drittlandübertragungen + Schutzmaßnahmen (Art. 46 DSGVO)
- Speicherdauer
- Betroffenenrechte: Auskunft, Berichtigung, Löschung, Einschränkung, Widerspruch, Portabilität
- Beschwerderecht bei Aufsichtsbehörde
- Hinweis auf Cookies/Tracking soweit eingesetzt

Datenschutzbeauftragter (DSB) erforderlich wenn (BDSG §38): >20 MA mit regelmäßiger
automatisierter Datenverarbeitung ODER bestimmte Kategorien (Scoring, Kranken-/Sozialdaten etc.).

## 3. Cookie-Einwilligung (TTDSG § 25)

TTDSG §25 (seit Dez. 2021): Speicherung von Informationen im Endgerät oder Zugriff auf
bereits gespeicherte Informationen erfordert Einwilligung — außer wenn unbedingt
erforderlich für den ausdrücklich gewünschten Dienst.

Einwilligungspflichtig:
- Analytics-Cookies (Google Analytics, Matomo ohne Anonymisierung)
- Werbe- und Tracking-Cookies; Marketing-Pixel
- Social-Media-Plugins mit Datenübertragung
- Session-Replay-Tools (Hotjar etc.)

Einwilligungsfrei:
- Session-Cookies für Navigation
- Login-Cookies (Authentifizierung)
- Warenkorb-Cookies
- Cookie-Präferenz-Speicherung selbst
- Technisch notwendige Load-Balancer-Cookies

Anforderungen an Einwilligung: vor Setzen der Cookies; opt-in (kein vorgesetztes Häkchen);
genauso einfach widerrufbar wie erteilbar; keine "Cookie-Walls" die Dienst von Einwilligung
abhängig machen (EuGH + OLG-Rechtsprechung).

## 4. AGB-Recht (BGB §§ 305–310)

Allgemeine Geschäftsbedingungen sind vorformulierte Vertragsbedingungen die für eine
Vielzahl von Verträgen gestellt werden.

Unwirksamkeitsrisiken (Auswahl):
- Überraschende Klauseln (§ 305c BGB): Bedingungen die Nutzer nicht erwarten müssen
- Unangemessene Benachteiligung (§ 307 BGB): Generalklausel; weiter Anwendungsbereich
- Haftungsausschluss für Vorsatz/grobe Fahrlässigkeit: unwirksam (§ 309 Nr. 7 BGB)
- Einseitige Änderungsrechte ohne sachlichen Grund: unwirksam (§ 308 Nr. 4 BGB)
- Automatische Verlängerung von Jahresverträgen ohne ausreichende Widerrufsmöglichkeit

Einbeziehungsvoraussetzungen (§ 305 Abs. 2 BGB):
- Deutlicher Hinweis vor Vertragsschluss
- Möglichkeit der Kenntnisnahme (vollständiger Text abrufbar)
- Einverständnis des Nutzers

## 5. Fernabsatz / E-Commerce (BGB §§ 312 ff)

Gilt für Verbraucherverträge die ausschließlich über Fernkommunikationsmittel geschlossen werden.

Pflichtinformationen vor Vertragsschluss (Art. 246a EGBGB):
- Wesentliche Eigenschaften der Ware/Dienstleistung
- Gesamtpreis inkl. Steuern und Versandkosten (PAngV beachten)
- Identität und Anschrift des Unternehmers
- Widerrufsrecht und Bedingungen (wenn anwendbar)
- Laufzeit bei Abonnements; Mindestvertragslaufzeit

Widerrufsrecht (§ 355 BGB): 14 Tage ohne Angabe von Gründen bei Fernabsatzverträgen.
Beginn: Tag nach Vertragsschluss (Dienstleistungen) oder Warenerhalt.
Digitale Inhalte: Widerruf erlischt wenn Ausführung mit ausdrücklicher Einwilligung + Kenntnis
des Erlöschens begonnen wurde.

Button-Lösung (§ 312j Abs. 3 BGB): Bestellbutton muss "Zahlungspflichtig bestellen"
oder vergleichbaren eindeutigen Text tragen. "Weiter", "Anmelden", "Bestätigen" → unwirksam.

## 6. Wettbewerbsrecht (UWG)

Verboten: Irreführende Werbung (§ 5 UWG), aggressive Geschäftspraktiken (§ 4a UWG),
unerlaubte E-Mail-Werbung ohne Einwilligung (§ 7 UWG).

Für Apps/Websites relevant:
- Dark Patterns die Nutzer zu ungewollten Käufen drängen: UWG §4a + ggf. DSGVO-Verstoß
- Gefälschte Bewertungen oder irreführende Testimonials: §5 UWG
- Preisvergleiche ohne vollständige Informationen: §5a UWG
- Subscribe-and-Save-Fallen (Abo versteckt): §5 UWG + §312j BGB

## 7. Urheberrecht (UrhG)

Für Websites und Apps relevant:
- Bilder, Fotos, Texte: nur mit Lizenz oder CC-Lizenz verwenden; Urhebervermerk pflegen
- Fonts: kommerzielle Nutzung prüfen (Google Fonts DSGVO-Konformität umstritten: lokales Hosting empfohlen)
- Code: Open-Source-Lizenzen beachten (GPL, MIT, Apache); GPL viral effect
- Software-Haftung: Urheberrechtsverletzungen im Code können teuer werden

## 8. Barrierefreiheit (BFSG — Barrierefreiheitsstärkungsgesetz)

Ab 28. Juni 2025: Barrierefreiheitspflicht für private Anbieter von:
- E-Commerce-Websites und -Apps
- Banking-Apps und digitale Finanzdienstleistungen
- Telekommunikationsdienste
- E-Books und Lesegeräte

Kleinstunternehmen-Ausnahme: <10 MA UND Jahresumsatz/Bilanzsumme ≤2 Mio. EUR.

Standard: EN 301 549 v3.2.1 (enthält WCAG 2.1 Level AA).
Mindestanforderungen: Tastaturnavigation, Screenreader-Kompatibilität, ausreichender
Farbkontrast, Textalternativen für Nicht-Text-Inhalte, Untertitel für Videos.

## Compliance-Checkliste

- [ ] Impressum vorhanden; alle Pflichtangaben nach DDG §5 enthalten
- [ ] Datenschutzerklärung aktuell; alle Art. 13/14 DSGVO-Angaben enthalten
- [ ] Cookie-Einwilligung vor dem Setzen nicht-essentieller Cookies (TTDSG §25)
- [ ] Cookie-Banner: opt-in, gleichwertiger Widerruf, keine Cookie-Wall
- [ ] AGB: vollständig abrufbar vor Vertragsschluss; keine sittenwidrigen Klauseln
- [ ] Button-Lösung: Bestellbutton korrekt beschriftet (§312j BGB)
- [ ] Widerrufsbelehrung erteilt und Widerrufsformular bereitgestellt
- [ ] Werbe-E-Mails: Double-Opt-In-Verfahren; Einwilligung dokumentiert
- [ ] Bilder/Fonts/Code: Lizenzen geprüft; UrhG-konform eingesetzt
- [ ] BFSG-Pflicht ab Juni 2025 geprüft; WCAG 2.1 AA umgesetzt oder Ausnahme dokumentiert
