from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

class HoneypotStatus(str, Enum):
    PENDING = "Pending"
    RUNNING = "Running"
    TERMINATING = "Terminating"
    TERMINATED = "Terminated"
    ERROR = "Error"

class HoneypotBase(BaseModel):
    name: str
    image: str = "shellm-honeypot:latest"

class HoneypotCreate(HoneypotBase):
    pass

class Honeypot(HoneypotBase):
    id: str
    status: HoneypotStatus
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
