from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.models.user import User
from app.models.honeypot import Honeypot, HoneypotCreate
from app.services.orchestrator.factory import get_orchestrator
from app.services.orchestrator.base import HoneypotOrchestrator

router = APIRouter()

@router.post("/", response_model=Honeypot)
def deploy_honeypot(
    *,
    honeypot_in: HoneypotCreate,
    # current_user: User = Depends(deps.get_current_active_user), # DISABLED FOR DEMO
    orchestrator: HoneypotOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Deploy a new honeypot.
    """
    return orchestrator.deploy_honeypot(honeypot_in)

@router.get("/", response_model=List[Honeypot])
def list_honeypots(
    current_user: User = Depends(deps.get_current_active_user),
    orchestrator: HoneypotOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    List all honeypots.
    """
    return orchestrator.list_honeypots()

@router.get("/{honeypot_id}", response_model=Honeypot)
def get_honeypot(
    honeypot_id: str,
    current_user: User = Depends(deps.get_current_active_user),
    orchestrator: HoneypotOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Get honeypot status.
    """
    honeypot = orchestrator.get_honeypot(honeypot_id)
    if not honeypot:
        raise HTTPException(status_code=404, detail="Honeypot not found")
    return honeypot

@router.delete("/{honeypot_id}", response_model=dict)
def terminate_honeypot(
    honeypot_id: str,
    current_user: User = Depends(deps.get_current_active_superuser),
    orchestrator: HoneypotOrchestrator = Depends(get_orchestrator)
) -> Any:
    """
    Terminate a honeypot (Admin only).
    """
    success = orchestrator.terminate_honeypot(honeypot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Honeypot not found or could not be terminated")
    return {"message": "Honeypot terminated successfully"}
