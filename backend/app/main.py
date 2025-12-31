from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base, SessionLocal
from app.models.user import User, UserRole
from app.models.alert import Alert
from app.models.session import HoneypotSession
from app.core.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

from app.core.simulation import start_simulation
import asyncio

@app.on_event("startup")
async def create_initial_data():
    db = SessionLocal()
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            hashed_password=get_password_hash("admin"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(user)
        db.commit()
    db.close()
    
    if settings.ENVIRONMENT == "local":
        print(f"ENVIRONMENT is {settings.ENVIRONMENT}, starting simulation...")
        asyncio.create_task(start_simulation())

@app.get("/")
def root():
    return {"message": "HaaS Dashboard Backend API"}
