from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HaaS Dashboard"
    
    # Security
    SECRET_KEY: str = "changethis-to-a-secure-random-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Environment
    ENVIRONMENT: Literal["local", "cloud"] = "local"
    ORCHESTRATOR_TYPE: Literal["mock", "k8s"] = "mock"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
