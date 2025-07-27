# utils/http_client.py
"""
HTTP client utilities for the Finance AI Agent.
"""
import httpx
from config import config

async def fetch_json(sessionid: str, endpoint: str) -> dict:
    """
    GET /api/{endpoint} with sessionid cookie, return parsed JSON or {} on error.
    
    Args:
        sessionid: User's session ID for authentication
        endpoint: API endpoint name
        
    Returns:
        Parsed JSON response or error dict
    """
    url = f"{config.MCP_BASE_URL}/api/{endpoint}"
    headers = {"Cookie": f"sessionid={sessionid}"}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"error": str(e)}
