"""
Configuration module for the Finance Agent application.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Google ADK
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    
    # Vertex AI Configuration
    VERTEX_AI_PROJECT_ID: str = os.getenv("VERTEX_AI_PROJECT_ID", "")
    VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")
    VERTEX_AI_MODEL: str = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-flash")
    USE_VERTEX_AI: bool = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
    
    # MCP Server
    MCP_BASE_URL: str = os.getenv("MCP_BASE_URL", "http://localhost:8080")
    
    # Application
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    APP_NAME: str = "Finance AI Agent"
    APP_VERSION: str = "1.0.0"
    
    # MCP Endpoints
    MCP_ENDPOINTS = [
        "net_worth",
        "credit_report", 
        "epf_details",
        "mf_transactions",
        "bank_transactions",
        "stock_transactions"
    ]
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        if not cls.MCP_BASE_URL:
            raise ValueError("MCP_BASE_URL environment variable is required")
        
        if cls.USE_VERTEX_AI and not cls.VERTEX_AI_PROJECT_ID:
            raise ValueError("VERTEX_AI_PROJECT_ID environment variable is required when USE_VERTEX_AI is enabled")

# Create a singleton instance
config = Config() 