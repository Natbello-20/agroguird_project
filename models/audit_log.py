from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, nullable=False)          # e.g., "create_aeo", "update_aeo"
    entity = Column(String, nullable=False)          # e.g., "aeo"
    entity_id = Column(Integer, nullable=False)
    performed_by = Column(Integer, nullable=False)   # user_id of the superadmin
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(Text)                           # JSON string with extra info
