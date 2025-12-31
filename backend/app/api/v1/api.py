from fastapi import APIRouter
from app.api.v1.endpoints import auth, honeypots, observability, websockets, cves, ioc

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(honeypots.router, prefix="/honeypots", tags=["honeypots"])
api_router.include_router(observability.router, prefix="/observability", tags=["observability"])
api_router.include_router(websockets.router, prefix="/ws", tags=["websockets"])
api_router.include_router(cves.router, prefix="/cves", tags=["cves"])
api_router.include_router(ioc.router, prefix="/ioc", tags=["ioc"])
