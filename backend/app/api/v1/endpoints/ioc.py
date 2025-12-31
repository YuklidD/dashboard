from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import csv
import io
import json

from app.api.deps import get_db
from app.models.session import HoneypotSession
from app.models.alert import Alert

router = APIRouter()

@router.get("/export", response_model=None)
def export_iocs(
    format: str = Query("json", enum=["json", "csv"]),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Export Indicators of Compromise (IOCs) from recorded sessions and alerts.
    Supports JSON and CSV formats.
    """
    # Simply fetch all sessions/alerts for now to extract IPs/Hashes
    # In a real app we'd filter by date
    sessions = db.query(HoneypotSession).all()
    alerts = db.query(Alert).all()
    
    iocs = []
    seen_ips = set()
    
    # Collect from Sessions
    for session in sessions:
        if session.source_ip and session.source_ip not in seen_ips:
            iocs.append({
                "type": "ipv4-addr",
                "value": session.source_ip,
                "source": "HaaS Honeypot",
                "confidence": "High",
                "tags": ["scanner", "honeypot-interaction"],
                "country": session.country,
                "timestamp": session.start_time.isoformat() if session.start_time else None
            })
            seen_ips.add(session.source_ip)
            
    # Collect from Alerts
    for alert in alerts:
        if alert.source_ip and alert.source_ip not in seen_ips:
            iocs.append({
                "type": "ipv4-addr",
                "value": alert.source_ip,
                "source": "HaaS WAF Alert",
                "confidence": "High",
                "tags": [alert.alert_type],
                "country": alert.country,
                "timestamp": alert.timestamp.isoformat() if alert.timestamp else None
            })
            seen_ips.add(alert.source_ip)

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Type", "Value", "Source", "Confidence", "Tags", "Country", "Timestamp"])
        for ioc in iocs:
            writer.writerow([
                ioc["type"], 
                ioc["value"], 
                ioc["source"], 
                ioc["confidence"], 
                ",".join(ioc["tags"]),
                ioc["country"],
                ioc["timestamp"]
            ])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=haas_iocs.csv"}
        )
        
    return JSONResponse(content={"count": len(iocs), "iocs": iocs})
