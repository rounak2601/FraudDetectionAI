from fastapi import APIRouter, Depends, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.transaction import Transaction

router = APIRouter()


@router.get("/health")
async def model_health(request: Request):
    scorer = request.app.state.scorer
    if scorer is None:
        return {
            "status": "unhealthy",
            "models_active": 0,
            "models": [],
            "error": "Models not loaded",
        }
    return {
        "status": "healthy",
        "models_active": 3,
        "models": [
            {"name": "XGBoost ONNX", "status": "ACTIVE", "detail": "Fraud classifier"},
            {"name": "Isolation Forest", "status": "ACTIVE", "detail": "Anomaly detector"},
            {"name": "Meta Learner", "status": "ACTIVE", "detail": "Calibrated ensemble"},
        ],
        "features": len(scorer.feature_names),
        "encoding_mode": scorer.encoding_mode,
        "fraud_threshold": scorer.fraud_threshold,
        "llm_available": bool(
            request.app.state.explainer
            and request.app.state.explainer.llm_explainer.available
        ),
    }


@router.get("/stats")
async def model_stats(db: Session = Depends(get_db)):
    total = db.query(Transaction).count()
    fraud = db.query(Transaction).filter(Transaction.is_fraud_predicted.is_(True)).count()
    high = db.query(Transaction).filter(Transaction.risk_level.in_(["HIGH", "CRITICAL"])).count()
    avg_score = db.query(func.avg(Transaction.fraud_score)).scalar() or 0.0
    return {
        "total_scored": total,
        "total_fraud_detected": fraud,
        "high_risk": high,
        "fraud_rate_percent": round((fraud / total * 100), 2) if total else 0,
        "avg_score_percent": round(float(avg_score) * 100, 2),
    }
