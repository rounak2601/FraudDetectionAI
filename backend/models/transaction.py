from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    account_id = Column(String, index=True)
    amount = Column(Float)
    merchant_category = Column(String)
    country = Column(String)
    device_id = Column(String)
    ip_address = Column(String)
    fraud_score = Column(Float)
    xgboost_score = Column(Float)
    isolation_score = Column(Float)
    is_fraud_predicted = Column(Boolean, default=False)
    risk_level = Column(String)
    shap_values = Column(Text)
    llm_explanation = Column(Text)
    triggered_rules = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())