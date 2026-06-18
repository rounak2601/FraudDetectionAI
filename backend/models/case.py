from sqlalchemy import Column, String, Float, Integer, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True, index=True)
    transaction_id = Column(String, index=True)
    account_id = Column(String)
    fraud_score = Column(Float)
    risk_level = Column(String)
    status = Column(String, default="open")
    analyst_decision = Column(String, nullable=True)
    analyst_notes = Column(Text, nullable=True)
    llm_explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())