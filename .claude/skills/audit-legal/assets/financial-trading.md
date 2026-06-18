# Deutsches Finanzmarktrecht — Überblick
# updated: 2026-06-11
# check-interval-days: 60
# sources:
#   KWG: https://www.gesetze-im-internet.de/kredwg/
#   WpIG: https://www.gesetze-im-internet.de/wpig/
#   WpHG: https://www.gesetze-im-internet.de/wphg/
#   ZAG: https://www.gesetze-im-internet.de/zag_2018/
#   KAGB: https://www.gesetze-im-internet.de/kagb/
#   GwG: https://www.gesetze-im-internet.de/gwg_2017/
#   GewO: https://www.gesetze-im-internet.de/gewo/
#   BaFin: https://www.bafin.de
#   MiFID II (EU): https://eur-lex.europa.eu/eli/dir/2014/65/oj/eng
#   MiCA (EU): https://eur-lex.europa.eu/eli/reg/2023/1114/oj/eng
# Hinweis: Gilt für Deutschland; EU-Recht ist ggf. direkt anwendbar. Keine Rechtsberatung.

## Scope-Trigger
Dieses Asset laden wenn das Projekt: Finanzprodukte (Aktien, ETFs, Fonds, Krypto,
Derivate, Versicherungen) anzeigt, vermittelt oder empfiehlt; Zahlungsdienste anbietet;
mit Banken oder Finanzdienstleistern zusammenarbeitet; oder Nutzer bei finanziellen
Entscheidungen unterstützt.

## 1. BaFin-Erlaubnispflichten — Überblick

| Tätigkeit | Rechtsgrundlage | Erlaubnis erforderlich |
|---|---|---|
| Bankgeschäfte (Einlagengeschäft, Kreditgeschäft) | KWG § 32 | BaFin-Erlaubnis als Kreditinstitut |
| Finanzdienstleistungen (Anlageberatung, -vermittlung, Portfolioverwaltung) | WpIG § 15 | BaFin-Erlaubnis als Wertpapierinstitut |
| Abschlussvermittlung von Investmentfondsanteilen (ohne vollständige WpIG-Lizenz) | GewO § 34f | IHK-Registrierung; kein BaFin-Kreditinstitut |
| Versicherungsvermittlung | GewO § 34d | IHK-Registrierung; Eintrag ins Vermittlerregister |
| Honorar-Finanzanlagenberatung | GewO § 34h | IHK-Registrierung; strengere Pflichten als 34f |
| Zahlungsdienste (Überweisung, Lastschrift, E-Geld) | ZAG §§ 10, 11 | BaFin-Erlaubnis als Zahlungsinstitut/E-Geld-Institut |
| Verwaltung von Investmentvermögen (Fonds) | KAGB § 20 | BaFin-Erlaubnis als KVG |
| Krypto-Verwahrgeschäft (Custodial Wallet) | KWG § 1 Abs. 1a Nr. 6 | BaFin-Erlaubnis |
| Krypto als CASP (Handel, Börse, Beratung) | MiCA (EU-Recht direkt) | BaFin-Zulassung als CASP ab 2025 |

## 2. Anlageberatung vs. Anlageempfehlung vs. Information

Anlageberatung (WpHG § 2 Abs. 8 Nr. 10): persönliche Empfehlung zu einem bestimmten
Finanzinstrument, die auf die Person des Kunden zugeschnitten ist oder als für ihn
geeignet dargestellt wird. Erfordert WpIG-Erlaubnis.

Anlageempfehlung (Marktempfehlung, WpHG § 85): allgemeine Empfehlung zu einem
Wertpapier (nicht personalisiert); strengere Dokumentationspflichten, aber keine
Beratungserlaubnis nötig.

Reine Information: Factual-Daten (Kurs, Fondszusammensetzung, historische Performance,
regulatorische Dokumente) ohne Personalisierung → keine Erlaubnis erforderlich.

Entscheidungshilfe:

| Merkmal | Einordnung |
|---|---|
| Kursanzeige, Factsheets, ETF-Datenblatt für alle gleich | Information — keine Erlaubnis |
| "Top 5 ETFs dieser Woche" für alle Nutzer gleich | ggf. Anlageempfehlung (§85 WpHG) — prüfen |
| "Dieser ETF passt zu Ihrem Risikoprofil" (personalisiert) | Anlageberatung — WpIG-Erlaubnis |
| Robo-Advisor mit Fragebogen und individueller Portfolioempfehlung | Anlageberatung — WpIG-Erlaubnis |
| Disclaimer allein verhindert Einstufung als Beratung NICHT | BaFin-Position |

## 3. Geldwäschegesetz (GwG)

Verpflichtete nach GwG §2: Kredit- und Finanzinstitute, Versicherungsunternehmen,
Kapitalverwaltungsgesellschaften, Güterhändler (ab 10.000 EUR Barzahlung),
Rechtsanwälte/Steuerberater bei bestimmten Tätigkeiten.

Pflichten der Verpflichteten:
- Risikomanagementsystem einrichten
- Kunden identifizieren (KYC: Know Your Customer) — Personalausweis, Handelsregister
- Wirtschaftlich Berechtigten ermitteln (Transparenzregister)
- Verdächtige Transaktionen der Financial Intelligence Unit (FIU) melden
- Mitarbeiter schulen; interne Sicherungsmaßnahmen dokumentieren

## 4. Verbraucherschutz bei Finanzprodukten

| Regelung | Inhalt |
|---|---|
| WpHG §§ 63 ff | Wohlverhaltensregeln: Interessenkonflikt, Eignung, Geeignetheitsprüfung |
| PRIIPs (EU-VO) | Key Information Document (KID) muss vor Anlageentscheidung ausgehändigt werden |
| KAGB §§ 297 ff | Wesentliche Anlegerinformationen (wAI) für Investmentfonds |
| PAngV | Preisangaben transparent; keine versteckten Kosten |
| Fernabsatzrecht (BGB § 312d) | Widerrufsrecht bei Online-Abschluss von Finanzdienstleistungen; 14 Tage |

## 5. Krypto (MiCA — EU-Recht, direkt anwendbar ab 2024/2025)

| Tätigkeit | MiCA-Pflicht |
|---|---|
| Non-custodial Wallet (Nutzer hält selbst Keys) | Kein MiCA-Erfordernis |
| Custodial Wallet (Anbieter hält Keys) | CASP-Zulassung erforderlich |
| Krypto-Börse / Trading-Plattform | CASP-Zulassung erforderlich |
| Krypto-Beratung | CASP-Zulassung + Personalanforderungen |
| Preisaggregator ohne Custody | In der Regel kein MiCA-Erfordernis |
| Stablecoins ausgeben | Zusätzliche Anforderungen (ART/EMT-Regime) |

Krypto als Finanzinstrument (Security Token): fällt unter KWG/WpIG, nicht MiCA —
strenge BaFin-Regulierung. Abgrenzung Security vs. Utility Token ist rechtlich komplex.

## 6. Versicherung (VAG / GewO §34d)

Versicherungsprodukte dürfen nur vermittelt werden von:
- Versicherungsmaklern (GewO §34d): im Auftrag des Kunden; unabhängig; IHK-Register
- Versicherungsvertretern (GewO §34d): im Auftrag eines oder mehrerer Versicherer
- Gebundene Vermittler: für einen einzigen Versicherer; vereinfachte Anforderungen

InsurTech / digitale Versicherungsvergleiche: gelten als Vermittlung; §34d-Zulassung erforderlich.

## Compliance-Checkliste

- [ ] Erlaubnispflichtige Tätigkeit geprüft (KWG, WpIG, ZAG, KAGB, GewO §34f/d/h)?
- [ ] Anlageberatung vs. Information klar abgegrenzt; keine personalisierte Empfehlung ohne WpIG-Erlaubnis?
- [ ] GwG: KYC-Prozess vorhanden wenn als Verpflichteter eingestuft?
- [ ] PRIIPs/wAI: KID-/wAI-Dokument vor Abschluss aushändigen?
- [ ] Krypto: Custody-Frage geklärt; MiCA-Pflicht geprüft?
- [ ] Versicherungsvermittlung: §34d-Registrierung bei IHK vorhanden?
- [ ] Fernabsatzrecht: Widerrufsbelehrung für Online-Finanzprodukte?
- [ ] Interessenkonflikte dokumentiert und offengelegt (WpHG §63)?
