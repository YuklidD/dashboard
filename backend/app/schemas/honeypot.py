from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class HoneypotCreate(BaseModel):
    honeypot_type: str  # shellm, ssh, http
    replicas: int = 1
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    duration_minutes: Optional[int] = 60

class HoneypotStatus(BaseModel):
    pod_name: str
    status: str  # running, pending, terminated
    node: Optional[str]
    ip: Optional[str]
    start_time: Optional[datetime]
    uptime_seconds: Optional[int]

class HoneypotResponse(BaseModel):
    deployment_name: str
    namespace: str
    replicas: int
    pods: List[HoneypotStatus]

class SessionCommand(BaseModel):
    timestamp: datetime
    command: str
    response: Optional[str]
    latency_ms: float
    threat_indicator: Optional[str]

class SessionDetail(BaseModel):
    session_id: str
    honeypot_type: str
    source_ip: str
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    commands: List[SessionCommand]
    threat_score: float
    status: str
