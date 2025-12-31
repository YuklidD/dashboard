from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from datetime import datetime
from app.core.database import Base

class HoneypotSession(Base):
    __tablename__ = "honeypot_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True, nullable=False)
    honeypot_type = Column(String, nullable=False)  # shellm, ssh, http
    source_ip = Column(String, nullable=False)
    source_port = Column(Integer)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    commands_count = Column(Integer, default=0)
    threat_score = Column(Float, default=0.0)
    status = Column(String, default="active")  # active, terminated, timeout
    pod_name = Column(String, nullable=True)
    
    # Geolocation
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    
    # MITRE ATT&CK
    mitre_techniques = Column(String, nullable=True)  # JSON string of matched techniques
    commands = Column(Text, nullable=True) # JSON string of commands
