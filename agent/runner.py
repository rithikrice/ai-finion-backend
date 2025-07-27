# agent/runner.py
"""
Agent runner that uses Google's Generative AI.
"""
import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from config import config
from agent.prompt_builder import build_prompt, build_enhanced_context
from mcp_client import mcp_client
from goals_manager import goals_manager
import logging

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel(model_name=config.GEMINI_MODEL)

async def run_agent_with_context(user_prompt: str, sessionid: str) -> str:
    """
    Run the AI agent with the user's prompt and session context.
    
    Args:
        user_prompt: The user's question or request
        sessionid: User's session ID for authentication
        
    Returns:
        The AI's response as a string
    """
    try:
        # Fetch enhanced context with spending analysis and goals
        context = await build_enhanced_context(sessionid, mcp_client, goals_manager)
        
        # Build the full prompt with context
        full_prompt = build_prompt(user_prompt, context)
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        if response.text:
            return response.text
        else:
            return "I couldn't generate a response. Please try again."
            
    except Exception as e:
        logger.error(f"Error in agent runner: {e}")
        raise

async def run_agent_streaming(user_prompt: str, sessionid: str):
    """
    Run the AI agent with streaming response.
    
    Args:
        user_prompt: The user's question or request
        sessionid: User's session ID for authentication
        
    Yields:
        Chunks of the AI's response
    """
    try:
        # Fetch enhanced context with spending analysis and goals
        context = await build_enhanced_context(sessionid, mcp_client, goals_manager)
        
        # Build the full prompt with context
        full_prompt = build_prompt(user_prompt, context)
        
        # Generate response with streaming
        response = model.generate_content(full_prompt, stream=True)
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        logger.error(f"Error in streaming agent: {e}")
        yield f"Error: {str(e)}"

async def run_query(prompt: str, use_flash: bool = False) -> Dict[str, Any]:
    """
    Run a query with the AI model using the provided prompt.
    
    Args:
        prompt: The complete prompt to send to the model
        use_flash: Whether to use Gemini 1.5 Flash (ignored, always uses configured model)
        
    Returns:
        Dict with 'response' key containing the AI's response
    """
    try:
        # Generate response
        response = model.generate_content(prompt)
        
        return {
            "response": response.text,
            "model": config.GEMINI_MODEL
        }
    except Exception as e:
        logger.error(f"Error in run_query: {e}")
        return {
            "response": f"I encountered an error processing your request: {str(e)}",
            "error": str(e)
        }
