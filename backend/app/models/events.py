from typing import Any, Dict, Optional
from pydantic import BaseModel

class WebSocketEvent(BaseModel):
    type: str # e.g., "honeypot_status", "attack_alert"
    payload: Dict[str, Any]
    timestamp: Optional[str] = None
