import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import func
from fastapi.middleware.cors import CORSMiddleware

from backend.database import create_tables, engine, wait_for_database
from backend.routers import cases, models, transactions


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.scorer = None
    app.state.explainer = None

    wait_for_database()
    create_tables()

    print("Loading ML models into memory...")
    try:
        from models.inference.scorer import FraudScorer

        # FraudScorer owns a single shared FraudExplainer. Do not load SHAP twice.
        app.state.scorer = FraudScorer()
        app.state.explainer = app.state.scorer.explainer
        print("FraudScorer and FraudExplainer loaded.")
    except Exception as exc:
        print(f"WARNING: Models could not be loaded: {exc}")

    print("Fraud Detection API ready.")
    yield
    engine.dispose()


app = FastAPI(
    title="Fraud Detection API",
    description="Real-time financial fraud detection with explainable AI",
    version="2.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)

app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(cases.router, prefix="/api/cases", tags=["Cases"])
app.include_router(models.router, prefix="/api/models", tags=["Models"])


@app.get("/")
async def root():
    return {"message": "Fraud Detection API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    scorer_ok = app.state.scorer is not None
    return {
        "status": "healthy" if scorer_ok else "degraded",
        "models_loaded": scorer_ok,
        "version": "2.2.0",
    }


@app.get("/api/monitoring")
async def monitoring():
    from backend.database import SessionLocal
    from backend.models.transaction import Transaction

    db = SessionLocal()
    try:
        total = db.query(Transaction).count()
        fraud = db.query(Transaction).filter(Transaction.is_fraud_predicted.is_(True)).count()
        high = db.query(Transaction).filter(Transaction.risk_level == "HIGH").count()
        critical = db.query(Transaction).filter(Transaction.risk_level == "CRITICAL").count()
        fraud_rate = round((fraud / total * 100), 2) if total else 0
        avg_score = db.query(func.avg(Transaction.fraud_score)).scalar() or 0.0
        return {
            "total_scored": total,
            "flagged": fraud,
            "cleared": total - fraud,
            "high_risk": high + critical,
            "fraud_rate": fraud_rate,
            "avg_score": round(float(avg_score) * 100, 2),
            "models_active": 3 if app.state.scorer else 0,
            "status": "online" if app.state.scorer else "degraded",
        }
    finally:
        db.close()
