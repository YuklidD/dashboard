from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from datetime import datetime
from ..database import Base

class Policy(Base):
    __tablename__ = "policies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    policy_type = Column(String, nullable=False)  # waf, honeypot, automation
    enabled = Column(Boolean, default=True)
    configuration = Column(Text)  # JSON string
    threshold_value = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, nullable=True)
