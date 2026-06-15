# AILIZA — Windows App bauen
© 2026 Karola Fromm-Nasreldin | Alle Rechte vorbehalten

## Was entsteht

Ein `dist/AILIZA/` Ordner mit:
```
AILIZA/
├── AILIZA.exe          ← Hauptprogramm
├── AILIZA starten.bat  ← Einfacher Starter für Nutzer
├── .env.example        ← Vorlage für API-Key
└── (weitere Dateien)
```

Der Nutzer entpackt den ZIP-Ordner, trägt seinen API-Key in `.env` ein und klickt auf `AILIZA starten.bat`.

## Voraussetzungen (auf deinem Windows-PC)

- Python 3.11 oder neuer → https://www.python.org/downloads/
- Beim Installieren: **"Add Python to PATH" ankreuzen!**

## App bauen

```
Doppelklick auf: installer\build_windows.bat
```

Das dauert 2–5 Minuten. Danach liegt die fertige App in `dist\AILIZA\`.

## Weitergeben

1. `dist\AILIZA\` Ordner als ZIP komprimieren (Rechtsklick → Senden an → ZIP)
2. ZIP per E-Mail oder USB-Stick weitergeben
3. Nutzer entpackt ZIP
4. Nutzer öffnet `.env` und trägt GROQ_API_KEY ein
5. Doppelklick auf `AILIZA starten.bat` → fertig

## Für technisch versierte Nutzer

Der API-Key kommt kostenlos von: https://console.groq.com → API Keys → Create
