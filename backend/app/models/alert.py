from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from ..database import Base

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_type = Column(String, nullable=False)  # waf_bypass, anomaly, high_threat
    severity = Column(String, nullable=False)  # critical, high, medium, low
    title = Column(String, nullable=False)
    description = Column(Text)
    source_ip = Column(String, nullable=True)
    session_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_resolved = Column(Integer, default=0)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)
