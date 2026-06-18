import uuid
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db
from backend.models.case import Case
from backend.models.transaction import Transaction

router = APIRouter()

class DecisionRequest(BaseModel):
    analyst_notes: Optional[str] = ""

@router.get("/open")
async def get_open_cases(db: Session = Depends(get_db)):
    cases = db.query(Case)\
        .filter(Case.status == "open")\
        .order_by(Case.created_at.desc())\
        .limit(50).all()
    return [
        {
            "case_id": c.case_id,
            "transaction_id": c.transaction_id,
            "account_id": c.account_id,
            "fraud_score": c.fraud_score,
            "risk_level": c.risk_level,
            "status": c.status,
            "created_at": str(c.created_at)
        }
        for c in cases
    ]

@router.post("/create/{transaction_id}")
async def create_case(transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction)\
        .filter(Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    existing = db.query(Case)\
        .filter(Case.transaction_id == transaction_id).first()
    if existing:
        return {"case_id": existing.case_id, "message": "Case already exists"}

    case = Case(
        case_id=f"CASE-{str(uuid.uuid4())[:8].upper()}",
        transaction_id=transaction_id,
        account_id=tx.account_id,
        fraud_score=tx.fraud_score,
        risk_level=tx.risk_level,
        llm_explanation=tx.llm_explanation
    )
    db.add(case)
    db.commit()
    return {"case_id": case.case_id, "message": "Case created successfully"}

@router.post("/{case_id}/approve")
async def approve_case(
    case_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "closed"
    case.analyst_decision = "approved"
    case.analyst_notes = request.analyst_notes
    db.commit()
    return {"case_id": case_id, "status": "approved", "message": "Transaction approved"}

@router.post("/{case_id}/block")
async def block_case(
    case_id: str,
    request: DecisionRequest,
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.case_id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    case.status = "closed"
    case.analyst_decision = "blocked"
    case.analyst_notes = request.analyst_notes
    db.commit()
    return {"case_id": case_id, "status": "blocked", "message": "Transaction blocked"}