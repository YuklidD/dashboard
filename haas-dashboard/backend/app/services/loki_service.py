import requests

class LokiService:
    def __init__(self, url="http://loki:3100"):
        self.base_url = url

    def query_logs(self, query, limit=100):
        try:
            params = {'query': query, 'limit': limit}
            response = requests.get(f"{self.base_url}/loki/api/v1/query_range", params=params)
            if response.status_code == 200:
                return response.json()
            return {"error": response.text}
        except Exception as e:
            return {"error": str(e)}

loki_service = LokiService()
