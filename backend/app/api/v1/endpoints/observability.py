from typing import List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.models.observability import HoneypotMetrics, LogEntry, SessionLog
from app.models.alert import Alert
from sqlalchemy.orm import Session
from app.services.observability.factory import get_observability_service
from app.services.observability.base import ObservabilityService
from app.core.websockets import manager
from datetime import datetime

router = APIRouter()

from app.schemas.alert import Alert as AlertSchema

@router.get("/alerts", response_model=List[AlertSchema])
def get_alerts(
    limit: int = 50,
    current_user: User = Depends(deps.get_current_active_user),
    db: Session = Depends(deps.get_db)  # Need to add db dependency import
):
    """
    Get recent alerts for the dashboard.
    """
    return db.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()

@router.post("/alerts/")
async def receive_alert(alert: dict):
    """
    Receive an external alert (e.g. from WAF) and broadcast it.
    """
    # Format for WebSocket
    event = {
        "type": "waf_bypass",
        "payload": {
            "source_ip": alert.get("source_ip", "unknown"),
            "payload": alert.get("payload", ""),
            "timestamp": alert.get("timestamp", datetime.utcnow().isoformat()),
            "severity": "HIGH",
            "confidence": alert.get("confidence", 1.0)
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(event)
    return {"status": "broadcasted"}

@router.get("/metrics", response_model=HoneypotMetrics)
def get_metrics(
    honeypot_id: str,
    time_range: str = "1h",
    current_user: User = Depends(deps.get_current_active_user),
    service: ObservabilityService = Depends(get_observability_service)
) -> Any:
    """
    Get metrics for a honeypot.
    """
    return service.get_metrics(honeypot_id, time_range)

@router.get("/logs", response_model=List[LogEntry])
def get_logs(
    honeypot_id: str,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
    service: ObservabilityService = Depends(get_observability_service)
) -> Any:
    """
    Get logs for a honeypot.
    """
    return service.get_logs(honeypot_id, limit)

@router.post("/sessions", response_model=dict)
def ingest_session(
    session_data: SessionLog,
    # In a real scenario, this might be authenticated via a service token, not user token
    # For now, we'll allow it or require a specific permission
    service: ObservabilityService = Depends(get_observability_service)
) -> Any:
    """
    Ingest a session log (called by honeypot).
    """
    success = service.ingest_session_log(session_data)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to ingest session")
    return {"message": "Session ingested successfully"}

@router.get("/sessions", response_model=List[SessionLog])
def get_sessions(
    honeypot_id: Optional[str] = None,
    current_user: User = Depends(deps.get_current_active_user),
    service: ObservabilityService = Depends(get_observability_service)
) -> Any:
    """
    Get recorded sessions.
    """
    return service.get_sessions(honeypot_id)
