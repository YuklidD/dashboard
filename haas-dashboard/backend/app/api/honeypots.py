from fastapi import APIRouter, Depends
from app.services.kubernetes_service import k8s_service
from app.schemas.honeypot import HoneypotStatus

router = APIRouter()

@router.get("/", response_model=list[HoneypotStatus])
def get_honeypots():
    deployments = k8s_service.list_deployments()
    honeypots = []
    if deployments:
        for d in deployments.items:
            # Filter for honeypot deployments based on label or name convention
            if "honeypot" in d.metadata.name:
                honeypots.append(HoneypotStatus(
                    name=d.metadata.name,
                    status="Running" if d.status.ready_replicas else "Pending",
                    available_replicas=d.status.ready_replicas or 0,
                    age=str(d.metadata.creation_timestamp)
                ))
    return honeypots
