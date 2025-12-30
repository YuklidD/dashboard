from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CVEMetric(BaseModel):
    baseScore: Optional[float] = None
    severity: Optional[str] = None

class CVEItem(BaseModel):
    id: str
    sourceIdentifier: str
    published: datetime
    lastModified: datetime
    vulnStatus: str
    description: str
    metrics: Optional[CVEMetric] = None
    
class CVELiistResponse(BaseModel):
    timestamp: datetime
    totalResults: int
    cves: List[CVEItem]
