# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Harness — main.py Integrations-Tests

Belegt dass der Groq-Hauptaufruf enforce_policy durchläuft:
  - Credentials werden VOR groq_client.chat blockiert
  - Kill-Switch AILIZA_EXTERNAL_LLM_ENABLED blockiert Groq-Aufruf
  - Private URLs werden im /agent/run Endpoint blockiert
  - file:// wird im /agent/run Endpoint blockiert
  - Normaler Text (ohne PII) erreicht groq_client.chat
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# FastAPI TestClient — kein echter Server nötig
from fastapi.testclient import TestClient

# Mock-Antwort für Groq (echte API wird nie aufgerufen)
_MOCK_LLM_RESPONSE = MagicMock()
_MOCK_LLM_RESPONSE.text = "KI-generiert — AILIZA (EU AI Act Art. 52) — Test-Antwort."
_MOCK_LLM_RESPONSE.model = "llama-3.3-70b-versatile"
_MOCK_LLM_RESPONSE.tokens_used = 42
_MOCK_LLM_RESPONSE.error = None

# main.py einmalig laden (TestClient cached die App)
import main as _main_module
_client = TestClient(_main_module.app, raise_server_exceptions=False)


def _neue_session(titel: str = "Test") -> str:
    """Hilfsfunktion: erstellt eine Session und gibt die session_id zurück."""
    r = _client.post("/sessions", json={"title": titel})
    assert r.status_code == 200, f"Session-Erstellung fehlgeschlagen: {r.text}"
    return r.json()["session_id"]


def _chat(session_id: str, message: str) -> dict:
    """Hilfsfunktion: sendet eine Chat-Nachricht."""
    r = _client.post(
        f"/sessions/{session_id}/chat",
        json={"session_id": session_id, "message": message, "model": "standard"},
    )
    assert r.status_code == 200, f"Chat-Aufruf fehlgeschlagen: {r.text}"
    return r.json()


# ── Credential-Blocking VOR Groq ─────────────────────────────────────────────

class TestCredentialBlockedBeforeGroq:

    def test_groq_key_blocked_groq_not_called(self):
        sid = _neue_session("cred-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "Mein Key: gsk_abc123def456ghi789jklmnopqrstuvwxyz")
        assert data["blocked"] is True
        mock_chat.assert_not_called()  # Groq wurde NICHT aufgerufen

    def test_anthropic_key_blocked_groq_not_called(self):
        sid = _neue_session("ant-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "Token: sk-ant-api03-abc123defghijklmno1234567890")
        assert data["blocked"] is True
        mock_chat.assert_not_called()

    def test_password_blocked_groq_not_called(self):
        sid = _neue_session("pw-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "password=supergeheim99")
        assert data["blocked"] is True
        mock_chat.assert_not_called()


# ── Kill-Switch AILIZA_EXTERNAL_LLM_ENABLED ──────────────────────────────────

class TestKillSwitchBlocksGroq:

    def test_kill_switch_false_blocks_groq(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "false")
        sid = _neue_session("ks-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "Normale Frage ohne sensible Daten")
        assert data["blocked"] is True
        mock_chat.assert_not_called()

    def test_kill_switch_zero_blocks_groq(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "0")
        sid = _neue_session("ks0-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "Hallo AILIZA")
        assert data["blocked"] is True
        mock_chat.assert_not_called()

    def test_kill_switch_on_allows_groq(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        sid = _neue_session("ks-on-test")
        with patch.object(_main_module.groq_client, "chat", return_value=_MOCK_LLM_RESPONSE):
            data = _chat(sid, "Was ist der EU AI Act?")
        assert data.get("blocked") is not True
        assert "text" in data


# ── Private URL im /agent/run Endpoint ───────────────────────────────────────

class TestAgentRunSSRFProtection:

    def test_private_192_blocked(self):
        r = _client.post("/agent/run", json={"task": "http://192.168.1.1/admin"})
        assert r.status_code == 200
        assert r.json()["status"] == "blocked"

    def test_loopback_blocked(self):
        r = _client.post("/agent/run", json={"task": "http://127.0.0.1:5432/"})
        assert r.json()["status"] == "blocked"

    def test_localhost_name_blocked(self):
        r = _client.post("/agent/run", json={"task": "http://localhost:8001/audit-logs"})
        assert r.json()["status"] == "blocked"

    def test_file_scheme_blocked(self):
        r = _client.post("/agent/run", json={"task": "file:///etc/passwd"})
        assert r.json()["status"] == "blocked"

    def test_internal_10_network_blocked(self):
        r = _client.post("/agent/run", json={"task": "http://10.0.0.1/"})
        assert r.json()["status"] == "blocked"

    def test_metadata_ip_blocked(self):
        # AWS/GCP Instance Metadata Service
        r = _client.post("/agent/run", json={"task": "http://169.254.169.254/latest/meta-data/"})
        assert r.json()["status"] == "blocked"


# ── Credential in /agent/run Endpoint ────────────────────────────────────────

class TestAgentRunCredentialProtection:

    def test_credential_in_search_blocked(self):
        r = _client.post("/agent/run", json={"task": "api_key=geheimnis_abc123def456ghi"})
        assert r.json()["status"] == "blocked"

    def test_gsk_key_in_search_blocked(self):
        r = _client.post("/agent/run", json={"task": "gsk_abc123def456ghi789jklmnopqr"})
        assert r.json()["status"] == "blocked"


# ── Normaler Text erreicht Groq ───────────────────────────────────────────────

class TestCleanTextReachesGroq:

    def test_normal_question_reaches_groq(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        sid = _neue_session("clean-test")
        with patch.object(
            _main_module.groq_client, "chat", return_value=_MOCK_LLM_RESPONSE
        ) as mock_chat:
            data = _chat(sid, "Erkläre mir den EU AI Act in drei Sätzen.")
        mock_chat.assert_called_once()  # Groq wurde genau einmal aufgerufen
        assert data.get("blocked") is not True

    def test_pii_text_reaches_groq_sanitized(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        sid = _neue_session("pii-test")
        with patch.object(
            _main_module.groq_client, "chat", return_value=_MOCK_LLM_RESPONSE
        ) as mock_chat:
            data = _chat(sid, "Schreibe einen Brief an max@beispiel.de")
        # PII-Text → allow_with_notice → Groq wird aufgerufen (mit sanitized Text)
        mock_chat.assert_called_once()
        # Der an Groq gesendete Text enthält keinen Klarnamen
        call_args = mock_chat.call_args
        sent_message = call_args.kwargs.get("message") or (call_args.args[0] if call_args.args else "")
        assert "max@beispiel.de" not in sent_message
        assert "[E-Mail-Adresse]" in sent_message
