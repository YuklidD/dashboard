from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class MetricPoint(BaseModel):
    timestamp: datetime
    value: float
    unit: str

class HoneypotMetrics(BaseModel):
    honeypot_id: str
    cpu_usage: List[MetricPoint]
    memory_usage: List[MetricPoint]
    network_in: List[MetricPoint]
    network_out: List[MetricPoint]

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    source: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

class SessionLog(BaseModel):
    session_id: str
    honeypot_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    attacker_ip: str
    commands: List[Dict[str, Any]] # e.g., {"timestamp": ..., "input": ..., "output": ...}
