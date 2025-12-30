import httpx
from datetime import datetime, timedelta
from typing import List, Optional
import logging

from app.schemas.cve import CVEItem, CVEMetric, CVELiistResponse

logger = logging.getLogger(__name__)

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

class CVEService:
    async def get_recent_cves(self, days: int = 7, limit: int = 20) -> CVELiistResponse:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # NVD requires ISO 8601 format: YYYY-MM-DDThh:mm:ss.s
        # Example: 2021-08-04T00:00:00.000
        pub_start_date = start_date.strftime("%Y-%m-%dT%H:%M:%S.000")
        pub_end_date = end_date.strftime("%Y-%m-%dT%H:%M:%S.000")
        
        params = {
            "pubStartDate": pub_start_date,
            "pubEndDate": pub_end_date,
            "resultsPerPage": limit,
            "noRejected": "" # exclude rejected
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(NVD_API_URL, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                
                cve_items = []
                for item in data.get("vulnerabilities", []):
                    cve_data = item.get("cve", {})
                    
                    # unique ID
                    cve_id = cve_data.get("id")
                    
                    # description (find english)
                    descriptions = cve_data.get("descriptions", [])
                    desc_text = "No description available"
                    for d in descriptions:
                        if d.get("lang") == "en":
                            desc_text = d.get("value")
                            break
                    
                    # metrics (try v3.1, then v3.0, then v2)
                    metrics_data = cve_data.get("metrics", {})
                    base_score = None
                    severity = None
                    
                    if "cvssMetricV31" in metrics_data:
                        m = metrics_data["cvssMetricV31"][0].get("cvssData", {})
                        base_score = m.get("baseScore")
                        severity = m.get("baseSeverity")
                    elif "cvssMetricV30" in metrics_data:
                        m = metrics_data["cvssMetricV30"][0].get("cvssData", {})
                        base_score = m.get("baseScore")
                        severity = m.get("baseSeverity")
                    elif "cvssMetricV2" in metrics_data:
                        m = metrics_data["cvssMetricV2"][0].get("cvssData", {})
                        base_score = m.get("baseScore")
                        severity = metrics_data["cvssMetricV2"][0].get("baseSeverity") # usually outside cvssData
                        
                    cve_items.append(CVEItem(
                        id=cve_id,
                        sourceIdentifier=cve_data.get("sourceIdentifier", ""),
                        published=datetime.fromisoformat(cve_data.get("published")),
                        lastModified=datetime.fromisoformat(cve_data.get("lastModified")),
                        vulnStatus=cve_data.get("vulnStatus", ""),
                        description=desc_text,
                        metrics=CVEMetric(baseScore=base_score, severity=severity) if base_score else None
                    ))
                
                return CVELiistResponse(
                    timestamp=datetime.now(),
                    totalResults=data.get("totalResults", 0),
                    cves=cve_items
                )
                
            except Exception as e:
                logger.error(f"Error fetching CVEs: {str(e)}")
                # Return empty list on error for now, or raise
                return CVELiistResponse(
                    timestamp=datetime.now(),
                    totalResults=0,
                    cves=[]
                )

cve_service = CVEService()
