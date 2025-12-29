from fastapi import APIRouter
from app.api.v1.endpoints import auth, honeypots, observability, websockets

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(honeypots.router, prefix="/honeypots", tags=["honeypots"])
api_router.include_router(observability.router, prefix="/observability", tags=["observability"])
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
