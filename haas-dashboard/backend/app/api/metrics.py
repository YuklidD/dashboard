from fastapi import APIRouter
from app.services.prometheus_service import prom_service

router = APIRouter()

@router.get("/cpu")
def get_cpu_metrics():
    return prom_service.get_metric("container_cpu_usage_seconds_total")

@router.get("/memory")
def get_memory_metrics():
    return prom_service.get_metric("container_memory_usage_bytes")
