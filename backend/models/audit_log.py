from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from backend.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String)
    transaction_id = Column(String, nullable=True)
    case_id = Column(String, nullable=True)
    user_id = Column(String, nullable=True)
    data = Column(Text)
    prev_hash = Column(String)
    entry_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())