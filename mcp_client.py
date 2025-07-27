"""
MCP Client for interacting with the Go MCP server.
Handles both REST (polling) and SSE (streaming) endpoints.
"""
import httpx
import json
from typing import Dict, Any, AsyncGenerator, Optional
from config import config
import logging

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for interacting with the Go MCP server."""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.MCP_BASE_URL
        self.timeout = httpx.Timeout(30.0, connect=10.0)
        
    def _get_headers(self, sessionid: str) -> Dict[str, str]:
        """Get headers with session cookie."""
        return {"Cookie": f"sessionid={sessionid}"}
    
    # REST endpoints (polling)
    async def get_net_worth(self, sessionid: str) -> Dict[str, Any]:
        """Get net worth data via REST."""
        return await self._fetch_json(sessionid, "net_worth")
    
    async def get_credit_report(self, sessionid: str) -> Dict[str, Any]:
        """Get credit report data via REST."""
        return await self._fetch_json(sessionid, "credit_report")
    
    async def get_epf_details(self, sessionid: str) -> Dict[str, Any]:
        """Get EPF details via REST."""
        return await self._fetch_json(sessionid, "epf_details")
    
    async def get_mf_transactions(self, sessionid: str) -> Dict[str, Any]:
        """Get mutual fund transactions via REST."""
        return await self._fetch_json(sessionid, "mf_transactions")
    
    async def get_bank_transactions(self, sessionid: str) -> Dict[str, Any]:
        """Get bank transactions via REST."""
        return await self._fetch_json(sessionid, "bank_transactions")
    
    async def get_stock_transactions(self, sessionid: str) -> Dict[str, Any]:
        """Get stock transactions via REST."""
        return await self._fetch_json(sessionid, "stock_transactions")
    
    async def _fetch_json(self, sessionid: str, endpoint: str) -> Dict[str, Any]:
        """Fetch JSON data from a REST endpoint."""
        url = f"{self.base_url}/api/{endpoint}"
        headers = self._get_headers(sessionid)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching {endpoint}: {e}")
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return {"error": str(e)}
    
    # SSE endpoints (streaming)
    async def stream_net_worth(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream net worth data via SSE."""
        async for event in self._stream_sse(sessionid, "net_worth"):
            yield event
    
    async def stream_credit_report(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream credit report data via SSE."""
        async for event in self._stream_sse(sessionid, "credit_report"):
            yield event
    
    async def stream_epf_details(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream EPF details via SSE."""
        async for event in self._stream_sse(sessionid, "epf_details"):
            yield event
    
    async def stream_mf_transactions(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream mutual fund transactions via SSE."""
        async for event in self._stream_sse(sessionid, "mf_transactions"):
            yield event
    
    async def stream_bank_transactions(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream bank transactions via SSE."""
        async for event in self._stream_sse(sessionid, "bank_transactions"):
            yield event
    
    async def stream_stock_transactions(self, sessionid: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream stock transactions via SSE."""
        async for event in self._stream_sse(sessionid, "stock_transactions"):
            yield event
    
    async def _stream_sse(self, sessionid: str, endpoint: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream SSE data from an endpoint."""
        url = f"{self.base_url}/stream/{endpoint}"
        headers = self._get_headers(sessionid)
        headers["Accept"] = "text/event-stream"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data.strip():
                                try:
                                    yield json.loads(data)
                                except json.JSONDecodeError:
                                    logger.error(f"Invalid JSON in SSE: {data}")
                                    
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error streaming {endpoint}: {e}")
            yield {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            logger.error(f"Error streaming {endpoint}: {e}")
            yield {"error": str(e)}
    
    # Batch fetch all data
    async def get_all_user_data(self, sessionid: str) -> Dict[str, Any]:
        """Fetch all user data from all endpoints."""
        data = {}
        
        for endpoint in config.MCP_ENDPOINTS:
            method = getattr(self, f"get_{endpoint}")
            data[endpoint] = await method(sessionid)
        
        return data

# Create a singleton instance
mcp_client = MCPClient() 