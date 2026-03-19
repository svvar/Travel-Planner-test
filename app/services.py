import httpx
import time
from fastapi import HTTPException
from typing import Optional

# Cache structure: { external_id: (timestamp, data) }
# TTL of 1 hour (3600 seconds)
api_cache = {}
CACHE_TTL = 3600

ART_INSTITUTE_BASE_URL = "https://api.artic.edu/api/v1"

async def check_place_exists(external_id: int) -> bool:
    """Verifies if a place (artwork) exists in the Art Institute API."""
    now = time.time()
    
    # Check cache
    if external_id in api_cache:
        cached_time, _ = api_cache[external_id]
        if now - cached_time < CACHE_TTL:
            return True
        else:
            del api_cache[external_id]

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{ART_INSTITUTE_BASE_URL}/artworks/{external_id}")
            if response.status_code == 200:
                api_cache[external_id] = (now, response.json())
                return True
            elif response.status_code == 404:
                return False
            else:
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
    return False
