import sys
sys.path.insert(0, ".")

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import create_tables
from backend.routers import transactions, cases, models

# ── Startup: load models ONCE, store on app.state ─────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Called once when server starts — never again
    create_tables()
    print("Loading ML models into memory...")
    try:
        from models.inference.scorer import FraudScorer
        from explainability.explainer import FraudExplainer
        app.state.scorer   = FraudScorer()
        app.state.explainer = FraudExplainer()
        print("✓ FraudScorer loaded")
        print("✓ FraudExplainer loaded")
    except Exception as e:
        print(f"WARNING: Could not load models: {e}")
        app.state.scorer   = None
        app.state.explainer = None
    print("Fraud Detection API ready.")
    yield
    # Shutdown cleanup (nothing needed)

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time financial fraud detection with explainable AI",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600
)

app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(cases.router,        prefix="/api/cases",        tags=["Cases"])
app.include_router(models.router,       prefix="/api/models",       tags=["Models"])

@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API is running",
        "docs": "http://localhost:8000/docs"
    }

@app.get("/health")
async def health():
    scorer_ok = app.state.scorer is not None
    return {
        "status":        "healthy" if scorer_ok else "degraded",
        "models_loaded": scorer_ok,
        "version":       "2.0.0"
    }

@app.get("/api/monitoring")
async def monitoring(db=None):
    from backend.database import SessionLocal
    from backend.models.transaction import Transaction
    db = SessionLocal()
    try:
        total  = db.query(Transaction).count()
        fraud  = db.query(Transaction).filter(Transaction.is_fraud_predicted == True).count()
        high   = db.query(Transaction).filter(Transaction.risk_level == "HIGH").count()
        critical = db.query(Transaction).filter(Transaction.risk_level == "CRITICAL").count()
        fraud_rate = round((fraud / total * 100), 2) if total > 0 else 0
        return {
            "total_scored":   total,
            "flagged":        fraud,
            "cleared":        total - fraud,
            "high_risk":      high + critical,
            "fraud_rate":     fraud_rate,
            "avg_score":      fraud_rate,
            "models_active":  3,
            "status":         "online"
        }
    finally:
        db.close()