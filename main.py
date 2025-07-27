# main.py
"""
Main entry point for the Finance AI Agent application.
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from datetime import datetime, timedelta

from config import config
from api import router
from goals_manager import goals_manager
from agent import prompt_builder
from mcp_client import mcp_client
from data_processor import TransactionProcessor
from agent.runner import run_query

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logging.info("Starting Finance AI Agent...")
    
    # Validate configuration
    config.validate()
    
    # Note: No demo data loading needed - MCP server provides rich, realistic data
    logging.info("Finance AI Agent ready - using MCP server data")
    
    yield
    
    # Shutdown
    logging.info("Shutting down Finance AI Agent...")

# Create FastAPI app
app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Personal Finance AI Agent with Google Gemini - Hackathon Demo",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "demo_mode": config.DEBUG
    }

async def generate():
    """
    Streams a placeholder response for the /stream/net_worth endpoint.
    In a real application, this would be replaced with actual streaming data.
    """
    yield "data: {\"net_worth\": 123456.78}\n\n"

@app.get("/stream/net_worth")
async def stream_net_worth():
    """
    Streams net worth data.
    """
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/api/ask-ai")
async def ask_ai(request: Request, background_tasks: BackgroundTasks):
    """
    Personal CFO endpoint - uses intelligent query analysis to fetch only relevant data.
    Provides focused, specific answers to user questions.
    """
    sessionid = request.cookies.get("sessionid")
    if not sessionid:
        raise HTTPException(status_code=401, detail="No session cookie found")
    
    # Get request body
    try:
        body = await request.json()
        logging.info(f"Request body: {body}")
        user_query = body.get("query", "").strip()
        logging.info(f"User query: '{user_query}'")
        if not user_query:
            raise HTTPException(status_code=400, detail="Query is required")
    except Exception as e:
        logging.error(f"Error parsing request body: {e}")
        raise HTTPException(status_code=400, detail="Invalid request body")
    
    # Get or create smart assistant
    try:
        from agent.ai_assistant import get_smart_assistant
        logging.info(f"Creating smart assistant for sessionid: {sessionid}")
        assistant = get_smart_assistant(mcp_client, goals_manager)
        
        # Process the query with intelligent data fetching
        logging.info(f"Processing query: {user_query}")
        result = await assistant.process_query(sessionid, user_query)
        logging.info(f"Query processing result: {result}")
    except Exception as e:
        logging.error(f"Error in AI assistant: {e}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        result = {
            "response": f"Error in AI processing: {str(e)}",
            "analysis": {"intent": "error"},
            "data_used": []
        }
    
    # Extract the response and metadata
    response_text = result.get("response", "I couldn't process your query. Please try again.")
    analysis = result.get("analysis", {})
    data_used = result.get("data_used", [])
    
    # Log the interaction for analytics
    background_tasks.add_task(
        log_ai_interaction,
        sessionid=sessionid,
        query=user_query,
        response=response_text,
        context_size=len(data_used)
    )
    
    return {
        "query": user_query,
        "response": response_text,
        "analysis": {
            "intent": analysis.get("intent", "unknown"),
            "data_sources_used": data_used,
            "time_period": analysis.get("time_period"),
            "specific_focus": analysis.get("specific_focus")
        },
        "performance": {
            "apis_called": len(data_used),
            "selective_fetching": True,
            "response_optimized": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/quick-insights")
async def quick_insights(request: Request):
    """
    Pre-defined quick insights for mobile - fast responses to common questions.
    """
    sessionid = request.cookies.get("sessionid")
    if not sessionid:
        raise HTTPException(status_code=401, detail="No session cookie found")
    
    # Build context once
    context = await prompt_builder.build_enhanced_context(
        sessionid, 
        mcp_client,
        goals_manager=goals_manager
    )
    
    insights = []
    
    # 1. Net Worth
    if 'net_worth' in context:
        net_worth_data = context['net_worth']
        if 'netWorthResponse' in net_worth_data:
            total = net_worth_data['netWorthResponse'].get('totalNetWorthValue', {})
            if total:
                value = int(total.get('units', '0'))
                insights.append({
                    "type": "net_worth",
                    "title": "Net Worth",
                    "value": f"₹{value:,}",
                    "icon": "💰"
                })
    
    # 2. Monthly Spending
    if 'spending_summary' in context:
        monthly_avg = context['spending_summary'].get('monthly_avg', 0)
        if monthly_avg > 0:
            insights.append({
                "type": "monthly_spend",
                "title": "Monthly Spending",
                "value": f"₹{int(monthly_avg):,}",
                "icon": "💳"
            })
    
    # 3. Next Payment
    if 'upcoming_payments' in context and context['upcoming_payments']:
        next_payment = context['upcoming_payments'][0]
        insights.append({
            "type": "next_payment",
            "title": "Next Payment",
            "value": f"{next_payment['category']} - ₹{int(next_payment['amount']):,}",
            "subtitle": f"Due: {next_payment['due']}",
            "icon": "📅"
        })
    
    # 4. Top Spending Category
    if 'spending_summary' in context:
        top_cats = context['spending_summary'].get('top_categories', [])
        if top_cats:
            top = top_cats[0]
            insights.append({
                "type": "top_category",
                "title": "Top Spending",
                "value": top['category'],
                "subtitle": f"{top['percentage']}% of spending",
                "icon": "📊"
            })
    
    # 5. Credit Score
    if 'credit_report' in context:
        credit_data = context['credit_report']
        if 'creditReportResponse' in credit_data:
            report = credit_data['creditReportResponse']
            if 'scoreInformation' in report:
                score = report['scoreInformation'].get('score')
                if score and score != 'N/A':
                    insights.append({
                        "type": "credit_score",
                        "title": "Credit Score",
                        "value": str(score),
                        "icon": "📈"
                    })
    
    # 6. Active Goals
    if 'goals' in context and context['goals']:
        closest_goal = max(context['goals'], key=lambda x: x.get('progress_percentage', 0))
        if closest_goal:
            insights.append({
                "type": "goal_progress",
                "title": closest_goal['name'],
                "value": f"{closest_goal['progress_percentage']}% complete",
                "subtitle": f"₹{int(closest_goal['current_amount']):,} of ₹{int(closest_goal['target_amount']):,}",
                "icon": "🎯"
            })
    
    return {
        "insights": insights,
        "quick_actions": [
            {"label": "What should I focus on?", "query": "What's my top financial priority right now?"},
            {"label": "Am I overspending?", "query": "Am I spending too much? Where can I cut back?"},
            {"label": "Investment advice", "query": "Should I increase my investments?"},
            {"label": "Debt strategy", "query": "How should I tackle my debt?"}
        ],
        "timestamp": datetime.now().isoformat()
    }

async def log_ai_interaction(sessionid: str, query: str, response: str, context_size: int):
    """Log AI interactions for analytics and improvement."""
    try:
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "sessionid": sessionid,
            "query": query,
            "response_length": len(response),
            "context_size": context_size
        }
        # In production, this would go to a database or analytics service
        print(f"AI Interaction logged: {log_data}")
    except Exception as e:
        print(f"Error logging AI interaction: {e}")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {config.APP_NAME}",
        "version": config.APP_VERSION,
        "demo_mode": config.DEBUG,
        "demo_session_id": "9999999999" if config.DEBUG else None,
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "ai": {
                "ask": "POST /api/ask",
                "ask_stream": "POST /stream/ask"
            },
            "data": {
                "nudges": "GET /api/nudges",
                "transactions": "GET /api/transactions",
                "net_worth": "GET /api/net_worth",
                "spend_daily": "GET /api/spend_daily?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD",
                "spend_monthly": "GET /api/spend_monthly?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD",
                "spend_by_category": "GET /api/spend_by_category?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD"
            },
            "goals": {
                "list": "GET /api/goals",
                "create": "POST /api/goals",
                "progress": "GET /api/goals/{goal_id}/progress"
            },
            "simulation": {
                "whatif": "POST /api/whatif"
            },
            "ai_assistant": {
                "ask": "POST /api/ask-ai - Your personal CFO (body: {\"query\": \"your question\"})",
                "quick_insights": "GET /api/quick-insights - Pre-computed insights for mobile"
            },
            "streaming": {
                "net_worth": "GET /stream/net_worth",
                "spend_daily": "GET /stream/spend_daily"
            }
        },
        "note": "Use sessionid cookie '9999999999' for demo data (login at MCP server first)" if config.DEBUG else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG
    )
