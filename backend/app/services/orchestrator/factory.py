from functools import lru_cache
from app.core.config import settings
from app.services.orchestrator.base import HoneypotOrchestrator
from app.services.orchestrator.mock import MockOrchestrator
from app.services.orchestrator.k8s import K8sOrchestrator

@lru_cache()
def get_orchestrator() -> HoneypotOrchestrator:
    if settings.ORCHESTRATOR_TYPE == "k8s":
        return K8sOrchestrator()
    return MockOrchestrator()
