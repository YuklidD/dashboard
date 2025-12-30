from abc import ABC, abstractmethod
from typing import List, Optional
from app.models.observability import HoneypotMetrics, LogEntry, SessionLog

class ObservabilityService(ABC):
    @abstractmethod
    def get_metrics(self, honeypot_id: str, time_range: str = "1h") -> HoneypotMetrics:
        """Get metrics for a specific honeypot."""
        pass

    @abstractmethod
    def get_logs(self, honeypot_id: str, limit: int = 100) -> List[LogEntry]:
        """Get recent logs for a honeypot."""
        pass

    @abstractmethod
    def ingest_log(self, log_data: LogEntry) -> bool:
        """Ingest a system log from a honeypot."""
        pass

    @abstractmethod
    def ingest_session_log(self, session_data: SessionLog) -> bool:
        """Ingest a session log from a honeypot."""
        pass
    
    @abstractmethod
    def get_sessions(self, honeypot_id: Optional[str] = None) -> List[SessionLog]:
        """Get recorded sessions."""
        pass
