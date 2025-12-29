from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.honeypot import Honeypot, HoneypotCreate

class HoneypotOrchestrator(ABC):
    @abstractmethod
    def deploy_honeypot(self, honeypot_create: HoneypotCreate) -> Honeypot:
        """Deploy a new honeypot instance."""
        pass

    @abstractmethod
    def terminate_honeypot(self, honeypot_id: str) -> bool:
        """Terminate a running honeypot."""
        pass

    @abstractmethod
    def get_honeypot(self, honeypot_id: str) -> Optional[Honeypot]:
        """Get status of a specific honeypot."""
        pass

    @abstractmethod
    def list_honeypots(self) -> List[Honeypot]:
        """List all managed honeypots."""
        pass
