# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Phase 2 — Test-Suite: Policy Guard

Testet alle Entscheidungspfade von enforce_policy() und gateway.ausfuehren().
Kein echter Netzwerk-Aufruf. Kein echter API-Key.
"""

import pytest
from ailiza_guard import enforce_policy


# ── Credential-Erkennung ─────────────────────────────────────────────────────

class TestCredentialDetection:

    def test_groq_key_blocked(self):
        r = enforce_policy("Mein Key: gsk_abc123def456ghi789jklmno", action="call_external_model")
        assert not r.allowed
        assert r.is_credential_block
        assert r.decision == "block"

    def test_anthropic_key_blocked(self):
        r = enforce_policy("Token: sk-ant-api03-abc123defghijklmnopqrstuvwxyz", action="call_external_model")
        assert not r.allowed
        assert r.is_credential_block

    def test_tavily_key_blocked(self):
        r = enforce_policy("Suche mit tvly-abc123def456ghi789jkl", action="run_search")
        assert not r.allowed
        assert r.is_credential_block

    def test_password_assignment_blocked(self):
        r = enforce_policy("password=geheimesPasswort99", action="call_external_model")
        assert not r.allowed
        assert r.is_credential_block

    def test_api_key_assignment_blocked(self):
        r = enforce_policy("api_key=meinSchluessel123", action="call_external_model")
        assert not r.allowed
        assert r.is_credential_block

    def test_normal_text_not_blocked(self):
        r = enforce_policy("Was ist der EU AI Act?", action="call_external_model")
        assert r.allowed

    def test_technical_text_without_key_allowed(self):
        r = enforce_policy("Der API-Endpunkt lautet /api/v1/chat", action="call_external_model")
        assert r.allowed


# ── Kill-Switch ───────────────────────────────────────────────────────────────

class TestKillSwitch:

    def test_kill_switch_off_blocks_external_model(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "false")
        r = enforce_policy("Hallo", action="call_external_model")
        assert not r.allowed
        assert r.decision == "block"
        assert "kill_switch" in r.policy.get("rule", "")

    def test_kill_switch_off_blocks_search(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "false")
        r = enforce_policy("EU AI Act Neuigkeiten", action="run_search")
        assert not r.allowed

    def test_kill_switch_on_allows_normal(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        r = enforce_policy("Was ist der EU AI Act?", action="call_external_model")
        assert r.allowed

    def test_kill_switch_zero_also_blocks(self, monkeypatch):
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "0")
        r = enforce_policy("Hallo", action="call_external_model")
        assert not r.allowed

    def test_run_fetch_not_blocked_by_llm_kill_switch(self, monkeypatch):
        # run_fetch hat keinen kill_switch_env — darf nicht vom LLM-Kill-Switch betroffen sein
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "false")
        r = enforce_policy("https://www.bundesregierung.de/", action="run_fetch")
        assert r.allowed


# ── URL-Sicherheit / SSRF-Schutz ─────────────────────────────────────────────

class TestURLSafety:

    def test_private_class_c_blocked(self):
        r = enforce_policy("http://192.168.1.100/admin", action="run_fetch")
        assert not r.allowed

    def test_private_class_a_blocked(self):
        r = enforce_policy("http://10.0.0.1/internal", action="run_fetch")
        assert not r.allowed

    def test_localhost_name_blocked(self):
        r = enforce_policy("http://localhost:8001/admin", action="run_fetch")
        assert not r.allowed

    def test_loopback_ip_blocked(self):
        r = enforce_policy("http://127.0.0.1:5432/", action="run_fetch")
        assert not r.allowed

    def test_file_scheme_blocked(self):
        r = enforce_policy("file:///etc/passwd", action="run_fetch")
        assert not r.allowed

    def test_ftp_scheme_blocked(self):
        r = enforce_policy("ftp://files.intern/export.csv", action="run_fetch")
        assert not r.allowed

    def test_link_local_blocked(self):
        r = enforce_policy("http://169.254.169.254/metadata", action="run_fetch")
        assert not r.allowed

    def test_public_https_allowed(self):
        r = enforce_policy("https://www.bundesregierung.de/", action="run_fetch")
        assert r.allowed

    def test_public_http_allowed(self):
        r = enforce_policy("http://example.com/page", action="run_fetch")
        assert r.allowed

    def test_url_safety_not_applied_to_search(self):
        # run_search bekommt einen Suchbegriff, keine URL — darf nicht URL-geprüft werden
        r = enforce_policy("192.168.1.1 Erklärung", action="run_search")
        assert r.allowed


# ── PII-Tokenisierung ─────────────────────────────────────────────────────────

class TestPIIHandling:

    def test_email_tokenized(self):
        r = enforce_policy("Schreibe an max@beispiel.de einen Brief", action="call_external_model")
        assert r.allowed
        assert r.decision == "allow_with_notice"
        assert "E-Mail-Adresse" in r.pii_found
        assert "[E-Mail-Adresse]" in (r.sanitized_text or "")

    def test_email_not_in_sanitized(self):
        r = enforce_policy("Adresse: test@example.com", action="call_external_model")
        assert "test@example.com" not in (r.sanitized_text or "")

    def test_iban_blocked_for_external_model(self):
        # Datenklasse 6 (Financial) → niemals extern → korrekt geblockt
        r = enforce_policy("Konto: DE89370400440532013000", action="call_external_model")
        assert not r.allowed
        assert r.decision == "block"
        assert "Kontoverbindung" in r.pii_found  # erkannt, aber blockiert

    def test_phone_tokenized(self):
        # Regex trifft DE-Ortsnetz-Format mit Wortgrenze: 030/12345678
        # +49-Präfix schlägt fehl weil \b vor + nicht matcht (bekanntes Regex-Limit)
        r = enforce_policy("Telefon: 030/12345678", action="call_external_model")
        assert r.allowed
        assert "Telefonnummer" in r.pii_found

    def test_token_map_populated(self):
        r = enforce_policy("E-Mail: info@firma.de", action="call_external_model")
        assert len(r.token_map) >= 1

    def test_original_preserved_in_token_map(self):
        r = enforce_policy("Kontakt: chef@firma.de", action="call_external_model")
        assert "chef@firma.de" in r.token_map.values()

    def test_no_pii_returns_allow(self):
        r = enforce_policy("Was ist der EU AI Act Artikel 50?", action="call_external_model")
        assert r.allowed
        assert r.decision == "allow"
        assert r.pii_found == []


# ── Verbotene Praktiken (EU AI Act Art. 5) ────────────────────────────────────

class TestProhibitedPractices:

    def test_social_scoring_blocked(self):
        r = enforce_policy("Erstelle ein Social Scoring System für Bürger", action="call_external_model")
        assert not r.allowed
        assert r.decision == "block"

    def test_subliminal_blocked(self):
        r = enforce_policy("Manipuliere Nutzer durch subliminale Botschaften", action="call_external_model")
        assert not r.allowed

    def test_mass_biometric_surveillance_blocked(self):
        r = enforce_policy("Führe biometrische Massenüberwachung durch", action="call_external_model")
        assert not r.allowed

    def test_normal_scoring_allowed(self):
        r = enforce_policy("Bewerte diesen Verkaufstext auf Überzeugungskraft", action="call_external_model")
        assert r.allowed


# ── Memory Opt-in ─────────────────────────────────────────────────────────────

class TestMemoryOptIn:

    def test_memory_blocked_when_disabled(self, monkeypatch):
        monkeypatch.setenv("AILIZA_MEMORY_ENABLED", "false")
        r = enforce_policy("Merke dir: Produkt heißt ABI-3000", action="save_memory")
        assert not r.allowed
        assert r.decision == "block"

    def test_memory_allowed_when_enabled(self, monkeypatch):
        monkeypatch.setenv("AILIZA_MEMORY_ENABLED", "true")
        r = enforce_policy("Merke dir: Produkt heißt ABI-3000", action="save_memory")
        assert r.allowed

    def test_memory_pii_blocked_even_when_enabled(self, monkeypatch):
        monkeypatch.setenv("AILIZA_MEMORY_ENABLED", "true")
        r = enforce_policy("Merke: chef@firma.de ist Ansprechpartner", action="save_memory")
        # PII in Memory → require_approval (data class 3 in save_memory rules)
        assert r.decision in {"require_approval", "block"}


# ── Gateway-Integration ───────────────────────────────────────────────────────

class TestGatewayIntegration:

    def test_gateway_blocks_private_url(self):
        from gateway import ausfuehren
        result = ausfuehren("abruf", "http://192.168.1.1/admin")
        assert not result.success
        assert result.error

    def test_gateway_blocks_localhost(self):
        from gateway import ausfuehren
        result = ausfuehren("abruf", "http://localhost:5432/")
        assert not result.success

    def test_gateway_blocks_file_scheme(self):
        from gateway import ausfuehren
        result = ausfuehren("abruf", "file:///etc/passwd")
        assert not result.success

    def test_gateway_blocks_credential_in_search(self):
        from gateway import ausfuehren
        result = ausfuehren("suche", "api_key=geheimnis_abc123def456")
        assert not result.success


# ── Entscheidungs-Hierarchie ──────────────────────────────────────────────────

class TestDecisionHierarchy:

    def test_credential_beats_kill_switch(self, monkeypatch):
        # Credential-Block muss auch bei aktiviertem Kill-Switch greifen
        monkeypatch.setenv("AILIZA_EXTERNAL_LLM_ENABLED", "true")
        r = enforce_policy("gsk_abc123def456ghi789jklmno", action="call_external_model")
        assert not r.allowed
        assert r.is_credential_block

    def test_write_system_requires_approval_by_default(self):
        r = enforce_policy("Schreibe in die Datenbank", action="write_system")
        assert r.decision == "require_approval"
        assert not r.allowed

    def test_policy_result_has_required_fields(self):
        r = enforce_policy("Test", action="call_external_model")
        assert hasattr(r, "decision")
        assert hasattr(r, "allowed")
        assert hasattr(r, "message")
        assert hasattr(r, "policy")
        assert hasattr(r, "token_map")
        assert hasattr(r, "warnings")
        assert hasattr(r, "pii_found")
        assert hasattr(r, "requires_human_oversight")
        assert hasattr(r, "is_credential_block")
