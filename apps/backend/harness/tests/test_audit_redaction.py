# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA Harness — Redaction & Audit Tests

Belegt dass PII das System nie ungeschwärzt verlässt:
  - sanitized_text enthält keine Klardaten
  - token_map Keys sind Platzhalter, Values sind Originale
  - pii_found enthält nur Typ-Namen, nie Werte
  - Approval-Preview (sanitized_text bei write_system) ist geschwärzt
  - IP-Hash verwendet HMAC (nicht plain SHA-256)
"""

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ailiza_guard import enforce_policy


# ── Redaction: sanitized_text enthält keine Klardaten ────────────────────────

class TestSanitizedTextContainsNoRawPII:

    def test_email_not_in_sanitized(self):
        r = enforce_policy("Kontakt: chef@musterfirma.de", action="call_external_model")
        assert r.sanitized_text is not None
        assert "chef@musterfirma.de" not in r.sanitized_text
        assert "[E-Mail-Adresse]" in r.sanitized_text

    def test_phone_not_in_sanitized(self):
        r = enforce_policy("Rufen Sie 030/12345678 an", action="call_external_model")
        assert r.sanitized_text is not None
        assert "030/12345678" not in r.sanitized_text

    def test_international_phone_not_in_sanitized(self):
        r = enforce_policy("Tel: +49 30 12345678", action="call_external_model")
        assert r.sanitized_text is not None
        assert "+49 30 12345678" not in r.sanitized_text

    def test_iban_detected_original_blocked(self):
        # IBAN → Datenklasse 6 (Financial) → blockiert für external model
        r = enforce_policy("IBAN: DE89370400440532013000", action="call_external_model")
        assert not r.allowed
        assert "Kontoverbindung" in r.pii_found
        assert "DE89370400440532013000" not in (r.sanitized_text or "")

    def test_multiple_pii_all_sanitized(self):
        r = enforce_policy(
            "E-Mail max@test.de und Telefon 030/12345678",
            action="call_external_model",
        )
        raw = r.sanitized_text or ""
        assert "max@test.de" not in raw
        assert "030/12345678" not in raw
        assert "[E-Mail-Adresse]" in raw


# ── Approval-Preview: Redaction vor DB-Speicherung ───────────────────────────

class TestApprovalPreviewRedaction:
    """
    Belegt dass bei require_approval der DB-Eintrag die sanitized Version enthält.
    In main.py: sanitized_preview = (policy.sanitized_text or body.message)[:200]
    Diese Tests prüfen die Policy-Seite: sanitized_text ist geschwärzt.
    """

    def test_email_not_in_write_system_preview(self):
        # write_system → default require_approval; PII sollte nicht in Preview
        r = enforce_policy("Schreibe an info@geheimefirma.de", action="write_system")
        assert r.decision == "require_approval"
        preview = r.sanitized_text or ""
        assert "info@geheimefirma.de" not in preview

    def test_phone_not_in_write_system_preview(self):
        r = enforce_policy("CRM: 030/99887766", action="write_system")
        assert r.decision == "require_approval"
        preview = r.sanitized_text or ""
        assert "030/99887766" not in preview

    def test_sanitized_preview_contains_placeholder(self):
        r = enforce_policy("Sende E-Mail an vertrieb@partner.de", action="write_system")
        assert r.decision == "require_approval"
        assert "[E-Mail-Adresse]" in (r.sanitized_text or "")


# ── Token-Map: Keys sind Platzhalter, Values sind Originale ──────────────────

class TestTokenMapStructure:

    def test_keys_are_placeholder_format(self):
        r = enforce_policy("Mail: test@beispiel.de", action="call_external_model")
        for key in r.token_map.keys():
            assert key.startswith("["), f"Key ist kein Platzhalter: {key}"
            assert key.endswith("]"), f"Key ist kein Platzhalter: {key}"

    def test_values_contain_original_pii(self):
        r = enforce_policy("Kontakt: info@firma.de", action="call_external_model")
        assert "info@firma.de" in r.token_map.values()

    def test_no_pii_value_in_keys(self):
        r = enforce_policy("Mail: check@test.de", action="call_external_model")
        for key in r.token_map.keys():
            assert "@" not in key, f"Key enthält '@' — PII im Schlüssel: {key}"


# ── pii_found: Nur Typ-Namen, nie Werte ──────────────────────────────────────

class TestPIIFoundContainsOnlyTypeNames:

    def test_pii_found_has_type_not_value(self):
        r = enforce_policy("Mail: geheim@intern.de", action="call_external_model")
        for pii_type in r.pii_found:
            assert "geheim@intern.de" not in pii_type
            assert "@" not in pii_type

    def test_pii_found_known_types_only(self):
        known = {
            "E-Mail-Adresse", "Telefonnummer", "Kontoverbindung",
            "Geburtsdatum", "IP-Adresse", "Sozialversicherung",
        }
        r = enforce_policy(
            "Mail: a@b.de, Tel: 030/12345678",
            action="call_external_model",
        )
        for pii_type in r.pii_found:
            assert pii_type in known, f"Unbekannter PII-Typ: {pii_type}"

    def test_no_pii_in_clean_text(self):
        r = enforce_policy("Was ist der EU AI Act?", action="call_external_model")
        assert r.pii_found == []


# ── IP-Hash: HMAC statt plain SHA-256 ────────────────────────────────────────

class TestIPHashHMAC:

    def test_ip_hash_differs_from_plain_sha256(self):
        from audit.audit_logger import _ip_hash
        ip = "203.0.113.42"  # TEST-NET-3 (RFC 5737) — keine echte IP
        hmac_hash = _ip_hash(ip)
        plain_sha256 = hashlib.sha256(ip.encode()).hexdigest()[:16]
        assert hmac_hash != plain_sha256, "IP-Hash nutzt nur SHA-256 — HMAC fehlt"

    def test_ip_hash_deterministic_within_call(self):
        from audit.audit_logger import _ip_hash
        ip = "198.51.100.1"  # TEST-NET-2 (RFC 5737)
        assert _ip_hash(ip) == _ip_hash(ip)

    def test_different_ips_produce_different_hashes(self):
        from audit.audit_logger import _ip_hash
        assert _ip_hash("198.51.100.1") != _ip_hash("198.51.100.2")

    def test_ip_hash_length_is_fixed(self):
        from audit.audit_logger import _ip_hash
        h = _ip_hash("203.0.113.1")
        assert len(h) == 16, f"Erwartete 16 Zeichen, bekam {len(h)}"

    def test_ip_hash_changes_with_secret(self, monkeypatch):
        from audit import audit_logger
        import importlib
        monkeypatch.setenv("AILIZA_IP_HASH_SECRET", "secret-a")
        h1 = audit_logger._ip_hash("203.0.113.1")
        monkeypatch.setenv("AILIZA_IP_HASH_SECRET", "secret-b")
        h2 = audit_logger._ip_hash("203.0.113.1")
        assert h1 != h2, "IP-Hash ignoriert AILIZA_IP_HASH_SECRET"


# ── Credential-Sparse-Event: Kein Inhalt gespeichert ─────────────────────────

class TestCredentialSparseAudit:

    def test_credential_block_has_no_content(self):
        r = enforce_policy(
            "Mein API Key: gsk_abc123def456ghi789jklmnopqrstuvwxyz",
            action="call_external_model",
        )
        assert not r.allowed
        assert r.is_credential_block is True
        # sanitized_text muss None sein — Credential wird nicht tokenisiert, nur blockiert
        assert r.sanitized_text is None
        # token_map muss leer sein
        assert r.token_map == {}

    def test_credential_decision_is_block(self):
        r = enforce_policy("token=supergeheim123", action="run_search")
        assert r.decision == "block"
        assert r.is_credential_block is True
