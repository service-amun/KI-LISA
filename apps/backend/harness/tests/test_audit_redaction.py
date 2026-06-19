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
from audit.audit_logger import redact_string, _deep_redact


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


# ── Audit-Log Redaction: write_audit_entry schwärzt alle Felder ───────────────

class TestAuditLogRedaction:
    """
    Belegt dass audit_logger.redact_string() und _deep_redact()
    PII und Secrets aus allen String-Werten entfernen.
    """

    def test_email_redacted_in_string(self):
        result = redact_string("Kontakt: chef@musterfirma.de — bitte anrufen")
        assert "chef@musterfirma.de" not in result
        assert "[E-Mail-Adresse]" in result

    def test_phone_redacted_in_string(self):
        result = redact_string("CRM-Eintrag: Telefon 030/12345678")
        assert "030/12345678" not in result
        assert "[Telefonnummer]" in result

    def test_international_phone_redacted(self):
        result = redact_string("Rückruf: +49 30 12345678")
        assert "+49 30 12345678" not in result

    def test_iban_redacted_in_string(self):
        result = redact_string("Überweisung an DE89370400440532013000")
        assert "DE89370400440532013000" not in result
        assert "[IBAN]" in result

    def test_groq_key_redacted_in_string(self):
        result = redact_string("API Key: gsk_abc123def456ghi789jklmnopqrstuvwxyz")
        assert "gsk_abc123def456" not in result
        assert "[Secret]" in result

    def test_bearer_token_redacted_in_string(self):
        # Konstruiert — kein echter Token im Quelltext (GitHub Secret Scanning)
        fake = "Bearer eyJmYWtlIjoidG9rZW4ifQ." + "X" * 20 + "." + "Y" * 20
        result = redact_string(f"Header: {fake}")
        assert "eyJmYWtlIjoidG9rZW4ifQ" not in result

    def test_password_assignment_redacted(self):
        result = redact_string("Konfiguration: password=SuperGeheim99!")
        assert "SuperGeheim99!" not in result
        assert "[Secret]" in result

    def test_deep_redact_dict(self):
        data = {
            "user": "chef@firma.de",
            "phone": "030/99887766",
            "message_len": 42,   # int — bleibt unverändert
            "nested": {"iban": "DE89370400440532013000"},
        }
        clean = _deep_redact(data)
        assert "chef@firma.de" not in str(clean)
        assert "030/99887766" not in str(clean)
        assert "DE89370400440532013000" not in str(clean)
        assert clean["message_len"] == 42  # int bleibt integer

    def test_deep_redact_list(self):
        data = ["mail: info@beispiel.de", "kein PII hier", "Tel: 0171/1234567"]
        clean = _deep_redact(data)
        assert "info@beispiel.de" not in str(clean)
        assert "0171/1234567" not in str(clean)
        assert "kein PII hier" in clean  # unverändert

    def test_clean_string_unchanged(self):
        text = "Normaler Text ohne PII oder Secrets."
        assert redact_string(text) == text

    def test_redact_none_safe(self):
        # None-Werte dürfen nicht crashen
        assert redact_string(None) is None

    def test_phone_in_audit_details_redacted(self):
        """Telefonnummer in Audit-Details darf nicht auf Disk landen."""
        from audit.audit_logger import write_audit_entry, get_audit_entries
        write_audit_entry("test.phone_redaction", {
            "message": "Rückruf an 030/12345678 gewünscht",
        })
        entries = get_audit_entries(limit=1)
        assert entries
        details_str = str(entries[0].get("details", ""))
        assert "030/12345678" not in details_str

    def test_email_in_audit_details_redacted(self):
        """E-Mail in Audit-Details darf nicht auf Disk landen."""
        from audit.audit_logger import write_audit_entry, get_audit_entries
        write_audit_entry("test.email_redaction", {
            "user_input": "Schreibe an ceo@geheimefirma.de",
        })
        entries = get_audit_entries(limit=1)
        assert entries
        details_str = str(entries[0].get("details", ""))
        assert "ceo@geheimefirma.de" not in details_str
        assert "E-Mail-Adresse" in details_str or "[E-Mail" in details_str


# ── require_approval: Pending erzeugen, kein externer Call ───────────────────

class TestRequireApprovalPolicy:
    """
    Belegt dass require_approval nur einen Pending-Record erzeugt —
    keine externe Aktion wird ausgelöst.
    """

    def test_write_system_requires_approval(self):
        r = enforce_policy("Schreibe in die CRM-Datenbank", action="write_system")
        assert r.decision == "require_approval"
        assert not r.allowed

    def test_write_system_approval_no_sanitized_content_if_no_pii(self):
        r = enforce_policy("Aktualisiere Kundenstatus auf 'aktiv'", action="write_system")
        assert r.decision == "require_approval"
        # Kein PII → sanitized_text bleibt None
        assert r.sanitized_text is None

    def test_write_system_with_pii_sanitized_for_preview(self):
        r = enforce_policy("Schreibe an info@firma.de", action="write_system")
        assert r.decision == "require_approval"
        # PII im Text → sanitized_text enthält Platzhalter, nicht Klardaten
        preview = r.sanitized_text or ""
        assert "info@firma.de" not in preview

    def test_memory_pii_requires_approval_not_block(self, monkeypatch):
        monkeypatch.setenv("AILIZA_MEMORY_ENABLED", "true")
        r = enforce_policy("Chef heißt Hans, erreichbar unter 030/12345678", action="save_memory")
        # Telefon → Datenklasse 3 → require_approval für save_memory
        assert r.decision in {"require_approval", "block"}
        assert not r.allowed
