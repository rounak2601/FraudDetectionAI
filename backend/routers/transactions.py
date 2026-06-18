import json
import uuid
import threading
import queue
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from backend.database import get_db, SessionLocal
from backend.models.transaction import Transaction

router = APIRouter()

# ── Concurrency controls ───────────────────────────────────────
# Max 3 SHAP threads at once — prevents DB pool exhaustion
_shap_semaphore = threading.Semaphore(3)
# LLM queue — runs ONE at a time so Ollama doesn't get overwhelmed
_llm_queue: queue.Queue = queue.Queue(maxsize=10)
_llm_worker_started = False

def _llm_worker():
    """Single background thread that processes LLM requests one at a time."""
    while True:
        try:
            item = _llm_queue.get(timeout=60)
            if item is None:
                break
            tx_id, tx_dict, shap_result, fraud_probability, explainer = item
            try:
                narrative = explainer.llm_explainer.explain(
                    transaction=tx_dict,
                    shap_results=shap_result,
                    fraud_probability=fraud_probability,
                )
                if not narrative or len(narrative) < 20:
                    narrative = (
                        f"This transaction scored {fraud_probability*100:.1f}% fraud probability. "
                        f"Key risk factors: {', '.join([f['feature'] for f in shap_result.get('top_features', [])[:3]])}."
                    )
            except Exception as e:
                narrative = (
                    f"Transaction scored {fraud_probability*100:.1f}% fraud probability "
                    f"based on behavioral pattern analysis."
                )
                print(f"[LLM error]: {e}")

            db = SessionLocal()
            try:
                tx = db.query(Transaction).filter(
                    Transaction.transaction_id == tx_id).first()
                if tx:
                    tx.llm_explanation = narrative
                    db.commit()
                    print(f"[LLM done] tx={tx_id[:8]} len={len(narrative)}")
            finally:
                db.close()
            _llm_queue.task_done()
        except queue.Empty:
            continue
        except Exception as e:
            print(f"[LLM worker error]: {e}")


def _start_llm_worker():
    global _llm_worker_started
    if not _llm_worker_started:
        t = threading.Thread(target=_llm_worker, daemon=True)
        t.start()
        _llm_worker_started = True


def _background_shap(tx_id: str, tx_dict: dict,
                     fraud_probability: float, explainer):
    """Runs SHAP in background with semaphore. Queues LLM after."""
    acquired = _shap_semaphore.acquire(blocking=True, timeout=30)
    if not acquired:
        print(f"[SHAP skip] semaphore timeout tx={tx_id[:8]}")
        return
    try:
        shap_result = explainer.shap_explainer.explain(tx_dict)
        shap_values = shap_result.get("all_shap_values", {})
        print(f"[SHAP done] tx={tx_id[:8]} prob={fraud_probability:.3f}")

        # Save SHAP immediately
        db = SessionLocal()
        try:
            tx = db.query(Transaction).filter(
                Transaction.transaction_id == tx_id).first()
            if tx:
                tx.shap_values = json.dumps(shap_values)
                db.commit()
                print(f"[SHAP saved] tx={tx_id[:8]}")
        finally:
            db.close()

        # Only queue LLM for MEDIUM and above — saves queue for transactions that matter
        if fraud_probability >= 0.3:
            try:
                _llm_queue.put_nowait(
                    (tx_id, tx_dict, shap_result, fraud_probability, explainer)
                )
            except queue.Full:
                print(f"[LLM queue full] tx={tx_id[:8]} — will generate on-demand")

    except Exception as e:
        print(f"[SHAP error]: {e}")
    finally:
        _shap_semaphore.release()


def _run_on_demand_llm(tx_id: str, tx_basic: dict, shap_values: dict,
                        fraud_probability: float, explainer):
    """LLM on-demand — triggered when Investigation page opens."""
    try:
        sorted_feats = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = [
            {"feature": k, "shap_value": round(v, 4),
             "direction": "increases_fraud_risk" if v > 0 else "decreases_fraud_risk"}
            for k, v in sorted_feats[:5]
        ]
        shap_result = {
            "top_features":    top_features,
            "all_shap_values": shap_values,
            "base_value":      0.035,
            "shap_sum":        round(sum(shap_values.values()), 4)
        }
        narrative = explainer.llm_explainer.explain(
            transaction=tx_basic,
            shap_results=shap_result,
            fraud_probability=fraud_probability,
        )
        if not narrative or len(narrative) < 20:
            top_3 = ", ".join([f["feature"] for f in top_features[:3]])
            narrative = (
                f"This transaction scored {fraud_probability*100:.1f}% fraud probability. "
                f"The primary risk indicators are {top_3}. "
                f"Analyst review is recommended based on the triggered rules and behavioral patterns."
            )
        db = SessionLocal()
        try:
            tx = db.query(Transaction).filter(
                Transaction.transaction_id == tx_id).first()
            if tx:
                tx.llm_explanation = narrative
                db.commit()
                print(f"[On-demand LLM done] tx={tx_id[:8]} len={len(narrative)}")
        finally:
            db.close()
    except Exception as e:
        print(f"[On-demand LLM error]: {e}")



class TransactionRequest(BaseModel):
    transaction_id: Optional[str] = None
    account_id: str
    amount: float
    merchant_category: str
    country: str
    device_id: str
    ip_address: str
    P_emaildomain: Optional[str] = "gmail.com"
    R_emaildomain: Optional[str] = "gmail.com"
    card4: Optional[str] = "visa"
    card6: Optional[str] = "debit"
    addr1: Optional[float] = 299.0
    addr2: Optional[float] = 87.0
    dist1: Optional[float] = 0.0
    C1: Optional[float] = 1.0
    C2: Optional[float] = 1.0
    C3: Optional[float] = 0.0
    C4: Optional[float] = 0.0
    C5: Optional[float] = 0.0
    C6: Optional[float] = 1.0
    C7: Optional[float] = 0.0
    C8: Optional[float] = 0.0
    C9: Optional[float] = 1.0
    C10: Optional[float] = 0.0
    V1: Optional[float] = 1.0
    V2: Optional[float] = 1.0
    V3: Optional[float] = 1.0
    V4: Optional[float] = 1.0
    V5: Optional[float] = 1.0
    V6: Optional[float] = 1.0
    V7: Optional[float] = 1.0
    V8: Optional[float] = 1.0
    V9: Optional[float] = 1.0
    V10: Optional[float] = 1.0


@router.post("/score")
async def score_transaction(
    request: Request,
    body: TransactionRequest,
    db: Session = Depends(get_db)
):
    # Ensure LLM worker is running
    _start_llm_worker()

    scorer    = request.app.state.scorer
    explainer = request.app.state.explainer

    if scorer is None:
        raise HTTPException(status_code=503, detail="Models not loaded.")

    try:
        tx_dict = body.model_dump()
        if not tx_dict.get("transaction_id"):
            tx_dict["transaction_id"] = str(uuid.uuid4())

        result = scorer.score(tx_dict, tx_dict["transaction_id"])

        fraud_probability  = result.fraud_probability
        risk_level         = result.risk_level
        xgboost_score      = result.xgb_score
        isolation_score    = result.isolation_score
        triggered_rules    = result.triggered_rules

        print(f"[SCORED] acct={tx_dict['account_id']} "
              f"prob={fraud_probability:.3f} risk={risk_level} "
              f"rules={len(triggered_rules)}")

        db_tx = Transaction(
            transaction_id     = tx_dict["transaction_id"],
            account_id         = tx_dict["account_id"],
            amount             = tx_dict["amount"],
            merchant_category  = tx_dict["merchant_category"],
            country            = tx_dict["country"],
            device_id          = tx_dict["device_id"],
            ip_address         = tx_dict["ip_address"],
            fraud_score        = fraud_probability,
            xgboost_score      = xgboost_score,
            isolation_score    = isolation_score,
            is_fraud_predicted = fraud_probability >= 0.5,
            risk_level         = risk_level,
            shap_values        = json.dumps({}),
            llm_explanation    = "",
            triggered_rules    = json.dumps(triggered_rules)
        )
        db.add(db_tx)
        db.commit()

        # Start SHAP in background (LLM is queued inside _background_shap)
        t = threading.Thread(
            target=_background_shap,
            args=(tx_dict["transaction_id"], tx_dict,
                  fraud_probability, explainer),
            daemon=True
        )
        t.start()

        return {
            "transaction_id":    tx_dict["transaction_id"],
            "fraud_probability": fraud_probability,
            "risk_level":        risk_level,
            "xgboost_score":     xgboost_score,
            "isolation_score":   isolation_score,
            "triggered_rules":   triggered_rules,
            "shap_values":       {},
            "llm_explanation":   "Analyzing..."
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_transactions(
        limit: int = 50, db: Session = Depends(get_db)):
    txs = db.query(Transaction)\
            .order_by(Transaction.created_at.desc())\
            .limit(limit).all()
    return [
        {
            "transaction_id":    t.transaction_id,
            "account_id":        t.account_id,
            "amount":            t.amount,
            "fraud_score":       t.fraud_score,
            "risk_level":        t.risk_level,
            "is_fraud_predicted": t.is_fraud_predicted,
            "merchant_category": t.merchant_category,
            "country":           t.country,
            "created_at":        str(t.created_at)
        }
        for t in txs
    ]



@router.post("/{transaction_id}/explain")
async def generate_explanation(transaction_id: str, db: Session = Depends(get_db)):
    try:
        tx = db.query(Transaction)\
            .filter(Transaction.transaction_id == transaction_id).first()
        if not tx:
            raise HTTPException(status_code=404, detail="Transaction not found")

        if tx.llm_explanation and len(tx.llm_explanation) > 20:
            return {"explanation": tx.llm_explanation, "status": "already_exists"}

        import sys
        sys.path.insert(0, ".")
        from explainability.explainer import FraudExplainer

        explainer = FraudExplainer()

        tx_dict = {
            "transaction_id": tx.transaction_id,
            "account_id": tx.account_id,
            "amount": tx.amount,
            "TransactionAmt": tx.amount,
            "merchant_category": tx.merchant_category,
            "country": tx.country,
            "P_emaildomain": "gmail.com",
            "R_emaildomain": "gmail.com",
            "card4": "visa",
        }

        shap_values = json.loads(tx.shap_values) if tx.shap_values else {}

        shap_results = {
            "top_features": [
                {"feature": k, "shap_value": v}
                for k, v in sorted(
                    shap_values.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )[:5]
            ] if shap_values else []
        }

        narrative = explainer.llm_explainer.explain(
            transaction=tx_dict,
            shap_results=shap_results,
            fraud_probability=tx.fraud_score or 0.5
        )

        tx.llm_explanation = narrative
        db.commit()

        return {"explanation": narrative, "status": "generated"}

    except Exception as e:
        return {"explanation": f"Analysis complete. Fraud score: {tx.fraud_score:.1%}. Review triggered rules for details.", "status": "fallback"}

@router.get("/{transaction_id}")
async def get_transaction(
        transaction_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "transaction_id":  tx.transaction_id,
        "account_id":      tx.account_id,
        "amount":          tx.amount,
        "country":         tx.country,
        "fraud_score":     tx.fraud_score,
        "risk_level":      tx.risk_level,
        "xgboost_score":   tx.xgboost_score,
        "isolation_score": tx.isolation_score,
        "shap_values":     json.loads(tx.shap_values)
                           if tx.shap_values else {},
        "llm_explanation": tx.llm_explanation
                           if tx.llm_explanation else "Generating explanation...",
        "triggered_rules": json.loads(tx.triggered_rules)
                           if tx.triggered_rules else [],
        "created_at":      str(tx.created_at)
    }