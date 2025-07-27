# agent/context_fetcher.py
"""
Context fetcher for the Finance AI Agent.
Uses the MCP client to fetch all user data.
"""
from typing import Dict, Any
from mcp_client import mcp_client

async def get_user_context(sessionid: str) -> Dict[str, Any]:
    """
    Fetches all MCP data for the given sessionid.
    Returns a dict with all user financial data.
    
    Args:
        sessionid: User's session ID for authentication
        
    Returns:
        Dictionary containing all user financial data
    """
    return await mcp_client.get_all_user_data(sessionid)
