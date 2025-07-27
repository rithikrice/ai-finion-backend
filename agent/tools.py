"""
ADK Tools for the Finance Agent.
These tools wrap the MCP endpoints for use with Google's Generative AI.
"""
from typing import Dict, Any, List
import json
from mcp_client import mcp_client
import google.generativeai as genai
from config import config

# Configure the Gemini API
genai.configure(api_key=config.GOOGLE_API_KEY)

# Define tool functions that the AI can use
async def get_net_worth_tool(sessionid: str) -> str:
    """
    Get the user's current net worth including assets and liabilities.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with net worth data
    """
    data = await mcp_client.get_net_worth(sessionid)
    return json.dumps(data, indent=2)

async def get_credit_report_tool(sessionid: str) -> str:
    """
    Get the user's credit report including credit score and credit history.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with credit report data
    """
    data = await mcp_client.get_credit_report(sessionid)
    return json.dumps(data, indent=2)

async def get_epf_details_tool(sessionid: str) -> str:
    """
    Get the user's EPF (Employee Provident Fund) details including balance and contributions.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with EPF details
    """
    data = await mcp_client.get_epf_details(sessionid)
    return json.dumps(data, indent=2)

async def get_mf_transactions_tool(sessionid: str) -> str:
    """
    Get the user's mutual fund transactions and portfolio details.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with mutual fund transactions
    """
    data = await mcp_client.get_mf_transactions(sessionid)
    return json.dumps(data, indent=2)

async def get_bank_transactions_tool(sessionid: str) -> str:
    """
    Get the user's bank transactions including deposits, withdrawals, and transfers.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with bank transactions
    """
    data = await mcp_client.get_bank_transactions(sessionid)
    return json.dumps(data, indent=2)

async def get_stock_transactions_tool(sessionid: str) -> str:
    """
    Get the user's stock transactions and portfolio details.
    
    Args:
        sessionid: User's session ID for authentication
    
    Returns:
        JSON string with stock transactions
    """
    data = await mcp_client.get_stock_transactions(sessionid)
    return json.dumps(data, indent=2)

# Tool definitions for Gemini using function declarations
def get_net_worth(sessionid: str) -> str:
    """Get the user's current net worth including assets and liabilities."""
    pass

def get_credit_report(sessionid: str) -> str:
    """Get the user's credit report including credit score and history."""
    pass

def get_epf_details(sessionid: str) -> str:
    """Get the user's EPF (Employee Provident Fund) details."""
    pass

def get_mf_transactions(sessionid: str) -> str:
    """Get the user's mutual fund transactions and portfolio."""
    pass

def get_bank_transactions(sessionid: str) -> str:
    """Get the user's bank transactions."""
    pass

def get_stock_transactions(sessionid: str) -> str:
    """Get the user's stock transactions and portfolio."""
    pass

# Create tools list for Gemini
FINANCE_TOOLS = [
    get_net_worth,
    get_credit_report,
    get_epf_details,
    get_mf_transactions,
    get_bank_transactions,
    get_stock_transactions
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "get_net_worth": get_net_worth_tool,
    "get_credit_report": get_credit_report_tool,
    "get_epf_details": get_epf_details_tool,
    "get_mf_transactions": get_mf_transactions_tool,
    "get_bank_transactions": get_bank_transactions_tool,
    "get_stock_transactions": get_stock_transactions_tool
}

async def execute_tool_call(tool_name: str, args: Dict[str, Any]) -> str:
    """Execute a tool call by name with given arguments."""
    if tool_name not in TOOL_FUNCTIONS:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    
    tool_func = TOOL_FUNCTIONS[tool_name]
    try:
        result = await tool_func(**args)
        return result
    except Exception as e:
        return json.dumps({"error": str(e)}) 