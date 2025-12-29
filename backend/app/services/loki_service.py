import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import logging
from ..config import settings

logger = logging.getLogger(__name__)

class LokiService:
    def __init__(self):
        self.base_url = settings.LOKI_URL
    
    async def query_logs(self, query: str, limit: int = 100, 
                        start_time: Optional[datetime] = None) -> List[Dict]:
        """Query logs from Loki"""
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        params = {
            "query": query,
            "limit": limit,
            "start": int(start_time.timestamp() * 1e9),  # nanoseconds
            "direction": "backward"
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/loki/api/v1/query_range",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                logs = []
                if data.get("data", {}).get("result"):
                    for stream in data["data"]["result"]:
                        for entry in stream.get("values", []):
                            logs.append({
                                "timestamp": datetime.fromtimestamp(int(entry[0]) / 1e9),
                                "message": entry[1],
                                "labels": stream.get("stream", {})
                            })
                
                return logs
        except Exception as e:
            logger.error(f"Error querying Loki: {e}")
            return []
    
    async def get_session_commands(self, session_id: str) -> List[Dict]:
        """Get command logs for a specific session"""
        query = f'{{job="honeypot",session_id="{session_id}"}}'
        logs = await self.query_logs(query, limit=1000)
        
        commands = []
        for log in logs:
            if "command:" in log["message"]:
                commands.append({
                    "timestamp": log["timestamp"],
                    "command": log["message"].split("command:")[1].strip(),
                    "response": "",
                    "lat
