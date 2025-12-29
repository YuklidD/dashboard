import uuid
from datetime import datetime
from typing import List, Optional, Dict
from app.services.orchestrator.base import HoneypotOrchestrator
from app.models.honeypot import Honeypot, HoneypotCreate, HoneypotStatus

class MockOrchestrator(HoneypotOrchestrator):
    def __init__(self):
        self._honeypots: Dict[str, Honeypot] = {}

    def deploy_honeypot(self, honeypot_create: HoneypotCreate) -> Honeypot:
        honeypot_id = str(uuid.uuid4())
        honeypot = Honeypot(
            id=honeypot_id,
            name=honeypot_create.name,
            image=honeypot_create.image,
            status=HoneypotStatus.RUNNING, # Immediate running for mock
            ip_address="192.168.1.100",
            created_at=datetime.utcnow()
        )
        self._honeypots[honeypot_id] = honeypot
        return honeypot

    def terminate_honeypot(self, honeypot_id: str) -> bool:
        if honeypot_id in self._honeypots:
            self._honeypots[honeypot_id].status = HoneypotStatus.TERMINATED
            # In a real mock, we might keep it for history, but here we can just delete or mark terminated
            del self._honeypots[honeypot_id]
            return True
        return False

    def get_honeypot(self, honeypot_id: str) -> Optional[Honeypot]:
        return self._honeypots.get(honeypot_id)

    def list_honeypots(self) -> List[Honeypot]:
        return list(self._honeypots.values())
