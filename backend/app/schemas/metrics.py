from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class MetricDataPoint(BaseModel):
    timestamp: datetime
    value: float

class MetricSeries(BaseModel):
    metric_name: str
    labels: Dict[str, str]
    data_points: List[MetricDataPoint]

class KPIMetrics(BaseModel):
    active_sessions: int
    total_attacks_detected: int
    waf_bypass_attempts: int
    avg_session_duration: float
    threat_score_avg: float
    active_honeypots: int

class ResourceMetrics(BaseModel):
    cpu_usage_percent: float
    memory_usage_mb: float
    network_ingress_mbps: float
    network_egress_mbps: float
    pod_count: int
    estimated_hourly_cost_usd: float
