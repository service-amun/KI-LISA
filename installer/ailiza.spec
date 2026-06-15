# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
# PyInstaller Spec-Datei für AILIZA Windows App
# Ausführen mit: pyinstaller ailiza.spec

import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent  # Projektverzeichnis

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[
        str(ROOT),
        str(ROOT / "apps" / "backend"),
    ],
    binaries=[],
    datas=[
        # Frontend einbinden
        (str(ROOT / "apps" / "frontend"), "apps/frontend"),
        # .env.example als Vorlage
        (str(ROOT / ".env.example"), "."),
    ],
    hiddenimports=[
        # FastAPI & Uvicorn
        "uvicorn",
        "uvicorn.main",
        "uvicorn.config",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.off",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "fastapi",
        "fastapi.staticfiles",
        "fastapi.responses",
        "fastapi.middleware",
        "fastapi.middleware.cors",
        "starlette",
        "starlette.staticfiles",
        "starlette.routing",
        "pydantic",
        "pydantic.v1",
        # Eigene Module
        "database",
        "groq_client",
        "agent_runtime",
        "session_manager",
        "gateway",
        "compliance_context",
        "audit.audit_logger",
        "skills.guardrail_skill",
        "skills.router_skill",
        "skills.reflection_skill",
        "compliance.eurlex_connector",
        "compliance.law_updater",
        "compliance.weekly_checker",
        "compliance.scheduler",
        "routers.approvals",
        "tools.standard_tools",
        # Standard-Bibliotheken
        "sqlite3",
        "dotenv",
        "email",
        "email.mime",
        "email.mime.text",
        "multiprocessing",
        "asyncio",
        "logging",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AILIZA",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,     # Konsolenfenster zeigen (Nutzer sieht Status)
    icon=None,        # Icon-Datei hier eintragen wenn vorhanden: "installer/ailiza.ico"
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="AILIZA",
)
