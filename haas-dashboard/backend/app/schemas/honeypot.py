from pydantic import BaseModel
from typing import Optional, List, Dict

class HoneypotConfig(BaseModel):
    name: str
    image: str
    port: int
    replicas: int = 1
    env: Optional[Dict[str, str]] = None

class HoneypotStatus(BaseModel):
    name: str
    status: str
    available_replicas: int
    age: str
