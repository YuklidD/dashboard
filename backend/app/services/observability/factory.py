from functools import lru_cache
from app.core.config import settings
from app.services.observability.base import ObservabilityService
from app.services.observability.mock import MockObservabilityService

@lru_cache()
def get_observability_service() -> ObservabilityService:
    # In the future, we can add RealObservabilityService here
    return MockObservabilityService()
