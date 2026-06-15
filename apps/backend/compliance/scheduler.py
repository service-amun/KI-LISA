# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Compliance Scheduler
Führt EUR-Lex-Checks beim Start und wöchentlich im Hintergrund durch.
Daemon-Thread — stoppt automatisch wenn der Server endet.
"""

import logging
import threading
import time

logger = logging.getLogger(__name__)

_WOCHE_SEKUNDEN = 7 * 24 * 60 * 60
_gestartet = False


def _check_job():
    try:
        from compliance.weekly_checker import komplett_check
        ergebnis = komplett_check()
        updates = ergebnis.get("law_updates", {})
        gespeichert = [n for n, u in updates.items() if u.get("gespeichert")]
        if gespeichert:
            logger.warning(
                "COMPLIANCE ⚠ Gesetze aktualisiert und im Gedächtnis gespeichert: %s",
                gespeichert,
            )
        elif ergebnis.get("handlungsbedarf"):
            logger.warning("COMPLIANCE ⚠ Handlungsbedarf: %s", ergebnis.get("gesetzes_aenderungen"))
        else:
            logger.info("COMPLIANCE ✓ Alle Prüfungen OK — keine Änderungen.")
    except Exception as exc:
        logger.error("COMPLIANCE Fehler: %s", exc)


def _loop():
    while True:
        time.sleep(_WOCHE_SEKUNDEN)
        _check_job()


def starten():
    """Startet den Scheduler genau einmal (idempotent)."""
    global _gestartet
    if _gestartet:
        return
    _gestartet = True

    # Einmaliger Check kurz nach Start (non-blocking)
    threading.Thread(target=_check_job, daemon=True, name="compliance-start").start()
    # Wöchentliche Wiederholung
    threading.Thread(target=_loop, daemon=True, name="compliance-weekly").start()
    logger.info("COMPLIANCE Scheduler aktiv — EUR-Lex wird wöchentlich geprüft.")
