# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Monatlicher DPIA-Aktualisierungs-Checker
Prüft alle relevanten Gesetze via HEAD-Request auf Änderungen,
erstellt einen monatlichen Prüfbericht und aktualisiert das Datum
in der DPIA-Datei.

Aufruf (manuell oder per Task Scheduler):
    python -m apps.backend.compliance.dpia_updater
    python apps/backend/compliance/dpia_updater.py
"""

import re
import sqlite3
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── Pfade ────────────────────────────────────────────────────────────────────

_MODUL_DIR = Path(__file__).resolve().parent
ROOT = _MODUL_DIR.parent.parent.parent.parent  # ki-lisa root
# Fallback: wenn als Skript direkt ausgeführt (nicht als Modul)
if not (ROOT / "apps").exists():
    ROOT = _MODUL_DIR.parent.parent.parent

DOCS_DIR = ROOT / "docs"
DPIA_PFAD = DOCS_DIR / "DPIA_AILIZA_Art35_DSGVO.md"
UPDATES_DIR = DOCS_DIR / "DPIA_updates"
DB_PFAD = ROOT / "data" / "dpia_checks.db"

# ── Rechtsquellen ────────────────────────────────────────────────────────────

QUELLEN: dict[str, dict] = {
    "DSGVO": {
        "name": "DSGVO — (EU) 2016/679",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32016R0679",
        "dpia_abschnitte": ["3§ Rechtsgrundlagen", "5§ Betroffenenrechte", "6§ Risikobewertung"],
        "beschreibung": "EU-Datenschutz-Grundverordnung",
        "quelle_typ": "EUR-Lex",
    },
    "EU_AI_Act": {
        "name": "EU AI Act — (EU) 2024/1689",
        "url": "https://eur-lex.europa.eu/legal-content/DE/TXT/HTML/?uri=CELEX:32024R1689",
        "dpia_abschnitte": ["2§ Verarbeitungsbeschreibung", "4§ Risikoklassifizierung", "7§ Maßnahmen"],
        "beschreibung": "EU-Verordnung über Künstliche Intelligenz",
        "quelle_typ": "EUR-Lex",
    },
    "BDSG": {
        "name": "BDSG 2018",
        "url": "https://www.gesetze-im-internet.de/bdsg_2018/",
        "dpia_abschnitte": ["2§ Verarbeitungsbeschreibung", "3§ Rechtsgrundlagen (§26 Beschäftigte)"],
        "beschreibung": "Bundesdatenschutzgesetz — §26 Beschäftigtendatenschutz",
        "quelle_typ": "Gesetze-im-Internet",
    },
    "DDG": {
        "name": "DDG — Digitale-Dienste-Gesetz",
        "url": "https://www.gesetze-im-internet.de/ddg/",
        "dpia_abschnitte": ["2§ Verarbeitungsbeschreibung"],
        "beschreibung": "Umsetzung des Digital Services Act in Deutschland",
        "quelle_typ": "Gesetze-im-Internet",
    },
    "TDDDG": {
        "name": "TDDDG",
        "url": "https://www.gesetze-im-internet.de/tdddg/",
        "dpia_abschnitte": ["5§ Einwilligung / Cookies"],
        "beschreibung": "Telekommunikation-Digitale-Dienste-Datenschutz-Gesetz",
        "quelle_typ": "Gesetze-im-Internet",
    },
}

# ── Datenbank ─────────────────────────────────────────────────────────────────

def _db() -> sqlite3.Connection:
    DB_PFAD.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PFAD)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS dpia_checks (
            quelle        TEXT PRIMARY KEY,
            letzter_check TEXT,
            last_modified TEXT,
            etag          TEXT,
            geaendert     INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn


# ── HTTP HEAD ─────────────────────────────────────────────────────────────────

def _head(url: str) -> dict[str, str]:
    """Holt Last-Modified + ETag via HEAD-Request ohne Volltext-Download."""
    try:
        req = urllib.request.Request(
            url,
            method="HEAD",
            headers={"User-Agent": "AILIZA-DPIA-Checker/1.0 (compliance monitoring)"},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            return {
                "last_modified": r.headers.get("Last-Modified", ""),
                "etag": r.headers.get("ETag", ""),
            }
    except urllib.error.HTTPError as e:
        return {"fehler": f"HTTP {e.code}", "last_modified": "", "etag": ""}
    except Exception as e:
        return {"fehler": str(e), "last_modified": "", "etag": ""}


# ── Prüf-Logik ────────────────────────────────────────────────────────────────

def alle_quellen_pruefen() -> dict[str, dict]:
    """
    Prüft alle Rechtsquellen und gibt Ergebnis zurück.
    Speichert neuen Stand in DB, damit nächster Lauf Änderungen erkennt.
    """
    jetzt = datetime.now(timezone.utc).isoformat()
    ergebnis: dict[str, dict] = {}

    with _db() as conn:
        for key, meta in QUELLEN.items():
            kopf = _head(meta["url"])
            row = conn.execute(
                "SELECT last_modified, etag FROM dpia_checks WHERE quelle = ?", (key,)
            ).fetchone()
            alt_lm = row[0] if row else None
            alt_etag = row[1] if row else None

            neu_lm = kopf.get("last_modified", "")
            neu_etag = kopf.get("etag", "")
            fehler = kopf.get("fehler", "")

            # Als geändert werten wenn sich LM oder ETag geändert hat (und bekannt ist)
            lm_geaendert = bool(neu_lm and alt_lm and neu_lm != alt_lm)
            etag_geaendert = bool(neu_etag and alt_etag and neu_etag != alt_etag)
            geaendert = lm_geaendert or etag_geaendert

            conn.execute("""
                INSERT OR REPLACE INTO dpia_checks
                    (quelle, letzter_check, last_modified, etag, geaendert)
                VALUES (?, ?, ?, ?, ?)
            """, (key, jetzt, neu_lm or alt_lm or "", neu_etag or alt_etag or "", int(geaendert)))

            ergebnis[key] = {
                "name": meta["name"],
                "beschreibung": meta["beschreibung"],
                "geaendert": geaendert,
                "letzter_check": jetzt,
                "last_modified": neu_lm or alt_lm or "unbekannt",
                "dpia_abschnitte": meta["dpia_abschnitte"],
                "fehler": fehler,
                "erstmalig": alt_lm is None,
            }

    return ergebnis


# ── DPIA-Datei: Datum aktualisieren ──────────────────────────────────────────

def dpia_datum_aktualisieren(version_hinweis: str) -> bool:
    """
    Aktualisiert die Zeile 'Zuletzt überarbeitet' in der DPIA-Datei.
    Gibt True zurück wenn erfolgreich, False wenn Datei nicht gefunden.
    """
    if not DPIA_PFAD.exists():
        return False

    heute = datetime.now().strftime("%Y-%m-%d")
    inhalt = DPIA_PFAD.read_text(encoding="utf-8")

    # Pattern: **Zuletzt überarbeitet:** 2026-06-18 (v1.3: ...)
    muster = r"(\*\*Zuletzt überarbeitet:\*\*\s*)(.+)"
    neuer_wert = rf"\g<1>{heute} ({version_hinweis})"
    neuer_inhalt = re.sub(muster, neuer_wert, inhalt)

    if neuer_inhalt != inhalt:
        DPIA_PFAD.write_text(neuer_inhalt, encoding="utf-8")
        return True
    return False


# ── Monatsbericht generieren ──────────────────────────────────────────────────

def monatsbericht_erstellen(ergebnis: dict[str, dict]) -> Path:
    """
    Erstellt einen Markdown-Monatsbericht in docs/DPIA_updates/YYYY-MM.md
    Gibt den Pfad zur erstellten Datei zurück.
    """
    UPDATES_DIR.mkdir(parents=True, exist_ok=True)
    jetzt = datetime.now()
    dateiname = jetzt.strftime("%Y-%m") + ".md"
    bericht_pfad = UPDATES_DIR / dateiname

    geaenderte = [k for k, v in ergebnis.items() if v["geaendert"]]
    fehler_liste = [k for k, v in ergebnis.items() if v.get("fehler")]
    erstmalige = [k for k, v in ergebnis.items() if v.get("erstmalig")]

    zeilen = [
        f"# DPIA Monatsbericht — {jetzt.strftime('%B %Y')}",
        "",
        f"Erstellt: {jetzt.strftime('%Y-%m-%d %H:%M')}  ",
        f"Nächste Prüfung: 1. {_naechster_monat(jetzt)}  ",
        "",
        "---",
        "",
    ]

    # Zusammenfassung
    if geaenderte:
        zeilen += [
            "## Ergebnis: Änderungen erkannt — manuelle Prüfung erforderlich",
            "",
            f"Folgende Rechtsquellen haben sich seit dem letzten Check geändert:",
            "",
        ]
        for k in geaenderte:
            v = ergebnis[k]
            zeilen.append(f"- **{v['name']}** — {v['beschreibung']}")
            zeilen.append(f"  - Last-Modified: `{v['last_modified']}`")
            zeilen.append(f"  - DPIA-Abschnitte zur Prüfung: {', '.join(v['dpia_abschnitte'])}")
            zeilen.append("")
    elif erstmalige:
        zeilen += [
            "## Ergebnis: Erstmalige Prüfung — Basiszustand gespeichert",
            "",
            "Beim ersten Lauf werden keine Änderungen erkannt (kein Vergleichswert).",
            "Ab dem nächsten Monat werden Änderungen zuverlässig erkannt.",
            "",
        ]
    else:
        zeilen += [
            "## Ergebnis: Keine Änderungen erkannt",
            "",
            "Alle überwachten Rechtsquellen zeigen denselben Stand wie beim letzten Check.",
            "Die DPIA ist weiterhin aktuell — keine sofortige Anpassung erforderlich.",
            "",
        ]

    # Detailtabelle
    zeilen += [
        "---",
        "",
        "## Geprüfte Rechtsquellen",
        "",
        "| Kürzel | Gesetz | Stand | Geändert |",
        "|--------|--------|-------|----------|",
    ]
    for key, v in ergebnis.items():
        status = "⚠️ JA" if v["geaendert"] else ("🆕 Erstmalig" if v.get("erstmalig") else "✅ Nein")
        lm = v["last_modified"][:16] if len(v["last_modified"]) > 16 else v["last_modified"]
        fehler = f" ⛔ {v['fehler']}" if v.get("fehler") else ""
        zeilen.append(f"| {key} | {v['name']} | {lm}{fehler} | {status} |")

    zeilen += [""]

    # Prüfpunkte wenn Änderungen
    if geaenderte:
        zeilen += [
            "---",
            "",
            "## Pflicht-Prüfpunkte (bei Änderungen)",
            "",
            "Folgende DPIA-Abschnitte MÜSSEN von einer rechtskundigen Person geprüft werden:",
            "",
        ]
        geprueft: set[str] = set()
        for k in geaenderte:
            for abschnitt in ergebnis[k]["dpia_abschnitte"]:
                if abschnitt not in geprueft:
                    zeilen.append(f"- [ ] `{abschnitt}` — wegen Änderung in: {ergebnis[k]['name']}")
                    geprueft.add(abschnitt)

        zeilen += [
            "",
            "Weitere Standardprüfpunkte (jährlich, unabhängig von Änderungen):",
            "",
            "- [ ] Sind die eingetragenen Firmendaten (Adresse, DSB) noch aktuell?",
            "- [ ] Hat sich die Anzahl der Nutzer oder Datenkategorien wesentlich geändert?",
            "- [ ] Wurden neue Auftragsverarbeiter (z.B. neuer LLM-Anbieter) eingesetzt?",
            "- [ ] Sind AVV-Verträge mit Groq und Tavily noch gültig und aktuell?",
            "- [ ] Wurde AILIZA in neue Hochrisikobereiche eingesetzt?",
            "",
        ]

    # Hinweis auf nächste Schritte
    zeilen += [
        "---",
        "",
        "## Nächste Schritte",
        "",
    ]
    if geaenderte:
        zeilen += [
            "1. Bericht an Datenschutzbeauftragten (DSB) weiterleiten.",
            "2. Betroffene DPIA-Abschnitte mit Rechtsanwalt oder DSB überarbeiten.",
            "3. DPIA-Versionsnummer erhöhen (z.B. v1.3 → v1.4).",
            "4. Aktualisierte DPIA intern freigeben und ablegen.",
            "5. Ggf. Art. 36 DSGVO-Konsultation bei der Aufsichtsbehörde prüfen.",
            "",
        ]
    else:
        zeilen += [
            "1. Bericht archivieren (Nachweis für DSGVO Art. 5 Abs. 2 Rechenschaftspflicht).",
            "2. Keine weiteren Maßnahmen erforderlich.",
            "",
        ]

    zeilen += [
        "---",
        "",
        "*Automatisch erstellt von AILIZA DPIA-Updater — Überprüfung durch rechtskundige Person erforderlich.*",
        f"*Nächste automatische Prüfung: 1. {_naechster_monat(jetzt)}*",
    ]

    bericht_pfad.write_text("\n".join(zeilen), encoding="utf-8")
    return bericht_pfad


def _naechster_monat(dt: datetime) -> str:
    if dt.month == 12:
        return datetime(dt.year + 1, 1, 1).strftime("%B %Y")
    return datetime(dt.year, dt.month + 1, 1).strftime("%B %Y")


# ── Hauptfunktion ─────────────────────────────────────────────────────────────

def monatliche_aktualisierung() -> dict:
    """
    Führt die vollständige monatliche DPIA-Aktualisierung durch:
    1. Alle Quellen prüfen
    2. Monatsbericht erstellen
    3. DPIA-Datum aktualisieren wenn Änderungen
    Gibt Zusammenfassung zurück.
    """
    print("[DPIA-Updater] Starte monatliche Rechtsprüfung ...", flush=True)

    ergebnis = alle_quellen_pruefen()
    geaenderte = [k for k, v in ergebnis.items() if v["geaendert"]]

    bericht = monatsbericht_erstellen(ergebnis)
    print(f"[DPIA-Updater] Monatsbericht erstellt: {bericht}", flush=True)

    dpia_aktualisiert = False
    if geaenderte:
        hinweis = f"Automatisch aktualisiert — Änderungen in: {', '.join(geaenderte)} — manuelle Rechtsprüfung erforderlich"
        dpia_aktualisiert = dpia_datum_aktualisieren(hinweis)
        if dpia_aktualisiert:
            print(f"[DPIA-Updater] DPIA-Datum aktualisiert: {DPIA_PFAD}", flush=True)
        print(
            f"[DPIA-Updater] ⚠️  ACHTUNG: Änderungen erkannt in {geaenderte}. "
            f"Bitte DPIA manuell prüfen und ggf. Datenschutzbeauftragten informieren.",
            flush=True,
        )
    else:
        print("[DPIA-Updater] Keine Änderungen — DPIA ist aktuell.", flush=True)

    return {
        "ergebnis": ergebnis,
        "geaenderte_quellen": geaenderte,
        "bericht_pfad": str(bericht),
        "dpia_datum_aktualisiert": dpia_aktualisiert,
    }


if __name__ == "__main__":
    zusammenfassung = monatliche_aktualisierung()
    geaendert = zusammenfassung["geaenderte_quellen"]
    if geaendert:
        print(f"\n  Änderungen erkannt in: {', '.join(geaendert)}")
        print(f"  Bericht: {zusammenfassung['bericht_pfad']}")
        sys.exit(1)  # Exit-Code 1 signalisiert Handlungsbedarf
    else:
        print(f"\n  Alles aktuell. Bericht: {zusammenfassung['bericht_pfad']}")
        sys.exit(0)
