from fastapi import APIRouter, HTTPException, Query
from typing import Any
from app.services.cve_service import cve_service
from app.schemas.cve import CVELiistResponse

router = APIRouter()

@router.get("/", response_model=CVELiistResponse)
async def read_cves(
    days: int = Query(7, ge=1, le=120, description="Number of days to look back (max 120)"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return")
) -> Any:
    """
    Retrieve newly released CVEs.
    """
    return await cve_service.get_recent_cves(days=days, limit=limit)
