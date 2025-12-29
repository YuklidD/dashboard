from prometheus_api_client import PrometheusConnect
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class PrometheusService:
    def __init__(self):
        self.prom = PrometheusConnect(url=settings.PROMETHEUS_URL, disable_ssl=True)
    
    def get_active_sessions_count(self) -> int:
        """Get current count of active honeypot sessions"""
        try:
            query = 'sum(haas_active_sessions)'
            result = self.prom.custom_query(query=query)
            if result and len(result) > 0:
                return int(float(result[0]['value'][1]))
            return 0
        except Exception as e:
            logger.error(f"Error querying active sessions: {e}")
            return 0
    
    def get_waf_bypass_attempts(self, hours: int = 24) -> int:
        """Get WAF bypass attempts in last N hours"""
        try:
            query = f'sum(increase(haas_waf_bypass_detected_total[{hours}h]))'
            result = self.prom.custom_query(query=query)
            if result and len(result) > 0:
                return int(float(result[0]['value'][1]))
            return 0
        except Exception as e:
            logger.error(f"Error querying WAF bypasses: {e}")
            return 0
    
    def get_avg_session_duration(self) -> float:
        """Get average session duration in seconds"""
        try:
            query = 'avg(haas_session_duration_seconds)'
            result = self.prom.custom_query(query=query)
            if result and len(result) > 0:
                return float(result[0]['value'][1])
            return 0.0
        except Exception as e:
            logger.error(f"Error querying avg duration: {e}")
            return 0.0
    
    def get_threat_score_avg(self) -> float:
        """Get average threat score across sessions"""
        try:
            query = 'avg(haas_threat_score)'
            result = self.prom.custom_query(query=query)
            if result and len(result) > 0:
                return float(result[0]['value'][1])
            return 0.0
        except Exception as e:
            logger.error(f"Error querying threat score: {e}")
            return 0.0
    
    def get_resource_metrics(self) -> Dict:
        """Get current resource utilization metrics"""
        try:
            cpu_query = 'sum(rate(container_cpu_usage_seconds_total{namespace="haas"}[5m])) * 100'
            memory_query = 'sum(container_memory_usage_bytes{namespace="haas"}) / 1024 / 1024'
            pod_count_query = 'count(kube_pod_info{namespace="haas"})'
            
            cpu_result = self.prom.custom_query(query=cpu_query)
            memory_result = self.prom.custom_query(query=memory_query)
            pod_result = self.prom.custom_query(query=pod_count_query)
            
            return {
                "cpu_usage_percent": float(cpu_result[0]['value'][1]) if cpu_result else 0.0,
                "memory_usage_mb": float(memory_result[0]['value'][1]) if memory_result else 0.0,
                "pod_count": int(float(pod_result[0]['value'][1])) if pod_result else 0,
                "network_ingress_mbps": 12.5,  # Mock data
                "network_egress_mbps": 8.3,
                "estimated_hourly_cost_usd": 0.45
            }
        except Exception as e:
            logger.error(f"Error querying resource metrics: {e}")
            return {
                "cpu_usage_percent": 0.0,
                "memory_usage_mb": 0.0,
                "pod_count": 0,
                "network_ingress_mbps": 0.0,
                "network_egress_mbps": 0.0,
                "estimated_hourly_cost_usd": 0.0
            }
    
    def get_time_series(self, metric_name: str, duration_hours: int = 24) -> List[Dict]:
        """Get time series data for a metric"""
        try:
            query = f'{metric_name}[{duration_hours}h]'
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=duration_hours)
            
            result = self.prom.custom_query_range(
                query=metric_name,
                start_time=start_time,
                end_time=end_time,
                step='5m'
            )
            
            data_points = []
            if result and len(result) > 0:
                for item in result[0]['values']:
                    data_points.append({
                        "timestamp": datetime.fromtimestamp(item[0]),
                        "value": float(item[1])
                    })
            
            return data_points
        except Exception as e:
            logger.error(f"Error querying time series: {e}")
            return []

prometheus_service = PrometheusService()
