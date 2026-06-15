# © 2026 Karola Fromm-Nasreldin | AILIZA — Alle Rechte vorbehalten
"""
AILIZA — Genehmigungen Router
Human Oversight für kritische Entscheidungen (EU AI Act Art. 14).
"""

from fastapi import APIRouter, HTTPException
import database

router = APIRouter(prefix="/approvals", tags=["Genehmigungen"])


@router.get("")
def list_approvals():
    return database.get_approvals(only_pending=True)


@router.get("/{approval_id}")
def get_approval(approval_id: int):
    all_approvals = database.get_approvals(only_pending=False)
    match = next((a for a in all_approvals if a["id"] == approval_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Genehmigung nicht gefunden.")
    return match


@router.post("/{approval_id}/approve")
def approve(approval_id: int):
    database.decide_approval(approval_id, approved=True)
    return {"status": "genehmigt", "id": approval_id}


@router.post("/{approval_id}/reject")
def reject(approval_id: int):
    database.decide_approval(approval_id, approved=False)
    return {"status": "abgelehnt", "id": approval_id}
