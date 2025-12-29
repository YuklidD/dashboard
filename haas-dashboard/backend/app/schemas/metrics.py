from pydantic import BaseModel
from typing import List, Dict, Any

class MetricData(BaseModel):
    name: str
    values: List[Dict[str, Any]] # timestamp, value

class SystemHealth(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    status: str
