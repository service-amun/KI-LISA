# KI-LISA / AILIZA — Projekt-Kontext für Claude Code

> Vollständiger Kontext für KI-Assistenten zur Weiterarbeit an diesem Projekt.
> Stand: 14.06.2026 | Version: 0.3.0 (in Entwicklung)

---

## Was dieses Projekt ist

**KI-LISA** (auch: **AILIZA**) ist ein EU-konformer KI-Assistent für kleine und mittlere Unternehmen (KMU) in Europa. Zielgruppe: Mitarbeiter ohne IT-Kenntnisse in Sekretariat, Buchhaltung, Vertrieb, HR und Kundenservice — in Deutschland, Österreich, Schweiz und der EU.

- **Repository:** github.com/service-amun/ki-lisa
- **Sprache:** Python (FastAPI Backend) + HTML/JS (Frontend, kein Build-Step)
- **Compliance:** DSGVO + EU AI Act Art. 52 (Limited Risk)
- **Kritische Frist:** 02.08.2026 — vollständige EU AI Act Anwendbarkeit

---

## Strategische Ausrichtung

### Kernregel (Non-Negotiable)
> **Der KMU-Mitarbeiter darf KEINEN technischen Schritt machen müssen.**
> Eine Datei herunterladen → Doppelklick → fertig.
> Alles andere (API-Keys, Server, Updates) läuft im Hintergrund.

### Was NICHT vorhanden sein darf
- Kein Python-Installation durch den Nutzer
- Keine API-Keys die der Nutzer selbst beschaffen muss
- Keine Kommandozeile (CMD/Terminal) sichtbar für Nutzer
- Keine technischen Fehlermeldungen für Nutzer
- Keine Blockierung von Anfragen (nur gelbe Warnhinweise)

### Compliance-Verhalten
- **Warnen statt Blockieren** — bei DSGVO/PII-Erkennung kommt die Antwort trotzdem, mit gelbem `msg-warn`-Banner
- Ausnahme: Verbotene KI-Praktiken (EU AI Act Art. 5) werden blockiert
- Hochrisiko-Anfragen (Kredit, HR-Scoring, Medizin) → Human Oversight Warnung, keine automatische Entscheidung
- Jede KI-Antwort trägt den EU AI Act Art. 52 Disclaimer: "KI-generiert — AILIZA"

---

## Zielarchitektur (Soll-Zustand)

```
ki-lisa/
├── apps/
│   ├── backend/
│   │   ├── main.py                   ← FastAPI Hauptdatei (app = "app"), Port 8001
│   │   ├── agent_runtime.py          ← Agent-Logik (search/fetch Tools)
│   │   ├── gateway.py                ← Tool-Ausführung + Guardrails
│   │   ├── database.py               ← SQLite (agent_runs, audit, approvals)
│   │   ├── groq_client.py            ← Groq LLM Client mit Compliance-Kontext
│   │   ├── compliance_context.py     ← DSGVO + EU AI Act Artikel-DB + Kontext-Builder
│   │   ├── session_manager.py        ← Pro-Chat isolierter Compliance-Zwischenspeicher
│   │   ├── approval.py
│   │   ├── policy.py
│   │   ├── routers/
│   │   │   └── approvals.py          ← /approvals Endpoints
│   │   ├── compliance/
│   │   │   ├── dsgvo.py              ← DSGVO Art. 5, 6, 17, 20, 25, 30, 35
│   │   │   ├── eu_ai_act.py          ← EU AI Act Art. 9, 13, 14, 52
│   │   │   ├── weekly_checker.py     ← Wöchentlicher Compliance-Check
│   │   │   ├── scheduler.py
│   │   │   └── eurlex_connector.py   ← EUR-Lex Delta-Checker (HEAD-only, kein Volltext)
│   │   ├── audit/
│   │   │   └── audit_logger.py       ← Vollständiger Audit Trail (DSGVO Art. 30)
│   │   ├── skills/
│   │   │   ├── router_skill.py       ← Task-Router (regelbasiert, kein LLM nötig)
│   │   │   ├── guardrail_skill.py    ← DSGVO + EU AI Act Filter (vor/nach LLM)
│   │   │   └── reflection_skill.py   ← RAG Memory + Lernfähigkeit (SQLite)
│   │   └── tools/
│   │       └── standard_tools.py
│   └── frontend/
│       └── index.html                ← Dashboard (Chat, Projekte, Skills, Status)
├── data/                             ← SQLite DBs, Checksummen (gitignore)
├── docs/
│   ├── AILIZA_Master_Prompt.md       ← Vollständiges Anforderungsdokument
│   ├── AILIZA_Projektübersicht_v3.md
│   └── AILIZA_Team_Anleitung.md
├── policies/
│   └── eu_compliance_policy.md
├── .env.example                      ← Vorlage (niemals echte Keys committen)
├── start_ailiza.bat                  ← Windows Doppelklick-Start
├── requirements.txt
├── Procfile                          ← Railway: web: uvicorn apps.backend.main:app ...
└── railway.json                      ← Railway Deployment-Konfiguration
```

---

## Aktueller Repo-Stand

Das Repository enthält derzeit nur `README.md` und `LICENSE`. Alle unten beschriebenen Komponenten müssen noch angelegt werden. Die Dateien existieren als Referenz-Uploads aus einer früheren Claude.ai-Session.

---

## Backend-Architektur

### FastAPI (apps/backend/main.py)

**Bestehende / geplante Endpoints:**

| Methode | Pfad | Beschreibung |
|---------|------|-------------|
| GET | `/health` | Backend-Status |
| GET/POST | `/audit-logs` | Audit-Trail |
| POST | `/tools/search` | Tavily Web-Suche |
| POST | `/tools/fetch` | URL abrufen |
| POST | `/agent/run` | Agent-Lauf starten |
| GET | `/agent/runs` | Alle Runs |
| GET | `/agent/runs/{id}` | Einzelner Run |
| GET/POST | `/sessions` | Chat-Sessions erstellen/listen |
| GET | `/sessions/{id}` | Session laden |
| POST | `/sessions/{id}/chat` | Nachricht in Session schicken |
| DELETE | `/sessions/{id}` | Session löschen (DSGVO Art. 17) |
| GET | `/approvals` | Offene Genehmigungen |
| POST | `/approvals/{id}/approve` | Genehmigen |
| POST | `/approvals/{id}/reject` | Ablehnen |
| GET | `/llm/providers` | Verfügbare LLM-Anbieter |
| POST | `/llm/chat` | LLM-Chat (Admin-Feature, zentraler Key) |
| GET | `/ai/status` | Groq-Status prüfen |
| POST | `/ai/chat` | Groq-Chat mit Compliance-Kontext |
| GET | `/dashboard` | Frontend ausliefern |

**Wichtig beim Entwickeln:**
- IMMER gegen `/docs` (FastAPI OpenAPI) prüfen, nicht gegen veraltete Endpoint-Listen
- Deutsche Phantom-Endpoints (`/Gesundheit`, `/Genehmigungen`, `/agent/läuft`) existieren NICHT
- Rate Limiting: 20 Anfragen/Minute pro IP (`_rate_store` + `check_rate_limit`)

### LLM-Integration (Groq — zentraler Key)

```python
# .env (nur serverseitig, niemals im Frontend)
GROQ_API_KEY=gsk_...        # Pflicht — kostenlos auf console.groq.com
TAVILY_API_KEY=tvly_...     # Für Web-Suche
ANTHROPIC_API_KEY=sk-ant-...  # Optional für Premium-Modelle
```

**Groq-Modelle (bevorzugt, kostenlos):**
- `llama3-70b-8192` — Hauptmodell
- `llama3-8b-8192` — Schnell/einfach
- `mixtral-8x7b-32768` — Alternativ

**Anthropic-Modelle (wenn Anthropic-Key gesetzt):**
- `claude-haiku-4-5` — Günstig/schnell
- `claude-sonnet-4-6` — Komplex/kritisch

**Routing-Logik (RouterSkill):**
- SIMPLE (≤8 Wörter, FAQ-Pattern) → Cache / Groq 8B → ~50 Tokens
- MODERATE (allgemein) → Haiku → ~500 Tokens
- COMPLEX (Compliance, Code, Legal) → Sonnet → ~2000 Tokens
- CRITICAL (Hochrisiko-Compliance) → Sonnet + Human Oversight → ~3000 Tokens

### Session-Compliance-Zwischenspeicher

Kernfeature: Jeder Chat hat seinen **eigenen isolierten Compliance-Kontext**.

```python
# Jede Session akkumuliert:
session.active_dsgvo_articles    # Erkannte Artikel wachsen an, nie weniger
session.active_eu_ai_act_articles
session.accumulated_warnings     # Warnungen der gesamten Session
session.risk_level               # "low" → "high" (nur hochstufen)
session.requires_human_oversight # False → True (nie zurück)
```

Sessions beeinflussen sich gegenseitig **nicht**. Gelöschte Sessions verschwinden vollständig (DSGVO Art. 17).

---

## Frontend-Architektur

### Dashboard (apps/frontend/index.html)

Single-file HTML/JS — kein Build-Step, kein Framework. Direkt bearbeitbar.

**Tabs:**
- 💬 **Chat** — Haupt-Interface, LLM-Selector-Bar oben
- 📁 **Projekte** — Projekte erstellen/verwalten (localStorage)
- ⚡ **Skills** — Vordefinierte Prompt-Shortcuts
- 🛡 **Status** — Compliance, Genehmigungen, Runs

**KMU-Skills (im Skills-Tab):**

| ID | Icon | Name | Prompt-Präfix |
|----|------|------|---------------|
| web | 🔍 | Web-Suche | `Suche nach: ` |
| eu | ⚖️ | EU AI Act Check | `Prüfe EU AI Act Compliance: ` |
| dsgvo | 🔒 | DSGVO Analyse | `DSGVO-Analyse für: ` |
| url | 🌐 | URL abrufen | `https://` |
| sum | 📝 | Zusammenfassen | `Fasse zusammen: ` |
| mail | ✉️ | E-Mail verfassen | `Schreibe E-Mail: ` |
| risk | ⚠️ | Risikoanalyse | `Analysiere Risiko: ` |
| news | 📰 | News | `Neuigkeiten zu: ` |

**Frontend-Konventionen:**
- API-Base: `const API = "http://127.0.0.1:8001"` (lokal) oder Railway-URL
- Chat-History in `localStorage` (`ailiza_chat`, max 50 Nachrichten)
- Compliance-Warnungen: CSS-Klasse `msg-warn` (gelber Banner)
- AI-Disclaimer: CSS-Klasse `msg-meta` mit "AILIZA · EU AI Act Art. 52"
- Keine externen Abhängigkeiten — reines Vanilla JS

**LLM-Selector-Bar:** Wird für KMU-Modus AUSGEBLENDET (kein Nutzer-Key).
Admin-Modus kann sie zeigen. Standard: Groq-Backend-Key, unsichtbar für Nutzer.

---

## Compliance-Architektur

### DSGVO-Artikel (implementiert)

| Artikel | Beschreibung | Implementiert in |
|---------|-------------|-----------------|
| Art. 5 | Datensparsamkeit, Zweckbindung | `guardrail_skill.py`, `compliance_context.py` |
| Art. 6 | Rechtsgrundlage | `dsgvo.py` |
| Art. 13 | Transparenz | System-Prompt (immer aktiv) |
| Art. 17 | Recht auf Löschung | `DELETE /sessions/{id}` |
| Art. 20 | Datenportabilität | `dsgvo.py` |
| Art. 25 | Privacy by Design | Architektur-Prinzip |
| Art. 30 | Audit Trail | `audit_logger.py` |
| Art. 35 | DSFA | `dsgvo.py` |

### EU AI Act (implementiert)

| Artikel | Beschreibung | Implementiert in |
|---------|-------------|-----------------|
| Art. 5 | Verbotene Praktiken | `guardrail_skill.py` (BLOCK) |
| Art. 6 | Hochrisiko-Definition | `guardrail_skill.py` (WARN + Human Oversight) |
| Art. 9 | Risikomanagementsystem | `eu_ai_act.py` |
| Art. 13 | Transparenz | `compliance_context.py`, System-Prompt |
| Art. 14 | Menschliche Aufsicht | Approvals-System |
| Art. 52 | Transparenzpflicht (Limited Risk) | Jede KI-Antwort trägt den Disclaimer |

### PII-Erkennung (guardrail_skill.py)

Erkannte Muster (DSGVO Art. 4): E-Mail, Telefon (DE), IBAN (DE), IP-Adresse, Geburtsdatum, Personalausweis, Sozialversicherungsnummer.

**Verhalten:** PII wird im Log geschwärzt (`[EMAIL_GESCHWÄRZT]`), Nutzer bekommt Warnung, Antwort kommt trotzdem.

### Was AILIZA NICHT tun darf

- Kreditentscheidungen treffen (EU AI Act Art. 6, Anhang III)
- Einstellungs-/Kündigungsentscheidungen automatisiert
- Medizinische Diagnosen stellen
- Biometrische Überwachung
- Nutzer manipulieren (EU AI Act Art. 5)
- Social Scoring

---

## Entwicklungs-Workflow

### Lokaler Start

```bash
# Backend
cd /path/to/ki-lisa
python -m uvicorn apps.backend.main:app --port 8001 --reload

# Frontend: Browser öffnen
# http://127.0.0.1:8001/dashboard
```

### Umgebungsvariablen

```env
# apps/backend/.env — NIEMALS committen
GROQ_API_KEY=gsk_...              # Pflicht
TAVILY_API_KEY=tvly_...           # Für Web-Suche
ANTHROPIC_API_KEY=sk-ant-...      # Optional
AILIZA_DATA_RETENTION_DAYS=90     # DSGVO Datenhaltung
AILIZA_HUMAN_OVERSIGHT=true       # Human Oversight aktivieren
```

### Deployment (Railway)

```
1. railway.app → New Project → GitHub → service-amun/ki-lisa
2. Environment Variables setzen:
   GROQ_API_KEY=gsk_...
   TAVILY_API_KEY=tvly_...
3. Deploy
```

`Procfile`:
```
web: uvicorn apps.backend.main:app --host 0.0.0.0 --port $PORT
```

---

## Code-Konventionen

### Python (Backend)

- **Keine** externen Bibliotheken außer FastAPI, Pydantic, SQLite3, requests/urllib
- Compliance-Checks laufen **VOR und NACH** jedem LLM-Aufruf (Input + Output Guardrail)
- Audit-Logging bei JEDER AI-Antwort: Modell, Tokens, Compliance-Summary, IP (gehasht)
- Keine echten Fehlermeldungen an den Nutzer — nur benutzerfreundliche Texte
- SQLite für alle persistenten Daten (`data/` Verzeichnis, gitignored)
- Rate Limiting immer aktiv: `check_rate_limit(request)` in jedem Chat-Endpoint

### HTML/JS (Frontend)

- Keine externen CDN-Abhängigkeiten — alles inline
- CSS kompakt (minified-Stil in einer `<style>`-Sektion)
- `localStorage` für Client-State (Chat-History, API-Keys wenn nötig)
- Kein Nutzerfehler darf als technische Exception erscheinen
- Typing-Indikator (`showTyping()`/`hideTyping()`) bei jeder AI-Anfrage
- Compliance-Footer in jeder AI-Nachricht: `.msg-meta` mit Art. 52 Hinweis

### Git

- Branch für diese Session: `claude/claude-md-docs-ssfhys`
- Commit-Messages auf Englisch, Beschreibungen können Deutsch sein
- Niemals committen: `.env`, `data/`, `*.db`, API-Keys
- Feature-Branches von `main` abzweigen

---

## Komponenten-Status

### Fertig (aus Referenz-Session, noch nicht im Repo)

| Datei | Zweck |
|-------|-------|
| `compliance_context.py` | DSGVO + EU AI Act Artikel-DB + System-Prompt-Builder |
| `session_manager.py` | Pro-Chat Compliance-Zwischenspeicher (SQLite) |
| `groq_client.py` (v2) | Groq LLM Client mit automatischem Compliance-Kontext |
| `skills/guardrail_skill.py` | Zweistufiger PII/Compliance-Filter |
| `skills/router_skill.py` | Regelbasierter Task-Router (ohne LLM) |
| `skills/reflection_skill.py` | RAG Memory Manager (SQLite-basiert) |
| `compliance/eurlex_connector.py` | EUR-Lex Delta-Checker (HEAD-only) |
| `frontend/index.html` | Dashboard v5 (Chat/Projekte/Skills/Status) |

### Zu bauen / zu verdrahten

1. **GROQ_API_KEY** in `apps/backend/.env` eintragen
2. **`compliance_context.py` + `session_manager.py`** in `main.py` verdrahten
3. **Session-Endpoints** (`/sessions/...`) in `main.py` aktivieren
4. **Frontend** auf `/sessions/{id}/chat` statt direkt `/agent/run` umstellen
5. **LLM-Selector-Bar** für KMU-Modus ausblenden (zentraler Groq-Key)
6. **Deployment** auf Railway neu aufsetzen (korrektes Repo, ENV-Vars)

### Geplant (aus AILIZA-Vergleich, noch nicht eingebaut)

Diese 3 Punkte wurden aus dem AILIZA-Konzept (ChatGPT, 15.06.2026) als sinnvoll bewertet
und sollen in einer späteren Session eingebaut werden:

1. **Orange-Stufe im Guardrail** (`guardrail_skill.py`)
   - Zwischen Gelb (Warnung) und Rot (Block) eine Freigabe-Stufe einführen
   - Orange = Admin oder verantwortliche Person muss bestätigen, bevor die Aktion ausgeführt wird
   - Anwendungsfall: externe Versendung, Datenexport, Hochrisiko-Anfragen
   - Umsetzung: `GuardrailResult.risk_level: "green" | "yellow" | "orange" | "red"`

2. **Secret-Klasse für Passwörter/Tokens** (`guardrail_skill.py`)
   - Eigener Erkennungstyp: Passwörter, API-Keys, Tokens (z.B. `gsk_`, `sk-`, `password=`)
   - Verhalten: Rot blockiert + wird NICHT ins Audit-Log geschrieben (Datensparsamkeit)
   - Umsetzung: neues Pattern `"Zugangsdaten"` mit `risk="red"` und `log=False`

3. **Vault-Ablaufzeit** (`main.py`, `_pii_zwischenspeicher`)
   - Jeder Platzhalter-Eintrag bekommt ein `expires_at` (Standard: 30 Minuten)
   - Nach Ablauf wird der Eintrag automatisch aus dem RAM gelöscht
   - Umsetzung: `_pii_zwischenspeicher[session_id] = {"map": token_map, "expires": time.time() + 1800}`
   - Cleanup-Funktion bei jedem Chat-Request aufrufen

### Bewusst NICHT eingebaut (verworfen)

- `llm_router.py` — Nutzer-API-Key-Eingabe widerspricht KMU-Anforderung
- Blockierende Guardrails — ersetzt durch Warn-only Ansatz
- Komplexer Super-Agent-Orchestrator — zu aufwändig für KMU-Fokus
- E-Mail direkt versenden — bräuchte SMTP/Outlook-Integration, falscher Scope für MVP
- 6-Klassen-Datensystem (AILIZA) — unsere 4 PII-Typen decken 90% der KMU-Fälle

---

## Bewertungskriterien für Entscheidungen

| Kriterium | Gewichtung |
|-----------|-----------|
| Einfachheit für Nutzer | 40% |
| DSGVO / EU AI Act Konformität | 30% |
| Geschwindigkeit der Antworten | 20% |
| Kosten für KMU | 10% |

---

## Häufige Fallstricke

1. **Endpoint-Mismatch** — ältere Frontend-Versionen riefen deutsche Phantasie-Endpoints auf. Immer gegen FastAPI `/docs` prüfen.
2. **API-Key im Frontend** — niemals `GROQ_API_KEY` ins Frontend-HTML schreiben. Zentraler Backend-Key.
3. **Blockierende Guardrails** — alte Version blockierte Anfragen. Neue Version: immer Antwort liefern, maximal `msg-warn`-Banner.
4. **SQLite-Pfad** — `data/` Verzeichnis muss existieren. `Path("data/...").parent.mkdir(parents=True, exist_ok=True)` in `__init__`.
5. **Railway-Deployment** — `PORT` aus Environment-Variable nehmen: `--port $PORT`. Nicht hart auf 8001 kodieren.
6. **CORS** — Backend braucht CORS-Middleware wenn Frontend von anderer Domain served wird.

---

## EU AI Act Fristen

| Datum | Status | Beschreibung |
|-------|--------|-------------|
| 01.08.2024 | ✅ | EU AI Act tritt in Kraft |
| 02.02.2025 | ✅ | Verbotene KI-Praktiken anwendbar |
| 02.08.2025 | ✅ | Governance-Regeln anwendbar |
| **02.08.2026** | **⚠️ ~49 Tage** | **VOLLSTÄNDIGE Anwendbarkeit** |
| 02.08.2027 | 🔜 | GPAI-Modelle müssen konform sein |

**Risikoklasse:** Limited Risk (Art. 52) — explizit KEIN Hochrisiko-System.

---

*KI-LISA / AILIZA · EU AI Act Limited Risk · DSGVO konform · Stand 14.06.2026*
