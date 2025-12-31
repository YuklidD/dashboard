from typing import Dict, Optional, Tuple
import random

class GeoService:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path
        # In a real implementation, we would load the MaxMind DB here
        # self.reader = geoip2.database.Reader(db_path) if db_path else None

    def resolve_ip(self, ip_address: str) -> Dict[str, any]:
        """
        Resolve an IP address to geolocation data.
        Returns a dictionary with latitude, longitude, and country.
        """
        # 1. Try real lookup if configured (Skipped for this mock)
        
        # 2. Simulation Mode / Fallback: Return random plausible coordinates
        # Generates coordinates roughly around major cities/continents to look realistic
        
        # Simple consistent hashing for "stable" random per IP
        seed = sum(ord(c) for c in ip_address)
        random.seed(seed)
        
        lat = random.uniform(-50, 60)
        lon = random.uniform(-120, 140)
        
        # Randomly assign a country from a small list of frequent "attacker" locations
        countries = ["CN", "RU", "US", "KP", "IR", "BR", "DE"]
        country = random.choice(countries)

        return {
            "latitude": lat,
            "longitude": lon,
            "country": country,
            "city": "Unknown"
        }

# Global instance
geo_service = GeoService()
