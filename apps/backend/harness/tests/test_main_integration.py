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

import pytest

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


@pytest.fixture(autouse=True)
def reset_rate_limit():
    """Rate-Limiter zwischen Tests zurücksetzen — verhindert 429-Fehler."""
    _main_module._rate_store.clear()
    yield
    _main_module._rate_store.clear()


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

    def test_groq_not_called_on_new_credential_patterns(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        sid = _neue_session("cred-gh-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            data = _chat(sid, "ghp_" + "A" * 36)
        assert data["blocked"] is True
        mock_chat.assert_not_called()

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


# ── require_approval: Pending-Record, kein externer Call ─────────────────────

class TestRequireApprovalCreatesOnlyPending:
    """
    Belegt dass bei require_approval kein Groq-Aufruf stattfindet —
    nur ein Pending-Approval-Record wird angelegt.

    enforce_policy wird gemockt weil call_external_model kein require_approval
    in den Regeln hat — die Policy selbst ist in TestRequireApprovalPolicy bewiesen.
    """

    def _make_approval_policy(self):
        from ailiza_guard import PolicyResult
        return PolicyResult(
            decision="require_approval",
            allowed=False,
            message="Test-Freigabe nötig",
            policy={"rule": "test", "action": "call_external_model", "data_classes": [3]},
        )

    def test_require_approval_creates_pending_no_groq(self):
        sid = _neue_session("approval-test")
        with patch.object(_main_module, "enforce_policy", return_value=self._make_approval_policy()):
            with patch.object(_main_module.groq_client, "chat") as mock_chat:
                r = _client.post(
                    f"/sessions/{sid}/chat",
                    json={"session_id": sid, "message": "Test", "model": "standard"},
                )
        assert r.status_code == 200
        data = r.json()
        # require_approval → approval_pending=True, kein Groq-Aufruf
        assert data.get("approval_pending") is True
        assert isinstance(data.get("approval_id"), int)
        assert data.get("approval_id", 0) > 0
        mock_chat.assert_not_called()

    def test_require_approval_response_is_not_blocked(self):
        sid = _neue_session("approval-block-test")
        with patch.object(_main_module, "enforce_policy", return_value=self._make_approval_policy()):
            with patch.object(_main_module.groq_client, "chat"):
                r = _client.post(
                    f"/sessions/{sid}/chat",
                    json={"session_id": sid, "message": "Test", "model": "standard"},
                )
        data = r.json()
        # approval_pending ist KEIN hard block — Nutzer bekommt freundlichen Hinweis
        assert data.get("blocked") is False
        assert data.get("approval_pending") is True

    def test_require_approval_approval_id_unique_per_request(self):
        """Jede require_approval-Anfrage erzeugt einen eigenen Approval-Record."""
        ids = []
        for i in range(3):
            sid = _neue_session(f"approval-uniq-{i}")
            with patch.object(_main_module, "enforce_policy", return_value=self._make_approval_policy()):
                with patch.object(_main_module.groq_client, "chat"):
                    r = _client.post(
                        f"/sessions/{sid}/chat",
                        json={"session_id": sid, "message": "Test", "model": "standard"},
                    )
            ids.append(r.json().get("approval_id"))
        # Alle IDs müssen verschieden und positiv sein
        assert len(set(ids)) == 3
        assert all(isinstance(i, int) and i > 0 for i in ids)


# ── Hauptpfade: Guard läuft vor jedem externen Aufruf ────────────────────────

class TestMainPathGuardIntegration:
    """
    Belegt end-to-end dass der Guard VOR jedem externen Aufruf sitzt.
    Chat → Guard → Groq
    Agent/Search → Guard → Tavily
    Agent/Fetch → Guard → URL
    """

    def test_chat_groq_call_blocked_without_kill_switch(self, monkeypatch):
        """Wenn Kill-Switch fehlt (fail-closed), erreicht kein Chat-Request Groq."""
        monkeypatch.delenv("AILIZA_EXTERNAL_LLM_ENABLED", raising=False)
        sid = _neue_session("no-ks-test")
        with patch.object(_main_module.groq_client, "chat") as mock_chat:
            r = _client.post(
                f"/sessions/{sid}/chat",
                json={"session_id": sid, "message": "Hallo", "model": "standard"},
            )
        assert r.status_code == 200
        data = r.json()
        assert data.get("blocked") is True
        mock_chat.assert_not_called()

    def test_agent_search_credential_blocked_before_tavily(self):
        """Credential im Search-Task blockiert vor Tavily."""
        r = _client.post("/agent/run", json={"task": "api_key=geheimnis_abc123def456ghi"})
        assert r.json()["status"] == "blocked"

    def test_agent_fetch_private_ip_blocked_before_request(self):
        """Private URL im Fetch-Task blockiert vor HTTP-Request."""
        r = _client.post("/agent/run", json={"task": "http://192.168.1.100/internal"})
        assert r.json()["status"] == "blocked"

    def test_agent_fetch_metadata_blocked(self):
        """Cloud-Metadata-IP blockiert."""
        r = _client.post("/agent/run", json={"task": "http://169.254.169.254/latest/"})
        assert r.json()["status"] == "blocked"

    def test_kill_switch_off_blocks_all_chat(self, monkeypatch):
        """Kill-Switch false → jeder Chat-Aufruf geblockt, unabhängig vom Inhalt."""
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "false")
        for message in ["Hallo", "EU AI Act", "Hilf mir beim Schreiben"]:
            sid = _neue_session(f"ks-{message[:4]}")
            with patch.object(_main_module.groq_client, "chat") as mock_chat:
                # Direkt posten statt _chat() — letzteres assertet status_code 200,
                # aber blockierte Anfragen kommen auch mit 200 zurück.
                r = _client.post(
                    f"/sessions/{sid}/chat",
                    json={"session_id": sid, "message": message, "model": "standard"},
                )
            assert r.status_code == 200
            data = r.json()
            assert data.get("blocked") is True, f"Erwartet blocked für: {message}"
            mock_chat.assert_not_called()
