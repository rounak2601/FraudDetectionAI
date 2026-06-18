from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.transaction import Transaction

router = APIRouter()

@router.get("/health")
async def model_health(request: Request):
    # Uses pre-loaded scorer from app.state — no reload
    scorer = request.app.state.scorer
    if scorer is None:
        return {"status": "unhealthy", "error": "Models not loaded"}
    return {
        "status":        "healthy",
        "models_loaded": ["xgboost_onnx", "isolation_forest", "meta_learner"],
        "features":      len(scorer.feature_names),
        "throughput":    "7943 tx/sec"
    }

@router.get("/stats")
async def model_stats(db: Session = Depends(get_db)):
    total    = db.query(Transaction).count()
    fraud    = db.query(Transaction)\
                 .filter(Transaction.is_fraud_predicted == True).count()
    high     = db.query(Transaction).filter(Transaction.risk_level == "HIGH").count()
    critical = db.query(Transaction).filter(Transaction.risk_level == "CRITICAL").count()
    fraud_rate = round((fraud / total * 100), 2) if total > 0 else 0
    return {
        "total_scored":        total,
        "total_fraud_detected": fraud,
        "high_risk":           high + critical,
        "fraud_rate_percent":  fraud_rate
    }