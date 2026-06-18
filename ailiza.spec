# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
# PyInstaller Spec — AILIZA Desktop App
# Aufruf: pyinstaller ailiza.spec
# Ergebnis: dist/AILIZA/AILIZA.exe  (Windows)
#           dist/AILIZA/AILIZA      (macOS/Linux)

import sys
from pathlib import Path

ROOT = Path(SPECPATH)

a = Analysis(
    [str(ROOT / 'ailiza_app.pyw')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / 'apps' / 'frontend'), 'apps/frontend'),
        (str(ROOT / '.env.example'),      '.'),
    ],
    hiddenimports=[
        # FastAPI / Starlette internals
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.loops.asyncio',
        'uvicorn.loops.uvloop',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.http.httptools_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.off',
        'uvicorn.lifespan.on',
        'starlette.routing',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.staticfiles',
        'starlette.responses',
        'fastapi.routing',
        # Pydantic
        'pydantic.deprecated.class_validators',
        'pydantic.deprecated.config',
        'pydantic.deprecated.tools',
        # App modules
        'apps.backend.main',
        'apps.backend.database',
        'apps.backend.groq_client',
        'apps.backend.session_manager',
        'apps.backend.compliance_context',
        'apps.backend.agent_runtime',
        'apps.backend.gateway',
        'apps.backend.approval',
        'apps.backend.policy',
        'apps.backend.audit.audit_logger',
        'apps.backend.skills.guardrail_skill',
        'apps.backend.skills.router_skill',
        'apps.backend.skills.reflection_skill',
        'apps.backend.compliance.dsgvo',
        'apps.backend.compliance.eu_ai_act',
        'apps.backend.compliance.weekly_checker',
        'apps.backend.compliance.scheduler',
        'apps.backend.compliance.eurlex_connector',
        'apps.backend.routers.approvals',
        'apps.backend.routers.datei_upload',
        'apps.backend.tools.standard_tools',
        # Extras
        'pypdf',
        'docx',
        'openpyxl',
        'pystray',
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'dotenv',
        'multipart',
        'email.mime.text',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'numpy', 'pandas', 'scipy'],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AILIZA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # kein CMD-Fenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=str(ROOT / 'ailiza.ico') if (ROOT / 'ailiza.ico').exists() else None,
    version=str(ROOT / 'build' / 'windows' / 'version_info.txt') if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AILIZA',
)
