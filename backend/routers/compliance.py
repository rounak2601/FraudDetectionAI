from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.transaction import Transaction
from backend.services.compliance import build_draft_sar, evaluate_rules, sanctions_check

router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    account_id: str | None = None
    merchant: str | None = None
    merchant_name: str | None = None
    beneficiary: str | None = None
    country: str | None = None
    ip_address: str | None = None
    amount: float = Field(default=0, ge=0)
    fraud_score: float = Field(default=0, ge=0, le=1)


@router.post("/check")
async def compliance_check(request: ComplianceCheckRequest):
    payload = request.model_dump()
    sanctions = sanctions_check(payload)
    rules = evaluate_rules(payload)
    return {"sanctions": sanctions, "rules": rules, "review_required": sanctions["matched"] or bool(rules)}


@router.get("/sar/{transaction_id}")
async def draft_sar(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    payload = {
        "transaction_id": tx.transaction_id,
        "account_id": tx.account_id,
        "amount": tx.amount,
        "country": tx.country,
        "fraud_score": tx.fraud_score,
    }
    sanctions = sanctions_check(payload)
    rules = evaluate_rules(payload)
    return {
        "transaction_id": transaction_id,
        "rules": rules,
        "sanctions": sanctions,
        "sar_xml_draft": build_draft_sar(payload, rules, sanctions),
    }
