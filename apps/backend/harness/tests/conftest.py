"""pytest-Konfiguration für AILIZA Harness Tests."""

import os
import sys
from pathlib import Path

# Backend-Pfad für Imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Safe Defaults für alle Tests — kein Netz, kein Memory
os.environ.setdefault("AILIZA_EXTERNAL_LLM_ENABLED", "true")
os.environ.setdefault("AILIZA_MEMORY_ENABLED", "false")
os.environ.setdefault("GROQ_API_KEY", "test-key-not-real")
os.environ.setdefault("TAVILY_API_KEY", "test-key-not-real")
os.environ.setdefault("AILIZA_DB_PATH", "/tmp/ailiza_test.db")
os.environ.setdefault("AILIZA_AUDIT_DB_PATH", "/tmp/ailiza_audit_test.db")
