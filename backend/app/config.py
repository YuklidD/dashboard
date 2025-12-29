from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "HaaS Dashboard"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str = "postgresql://haas:haas_password@postgres:5432/haas_db"
    
    # Kubernetes
    K8S_NAMESPACE: str = "haas"
    K8S_IN_CLUSTER: bool = True
    
    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus:9090"
    
    # Loki
    LOKI_URL: str = "http://loki:3100"
    
    class Config:
        env_file = ".env"

settings = Settings()
