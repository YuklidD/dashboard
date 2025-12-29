from prometheus_api_client import PrometheusConnect
import os

class PrometheusService:
    def __init__(self, url="http://prometheus-server"):
        self.prom = PrometheusConnect(url=url, disable_ssl=True)

    def get_metric(self, metric_name):
        try:
            return self.prom.get_current_metric_value(metric_name)
        except Exception as e:
            print(f"Error fetching metric {metric_name}: {e}")
            return []

    def get_custom_query(self, query):
        try:
            return self.prom.custom_query(query)
        except Exception as e:
            print(f"Error executing query {query}: {e}")
            return []

prom_service = PrometheusService()
