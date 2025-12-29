from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import auth_router, honeypots_router, waf_router, metrics_router, sessions_router, websocket_router
from app.database import SessionLocal, engine, Base
from app.models import User, Session, Alert, Policy # Ensure models are registered

# Create tables on module import or startup
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to HaaS Dashboard API"}

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(honeypots_router, prefix=f"{settings.API_V1_STR}/honeypots", tags=["honeypots"])
app.include_router(waf_router, prefix=f"{settings.API_V1_STR}/waf", tags=["waf"])
app.include_router(metrics_router, prefix=f"{settings.API_V1_STR}/metrics", tags=["metrics"])
app.include_router(sessions_router, prefix=f"{settings.API_V1_STR}/sessions", tags=["sessions"])
app.include_router(websocket_router, tags=["websocket"])

@app.on_event("startup")
def startup_event():
    from app.services.auth_service import get_password_hash
    import time
    from sqlalchemy.exc import OperationalError
    
    # Debug: Print registered tables
    print("Registered tables:", Base.metadata.tables.keys())
    
    # Retry loop for DB connection and table creation
    max_retries = 5
    for i in range(max_retries):
        try:
            print(f"Attempting to connect to DB (Attempt {i+1}/{max_retries})...")
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully.")
            break
        except OperationalError as e:
            print(f"DB not ready yet: {e}")
            time.sleep(2)
    else:
        print("Could not connect to DB after multiple retries.")
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "admin@haas.com").first()
        hashed_password = get_password_hash("admin123")
        if not user:
            user = User(email="admin@haas.com", hashed_password=hashed_password, is_active=True, is_superuser=True)
            db.add(user)
            print("Created default user: admin@haas.com / admin123")
        else:
            user.hashed_password = hashed_password
            print("Updated default user password")
        
        db.commit()
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()
