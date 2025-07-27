"""
FastAPI routes for the Finance AI Agent.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Response, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, date, timedelta
import json
import asyncio
import uuid
import httpx
import logging

from agent.runner import run_agent_with_context, run_agent_streaming
from mcp_client import mcp_client
from sse_starlette.sse import EventSourceResponse
from data_processor import TransactionProcessor
from goals_manager import goals_manager
from config import config
from datetime import datetime

router = APIRouter()

# Request/Response Models
class AskRequest(BaseModel):
    prompt: str = Field(..., description="The user's question or request")

class AskResponse(BaseModel):
    response: str = Field(..., description="The AI's response")

class GoalCreate(BaseModel):
    name: str = Field(..., description="Goal name")
    target_amount: Optional[float] = Field(None, description="Target amount to save (AI will estimate if not provided)")
    current_amount: float = Field(0, description="Current saved amount")
    target_date: Optional[datetime] = Field(None, description="Target date to achieve the goal")
    time_frame_months: Optional[int] = Field(None, description="Time frame in months to achieve the goal (alternative to target_date)")
    description: Optional[str] = Field(None, description="Goal description")
    category: Optional[str] = Field(None, description="Goal category (e.g., travel, gadgets, education)")

class GoalEstimateRequest(BaseModel):
    name: str = Field(..., description="Goal name")
    description: str = Field(..., description="Goal description")
    months_to_achieve: int = Field(..., description="Number of months to achieve the goal")
    category: Optional[str] = Field(None, description="Goal category (e.g., travel, gadgets, education)")

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    current_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    category: Optional[str] = None

class GoalProgress(BaseModel):
    goal_id: str
    name: str
    target_amount: float
    current_amount: float
    target_date: datetime
    progress_percentage: float
    monthly_required: float
    days_remaining: int
    on_track: bool

class LifestyleChangeRequest(BaseModel):
    change_type: str = Field(..., description="Type of lifestyle change")
    current_value: float = Field(..., description="Current spending/value")
    target_value: float = Field(..., description="Target spending/value")
    
class LifestyleRecommendation(BaseModel):
    id: str
    category: str
    description: str
    current_spending: float
    recommended_spending: float
    potential_savings: float
    difficulty: str  # easy, medium, hard
    impact: str  # low, medium, high

class WhatIfRequest(BaseModel):
    scenario: str = Field(..., description="Scenario type: mf_return or spend_reduction")
    amount: Optional[float] = Field(None, description="Investment amount for mf_return")
    horizon_months: Optional[int] = Field(12, description="Investment horizon in months")
    percent: Optional[float] = Field(None, description="Reduction percentage for spend_reduction")
    annual_rate: Optional[float] = Field(0.12, description="Annual return rate (default 12%)")

class TransactionCreate(BaseModel):
    amount: float = Field(..., description="Transaction amount")
    narration: str = Field(..., description="Transaction description")
    category: Optional[str] = Field(None, description="Transaction category")
    date: Optional[str] = Field(None, description="Transaction date (YYYY-MM-DD)")
    type: str = Field("expense", description="Transaction type: expense or income")

class LoginRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number for login")
    session_id: Optional[str] = Field(None, description="Optional session ID (will use phone number if not provided)")

class CelebrityComparisonRequest(BaseModel):
    celebrity_name: str = Field(..., description="Name of the celebrity to compare with")
    comparison_type: str = Field("all", description="Type of comparison: net_worth, income, investments, real_estate, all")

class CelebrityData(BaseModel):
    name: str
    net_worth: float
    monthly_income: float
    investments: float
    real_estate: float
    primary_income_sources: List[str]
    data_source: str
    last_updated: str

class UserFinancialData(BaseModel):
    net_worth: float
    monthly_income: float
    investments: float
    real_estate: float

class ComparisonInsights(BaseModel):
    net_worth_percentage: float
    income_percentage: float
    investment_percentage: float
    real_estate_percentage: float
    motivational_message: str
    achievement_insight: str
    next_milestone: str

class CelebrityComparisonResponse(BaseModel):
    user_data: UserFinancialData
    celebrity_data: CelebrityData
    comparison: ComparisonInsights
    generated_at: str

# Dependency to get session ID
async def get_sessionid(request: Request) -> str:
    """Extract session ID from cookie."""
    sessionid = request.cookies.get("sessionid")
    if not sessionid:
        raise HTTPException(status_code=401, detail="Login required - no sessionid cookie")
    return sessionid

# Login API
@router.post("/api/login")
async def login(request: LoginRequest, response: Response):
    """Login using phone number and get session cookie."""
    try:
        # Use phone number as session ID if not provided
        session_id = request.session_id or request.phone_number
        
        # Validate phone number format (basic validation)
        if not request.phone_number.isdigit() or len(request.phone_number) != 10:
            raise HTTPException(
                status_code=400, 
                detail="Invalid phone number format. Please provide a 10-digit phone number."
            )
        
        # Call MCP login endpoint
        mcp_login_url = f"{config.MCP_BASE_URL}/login"
        login_data = {
            "sessionId": session_id,
            "phoneNumber": request.phone_number
        }
        
        async with httpx.AsyncClient() as client:
            mcp_response = await client.post(
                mcp_login_url,
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10.0
            )
        
        # Check if MCP login was successful
        if mcp_response.status_code == 200:
            # Set session cookie
            response.set_cookie(
                key="sessionid",
                value=session_id,
                max_age=86400,  # 24 hours
                httponly=True,
                secure=True,  # Set to True in production with HTTPS
                samesite="lax"
            )
            
            return {
                "success": True,
                "message": "Login successful",
                "phone_number": request.phone_number,
                "session_id": session_id,
                "expires_in": 86400,
                "demo_note": "Session cookie set. Use this sessionid in subsequent API calls."
            }
        else:
            # MCP login failed
            raise HTTPException(
                status_code=401,
                detail=f"Login failed. MCP server returned status {mcp_response.status_code}. Please check your phone number and try again."
            )
            
    except httpx.RequestError as e:
        # Network error (MCP server not running)
        raise HTTPException(
            status_code=503,
            detail=f"Login service unavailable. MCP server is not running or not accessible. Error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed due to unexpected error: {str(e)}"
        )

# NEW ENDPOINTS

# Payment Nudges
@router.get("/api/nudges")
async def get_payment_nudges(sessionid: str = Depends(get_sessionid)):
    """Get upcoming payment nudges based on recurring transactions."""
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        nudges = TransactionProcessor.get_payment_nudges(bank_data)
        
        # Filter out deleted nudges
        deleted_nudges = get_deleted_nudges(sessionid)
        filtered_nudges = [
            nudge for nudge in nudges 
            if nudge.get('category', '').lower() not in deleted_nudges
        ]
        
        return filtered_nudges
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/nudges/{category}")
async def delete_payment_nudge(
    category: str,
    sessionid: str = Depends(get_sessionid)
):
    """Delete a specific payment nudge by category (e.g., 'Netflix', 'Rent', 'AMEX Card Payment')."""
    try:
        # Validate that the category exists in current nudges
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        current_nudges = TransactionProcessor.get_payment_nudges(bank_data)
        
        # Find the nudge by category (case-insensitive)
        nudge_to_delete = None
        for nudge in current_nudges:
            if nudge.get('category', '').lower() == category.lower():
                nudge_to_delete = nudge
                break
        
        if not nudge_to_delete:
            raise HTTPException(
                status_code=404, 
                detail=f"No nudge found for category '{category}'. Available categories: {[n.get('category') for n in current_nudges]}"
            )
        
        # Store the deleted nudge in memory
        add_deleted_nudge(sessionid, category)
        
        # Create a transaction to reflect the payment was made
        payment_transaction = {
            "amount": nudge_to_delete['amount'],
            "narration": f"Payment: {nudge_to_delete['category']} - {nudge_to_delete['merchant']}",
            "category": nudge_to_delete['category'],
            "date": datetime.now().strftime("%Y-%m-%d"),  # Today's date
            "type": "expense",
            "txn_type": "DEBIT"  # Add this for spending analysis compatibility
        }
        
        # Add the payment transaction to demo transactions
        add_demo_transaction(sessionid, payment_transaction)
        
        # Return success response with deleted nudge info and created transaction
        return {
            "success": True,
            "message": f"Payment for '{nudge_to_delete['category']}' has been processed and nudge removed",
            "deleted_nudge": nudge_to_delete,
            "created_transaction": payment_transaction,
            "demo_note": "Payment transaction created and nudge removed from preferences"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete nudge: {str(e)}")

# Unified Transactions List
@router.get("/api/transactions")
async def get_all_transactions(sessionid: str = Depends(get_sessionid)):
    """Get all transactions (bank + MF + stocks + demo) in a unified list."""
    try:
        # Fetch MCP data
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        mf_data = await mcp_client.get_mf_transactions(sessionid)
        stock_data = await mcp_client.get_stock_transactions(sessionid)
        
        # Merge MCP transactions
        transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
        
        # Add demo transactions (in-memory storage for hackathon)
        # In production, this would be a database
        demo_transactions = get_demo_transactions(sessionid)
        transactions.extend(demo_transactions)
        
        # Sort by date descending
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Transaction Summary API
@router.get("/api/transactions/summary")
async def get_transaction_summary(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    sessionid: str = Depends(get_sessionid)
):
    """Get transaction summary (expenses, income, balance) for a date range."""
    try:
        # Fetch all transactions
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        mf_data = await mcp_client.get_mf_transactions(sessionid)
        stock_data = await mcp_client.get_stock_transactions(sessionid)
        
        transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
        demo_transactions = get_demo_transactions(sessionid)
        transactions.extend(demo_transactions)
        
        # Filter transactions by date range
        filtered_transactions = [
            txn for txn in transactions 
            if from_date <= txn['date'] <= to_date
        ]
        
        # Calculate summary
        total_expenses = sum(
            txn['amount'] for txn in filtered_transactions 
            if txn.get('txn_type') == 'DEBIT' or txn.get('type') == 'expense'
        )
        
        total_income = sum(
            txn['amount'] for txn in filtered_transactions 
            if txn.get('txn_type') == 'CREDIT' or txn.get('type') == 'income'
        )
        
        balance = total_income - total_expenses
        
        # Get latest transaction date
        if filtered_transactions:
            latest_date = max(txn['date'] for txn in filtered_transactions)
        else:
            latest_date = datetime.now().strftime('%Y-%m-%d')
        
        return {
            "total_expenses": round(total_expenses, 2),
            "total_income": round(total_income, 2),
            "balance": round(balance, 2),
            "from_date": from_date,
            "to_date": to_date,
            "transaction_count": len(filtered_transactions),
            "currency": "INR",
            "last_updated": datetime.now().isoformat(),
            "latest_transaction_date": latest_date
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating summary: {str(e)}")

# In-memory storage for demo transactions
_demo_transactions = {}

# In-memory storage for deleted nudges
_deleted_nudges = {}

def get_demo_transactions(sessionid: str) -> List[Dict]:
    """Get demo transactions for a user."""
    return _demo_transactions.get(sessionid, [])

def add_demo_transaction(sessionid: str, transaction: Dict):
    """Add a demo transaction to in-memory storage."""
    if sessionid not in _demo_transactions:
        _demo_transactions[sessionid] = []
    _demo_transactions[sessionid].append(transaction)

def get_deleted_nudges(sessionid: str) -> Set[str]:
    """Get deleted nudges for a user."""
    return _deleted_nudges.get(sessionid, set())

def add_deleted_nudge(sessionid: str, category: str):
    """Add a deleted nudge to in-memory storage."""
    if sessionid not in _deleted_nudges:
        _deleted_nudges[sessionid] = set()
    _deleted_nudges[sessionid].add(category.lower())

# Spend Analysis - Daily
@router.get("/api/spend_daily")
async def get_daily_spend(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    sessionid: str = Depends(get_sessionid)
):
    """Get daily spending aggregates for a date range."""
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        
        # Add demo transactions
        demo_transactions = get_demo_transactions(sessionid)
        if demo_transactions:
            transactions.extend(demo_transactions)
        
        daily_spend = TransactionProcessor.calculate_daily_spend(transactions, from_date, to_date)
        return daily_spend
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Spend Analysis - Monthly
@router.get("/api/spend_monthly")
async def get_monthly_spend(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    sessionid: str = Depends(get_sessionid)
):
    """Get monthly spending aggregates for a date range."""
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        
        # Add demo transactions
        demo_transactions = get_demo_transactions(sessionid)
        if demo_transactions:
            transactions.extend(demo_transactions)
        
        monthly_spend = TransactionProcessor.calculate_monthly_spend(transactions, from_date, to_date)
        return monthly_spend
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Spend by Category
@router.get("/api/spend_by_category")
async def get_spend_by_category(
    from_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    sessionid: str = Depends(get_sessionid)
):
    """Get spending breakdown by category for a date range."""
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        
        # Add demo transactions
        demo_transactions = get_demo_transactions(sessionid)
        if demo_transactions:
            transactions.extend(demo_transactions)
        
        breakdown = TransactionProcessor.calculate_category_breakdown(transactions, from_date, to_date)
        return breakdown
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# What-If Simulator
@router.post("/api/whatif")
async def whatif_simulator(
    request: WhatIfRequest,
    sessionid: str = Depends(get_sessionid)
):
    """Run what-if financial simulations."""
    try:
        # If spend_reduction scenario, calculate average monthly spend
        if request.scenario == 'spend_reduction' and not hasattr(request, 'avg_monthly_spend'):
            # Get last 3 months of data
            bank_data = await mcp_client.get_bank_transactions(sessionid)
            transactions = TransactionProcessor.parse_bank_transactions(bank_data)
            
            # Calculate average monthly spend
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            monthly_data = TransactionProcessor.calculate_monthly_spend(
                transactions, 
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            avg_monthly_spend = sum(m['amount'] for m in monthly_data) / len(monthly_data) if monthly_data else 50000
            
            result = TransactionProcessor.whatif_simulator(
                request.scenario,
                percent=request.percent,
                avg_monthly_spend=avg_monthly_spend
            )
        else:
            result = TransactionProcessor.whatif_simulator(
                request.scenario,
                amount=request.amount,
                horizon_months=request.horizon_months,
                annual_rate=request.annual_rate,
                percent=request.percent
            )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Add Transaction (Enhanced for Hackathon Demo)
@router.post("/api/transactions")
async def add_transaction(
    transaction: TransactionCreate,
    sessionid: str = Depends(get_sessionid)
):
    """Add a new transaction to the user's financial records."""
    try:
        # Validate transaction data
        if transaction.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        if not transaction.narration or len(transaction.narration.strip()) == 0:
            raise HTTPException(status_code=400, detail="Transaction description is required")
        
        # Auto-categorize if not provided
        if not transaction.category:
            transaction.category = TransactionProcessor.categorize_transaction(transaction.narration)
        
        # Handle date from date picker - convert various formats to YYYY-MM-DD
        if transaction.date:
            try:
                # Handle ISO string format (e.g., "2024-07-15T00:00:00.000Z")
                if 'T' in transaction.date:
                    transaction.date = transaction.date.split('T')[0]
                # Handle timestamp format
                elif transaction.date.isdigit() and len(transaction.date) > 8:
                    timestamp = int(transaction.date)
                    if len(transaction.date) == 13:  # milliseconds
                        timestamp = timestamp / 1000
                    transaction.date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                # Handle DD/MM/YYYY format
                elif '/' in transaction.date and len(transaction.date.split('/')) == 3:
                    parts = transaction.date.split('/')
                    if len(parts[0]) == 2 and len(parts[1]) == 2:  # DD/MM/YYYY
                        transaction.date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elif len(parts[0]) == 2 and len(parts[1]) == 2:  # MM/DD/YYYY
                        transaction.date = f"{parts[2]}-{parts[0]}-{parts[1]}"
                # Handle empty string or invalid date
                elif not transaction.date.strip():
                    transaction.date = datetime.now().strftime('%Y-%m-%d')
            except Exception as e:
                print(f"⚠️  Date conversion error: {e}, using today's date")
                transaction.date = datetime.now().strftime('%Y-%m-%d')
        else:
            # Set default date to today if not provided
            transaction.date = datetime.now().strftime('%Y-%m-%d')
        
        # Create transaction object
        new_transaction = {
        "id": str(uuid.uuid4()),
        "user_id": sessionid,
        "amount": transaction.amount,
            "narration": transaction.narration.strip(),
            "category": transaction.category,
            "date": transaction.date,
        "type": transaction.type,
            "txn_type": "DEBIT" if transaction.type == "expense" else "CREDIT",
            "merchant": transaction.narration.split()[0] if transaction.narration else "Unknown",
        "created_at": datetime.now().isoformat(),
            "status": "completed",
            "source": "demo"  # Mark as demo transaction
        }
        
        # Store in demo storage (in-memory for hackathon)
        add_demo_transaction(sessionid, new_transaction)
        
        # Log the transaction for demo purposes
        print(f"Demo transaction created: {new_transaction}")
        
        return {
            "success": True,
            "transaction": new_transaction,
            "message": "Transaction recorded successfully",
            "demo_note": "Transaction added to demo storage and will appear in GET /api/transactions"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating transaction: {str(e)}")

# Update Transaction
@router.put("/api/transactions/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionCreate,
    sessionid: str = Depends(get_sessionid)
):
    """Update an existing transaction."""
    try:
        # Validate transaction data
        if transaction_update.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")
        
        if not transaction_update.narration or len(transaction_update.narration.strip()) == 0:
            raise HTTPException(status_code=400, detail="Transaction description is required")
        
        # Auto-categorize if not provided
        if not transaction_update.category:
            transaction_update.category = TransactionProcessor.categorize_transaction(transaction_update.narration)
        
        # Handle date from date picker - convert various formats to YYYY-MM-DD
        if transaction_update.date:
            try:
                # Handle ISO string format (e.g., "2024-07-15T00:00:00.000Z")
                if 'T' in transaction_update.date:
                    transaction_update.date = transaction_update.date.split('T')[0]
                # Handle timestamp format
                elif transaction_update.date.isdigit() and len(transaction_update.date) > 8:
                    timestamp = int(transaction_update.date)
                    if len(transaction_update.date) == 13:  # milliseconds
                        timestamp = timestamp / 1000
                    transaction_update.date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                # Handle DD/MM/YYYY format
                elif '/' in transaction_update.date and len(transaction_update.date.split('/')) == 3:
                    parts = transaction_update.date.split('/')
                    if len(parts[0]) == 2 and len(parts[1]) == 2:  # DD/MM/YYYY
                        transaction_update.date = f"{parts[2]}-{parts[1]}-{parts[0]}"
                    elif len(parts[0]) == 2 and len(parts[1]) == 2:  # MM/DD/YYYY
                        transaction_update.date = f"{parts[2]}-{parts[0]}-{parts[1]}"
                # Handle empty string or invalid date
                elif not transaction_update.date.strip():
                    transaction_update.date = datetime.now().strftime('%Y-%m-%d')
            except Exception as e:
                print(f"⚠️  Date conversion error: {e}, using today's date")
                transaction_update.date = datetime.now().strftime('%Y-%m-%d')
        else:
            # Set default date to today if not provided
            transaction_update.date = datetime.now().strftime('%Y-%m-%d')
        
        # Create updated transaction object
        updated_transaction = {
            "id": transaction_id,
            "user_id": sessionid,
            "amount": transaction_update.amount,
            "narration": transaction_update.narration.strip(),
            "category": transaction_update.category,
            "date": transaction_update.date,
            "type": transaction_update.type,
            "txn_type": "DEBIT" if transaction_update.type == "expense" else "CREDIT",
            "merchant": transaction_update.narration.split()[0] if transaction_update.narration else "Unknown",
            "updated_at": datetime.now().isoformat(),
            "status": "updated",
            "source": "demo"
        }
        
        # Update in demo storage
        demo_transactions = get_demo_transactions(sessionid)
        for i, txn in enumerate(demo_transactions):
            if txn['id'] == transaction_id:
                demo_transactions[i] = updated_transaction
                break
        
        print(f"Demo transaction updated: {updated_transaction}")
        
        return {
            "success": True,
            "transaction": updated_transaction,
            "message": "Transaction updated successfully",
            "demo_note": "Transaction updated in demo storage"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating transaction: {str(e)}")

# Delete Transaction
@router.delete("/api/transactions/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    sessionid: str = Depends(get_sessionid)
):
    """Delete a transaction."""
    try:
        # Remove from demo storage
        demo_transactions = get_demo_transactions(sessionid)
        demo_transactions[:] = [txn for txn in demo_transactions if txn['id'] != transaction_id]
        
        print(f"Demo transaction deleted: {transaction_id} for user {sessionid}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "message": "Transaction deleted successfully",
            "demo_note": "Transaction removed from demo storage"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting transaction: {str(e)}")

# Get Single Transaction
@router.get("/api/transactions/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    sessionid: str = Depends(get_sessionid)
):
    """Get a specific transaction by ID."""
    try:
        # In a real implementation, this would fetch from database/MCP server
        # For demo, return a mock transaction
        mock_transaction = {
            "id": transaction_id,
            "user_id": sessionid,
            "amount": 1000.0,
            "narration": "Demo Transaction",
            "category": "Shopping",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "type": "expense",
            "txn_type": "DEBIT",
            "merchant": "Demo",
            "created_at": datetime.now().isoformat(),
            "status": "completed"
    }
        
        return {
            "success": True,
            "transaction": mock_transaction,
            "demo_note": "In production, this would fetch the actual transaction from your records"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching transaction: {str(e)}")

# SSE Streaming for spend data
@router.get("/stream/spend_daily")
async def stream_daily_spend(sessionid: str = Depends(get_sessionid)):
    """Stream daily spend updates via SSE."""
    async def generate():
        while True:
            try:
                # Get current date
                today = datetime.now().strftime('%Y-%m-%d')
                week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
                
                # Fetch latest data
                bank_data = await mcp_client.get_bank_transactions(sessionid)
                transactions = TransactionProcessor.parse_bank_transactions(bank_data)
                daily_spend = TransactionProcessor.calculate_daily_spend(transactions, week_ago, today)
                
                yield {"data": json.dumps({"daily_spend": daily_spend, "timestamp": datetime.now().isoformat()})}
                
                # Wait 30 seconds before next update
                await asyncio.sleep(30)
            except Exception as e:
                yield {"data": json.dumps({"error": str(e)})}
                break
    
    return EventSourceResponse(generate())

# EXISTING ENDPOINTS (keeping them as is)

# AI Agent Endpoints
@router.post("/api/ask", response_model=AskResponse)
async def ask_endpoint(request: AskRequest, sessionid: str = Depends(get_sessionid)):
    """
    Ask the AI agent a question about your finances.
    The agent has access to all your financial data.
    """
    try:
        # Use the optimized SmartFinanceAssistant instead of the old runner
        from agent.ai_assistant import get_smart_assistant
        assistant = get_smart_assistant(mcp_client, goals_manager)
        
        # Process the query with intelligent data fetching
        result = await assistant.process_query(sessionid, request.prompt)
        
        # Extract the response
        response_text = result.get("response", "I couldn't process your query. Please try again.")
        
        return AskResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI error: {str(e)}")

@router.post("/stream/ask")
async def ask_stream_endpoint(request: AskRequest, sessionid: str = Depends(get_sessionid)):
    """
    Ask the AI agent a question with streaming response (SSE).
    """
    async def generate():
        try:
            # Use the optimized SmartFinanceAssistant
            from agent.ai_assistant import get_smart_assistant
            assistant = get_smart_assistant(mcp_client, goals_manager)
            
            # Process the query with intelligent data fetching
            result = await assistant.process_query(sessionid, request.prompt)
            
            # Stream the response
            response_text = result.get("response", "I couldn't process your query. Please try again.")
            
            # Split response into chunks for streaming
            words = response_text.split()
            chunk_size = 5  # Send 5 words at a time
            
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i + chunk_size])
                yield {"data": chunk}
                
        except Exception as e:
            yield {"data": f"Error: {str(e)}"}
    
    return EventSourceResponse(generate())

# MCP Data Endpoints (REST)
@router.get("/api/net_worth")
async def get_net_worth(sessionid: str = Depends(get_sessionid)):
    """Get user's net worth data."""
    return await mcp_client.get_net_worth(sessionid)

@router.get("/api/credit_report")
async def get_credit_report(sessionid: str = Depends(get_sessionid)):
    """Get user's credit report."""
    return await mcp_client.get_credit_report(sessionid)

@router.get("/api/epf_details")
async def get_epf_details(sessionid: str = Depends(get_sessionid)):
    """Get user's EPF details."""
    return await mcp_client.get_epf_details(sessionid)

@router.get("/api/mf_transactions")
async def get_mf_transactions(sessionid: str = Depends(get_sessionid)):
    """Get user's mutual fund transactions."""
    return await mcp_client.get_mf_transactions(sessionid)

@router.get("/api/bank_transactions")
async def get_bank_transactions(sessionid: str = Depends(get_sessionid)):
    """Get user's bank transactions."""
    return await mcp_client.get_bank_transactions(sessionid)

@router.get("/api/stock_transactions")
async def get_stock_transactions(sessionid: str = Depends(get_sessionid)):
    """Get user's stock transactions."""
    return await mcp_client.get_stock_transactions(sessionid)

# MCP Data Endpoints (SSE Streaming)
@router.get("/stream/net_worth")
async def stream_net_worth(sessionid: str = Depends(get_sessionid)):
    """Stream net worth data via SSE."""
    async def generate():
        async for data in mcp_client.stream_net_worth(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

@router.get("/stream/credit_report")
async def stream_credit_report(sessionid: str = Depends(get_sessionid)):
    """Stream credit report via SSE."""
    async def generate():
        async for data in mcp_client.stream_credit_report(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

@router.get("/stream/epf_details")
async def stream_epf_details(sessionid: str = Depends(get_sessionid)):
    """Stream EPF details via SSE."""
    async def generate():
        async for data in mcp_client.stream_epf_details(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

@router.get("/stream/mf_transactions")
async def stream_mf_transactions(sessionid: str = Depends(get_sessionid)):
    """Stream mutual fund transactions via SSE."""
    async def generate():
        async for data in mcp_client.stream_mf_transactions(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

@router.get("/stream/bank_transactions")
async def stream_bank_transactions(sessionid: str = Depends(get_sessionid)):
    """Stream bank transactions via SSE."""
    async def generate():
        async for data in mcp_client.stream_bank_transactions(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

@router.get("/stream/stock_transactions")
async def stream_stock_transactions(sessionid: str = Depends(get_sessionid)):
    """Stream stock transactions via SSE."""
    async def generate():
        async for data in mcp_client.stream_stock_transactions(sessionid):
            yield {"data": json.dumps(data)}
    
    return EventSourceResponse(generate())

# Goal Management Endpoints (Using JSON file storage)
@router.get("/api/goals")
async def list_goals(sessionid: str = Depends(get_sessionid)):
    """List all goals for the user with progress calculations."""
    try:
        goals = goals_manager.list_goals(sessionid)
        
        # Handle both list and dict responses from goals_manager
        goals_list = goals if isinstance(goals, list) else goals.get('goals', [])
        
        # Enhance goals with progress calculations for UI
        enhanced_goals = []
        for goal in goals_list:
            progress = goals_manager.calculate_goal_progress(goal)
            
            # Calculate remaining months
            target_date = datetime.fromisoformat(goal['target_date'])
            remaining_days = (target_date - datetime.now()).days
            remaining_months = max(1, remaining_days // 30)
            
            # Calculate monthly needed
            remaining_amount = goal['target_amount'] - goal['current_amount']
            monthly_needed = remaining_amount / remaining_months if remaining_months > 0 else 0
            
            enhanced_goal = {
                **goal,
                "progress_percentage": progress['progress_percentage'],
                "monthly_needed": round(monthly_needed, 2),
                "remaining_months": remaining_months,
                "remaining_amount": remaining_amount,
                "on_track": progress['on_track']
            }
            enhanced_goals.append(enhanced_goal)
        
        # Return individual goal objects (same structure as POST response) with summary data
        return {
            "goals": enhanced_goals,
            "summary": {
                "total_goals": len(enhanced_goals),
                "total_target": sum(g['target_amount'] for g in enhanced_goals),
                "total_saved": sum(g['current_amount'] for g in enhanced_goals),
                "overall_progress": round((sum(g['current_amount'] for g in enhanced_goals) / sum(g['target_amount'] for g in enhanced_goals)) * 100, 1) if enhanced_goals else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch goals: {str(e)}")

def generate_goal_insights(goal_name: str, category: str, target_amount: float, months_to_achieve: int, 
                          monthly_income: float, monthly_expenses: float, monthly_savings: float, savings_rate: float) -> dict:
    """Generate Finion Insights for goal achievement."""
    monthly_needed = target_amount / months_to_achieve
    current_savings_ratio = monthly_savings / monthly_needed if monthly_needed > 0 else 0
    
    insights = {
        "savings_strategy": [],
        "lifestyle_recommendations": [],
        "investment_opportunities": [],
        "risk_assessment": "",
        "success_probability": ""
    }
    
    # Savings Strategy
    if current_savings_ratio >= 1.2:
        insights["savings_strategy"].append("🎯 You're already saving enough! Maintain your current savings rate.")
        insights["success_probability"] = "Very High (95%)"
    elif current_savings_ratio >= 0.8:
        insights["savings_strategy"].append("📈 Increase savings by 20-30% to comfortably achieve this goal.")
        insights["success_probability"] = "High (80%)"
    elif current_savings_ratio >= 0.5:
        insights["savings_strategy"].append("💪 You'll need to double your savings rate. Consider cutting non-essential expenses.")
        insights["success_probability"] = "Moderate (60%)"
    else:
        insights["savings_strategy"].append("🚨 Significant lifestyle changes needed. Consider extending timeline or reducing goal amount.")
        insights["success_probability"] = "Low (30%)"
    
    # Category-specific insights
    if category == "travel":
        insights["savings_strategy"].append("✈️ Book flights 6-8 months in advance for better prices")
        insights["lifestyle_recommendations"].append("🏠 Consider home-sharing or budget accommodations")
        insights["lifestyle_recommendations"].append("🍽️ Plan meals to avoid expensive tourist restaurants")
    elif category == "gadgets":
        insights["savings_strategy"].append("📱 Wait for festive sales or exchange offers")
        insights["lifestyle_recommendations"].append("💳 Consider EMI options if available at 0% interest")
        insights["investment_opportunities"].append("📊 Invest in tech stocks to potentially offset gadget costs")
    elif category == "emergency":
        insights["savings_strategy"].append("🛡️ Prioritize this goal - emergency funds are crucial")
        insights["lifestyle_recommendations"].append("💰 Keep emergency fund in high-yield savings account")
        insights["investment_opportunities"].append("📈 Consider liquid funds for better returns than savings account")
    elif category == "education":
        insights["savings_strategy"].append("🎓 Look for scholarships, employer reimbursement programs")
        insights["lifestyle_recommendations"].append("📚 Consider online courses as cost-effective alternatives")
        insights["investment_opportunities"].append("📊 Education-focused mutual funds can help grow your savings")
    
    # General financial insights
    if savings_rate < 15:
        insights["lifestyle_recommendations"].append("📊 Track your expenses to identify saving opportunities")
        insights["lifestyle_recommendations"].append("🏠 Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings")
    
    if monthly_expenses > monthly_income * 0.7:
        insights["lifestyle_recommendations"].append("⚠️ Your expenses are high relative to income. Review discretionary spending")
    
    # Investment opportunities based on timeline
    if months_to_achieve >= 12:
        insights["investment_opportunities"].append("📈 Consider SIP in mutual funds for better returns than savings")
        insights["investment_opportunities"].append("🏦 Fixed deposits can provide guaranteed returns")
    elif months_to_achieve >= 6:
        insights["investment_opportunities"].append("💰 High-yield savings accounts or liquid funds")
    else:
        insights["investment_opportunities"].append("💳 Keep in savings account for immediate access")
    
    # Risk assessment
    if current_savings_ratio < 0.5:
        insights["risk_assessment"] = "High - Goal may be unrealistic with current savings rate"
    elif current_savings_ratio < 0.8:
        insights["risk_assessment"] = "Moderate - Requires significant lifestyle changes"
    else:
        insights["risk_assessment"] = "Low - Goal is achievable with current or slightly improved savings"
    
    return insights

@router.post("/api/goals")
async def create_goal(
    goal: GoalCreate,
    sessionid: str = Depends(get_sessionid)
):
    """Create a new financial goal with AI-powered target amount estimation."""
    try:
        # Calculate target date and months to achieve goal
        if goal.target_date:
            target_date = goal.target_date
            months_to_achieve = max(1, (target_date - datetime.now()).days // 30)
        elif goal.time_frame_months:
            # Calculate target date from time frame
            target_date = datetime.now() + timedelta(days=goal.time_frame_months * 30)
            months_to_achieve = goal.time_frame_months
        else:
            raise HTTPException(status_code=400, detail="Either target_date or time_frame_months must be provided")
        
        # If target_amount is not provided, use AI to estimate it
        target_amount = goal.target_amount
        category_reasoning = ""
        financial_reasoning = ""
        finion_insights = {}
        
        if target_amount is None:
            
            # Use the goals estimate logic to get AI-powered target amount
            # datetime is already imported at the top
            
            # Fetch user's financial data for AI analysis
            bank_data = await mcp_client.get_bank_transactions(sessionid)
            mf_data = await mcp_client.get_mf_transactions(sessionid)
            stock_data = await mcp_client.get_stock_transactions(sessionid)
            
            # Get demo transactions
            demo_transactions = get_demo_transactions(sessionid)
            
            # Merge all transactions
            all_transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
            if demo_transactions:
                all_transactions.extend(demo_transactions)
            
            # Calculate user's financial profile
            now = datetime.now()
            current_month_start = datetime(now.year, now.month, 1)
            
            # For demo purposes, use 2024 data
            if now.year > 2024:
                current_month_start = datetime(2024, 7, 1)
                current_month_end = datetime(2024, 7, 31)
            else:
                current_month_end = now
            
            # Filter current month transactions
            current_month_txns = [t for t in all_transactions if 
                                 current_month_start <= datetime.strptime(t['date'], '%Y-%m-%d') <= current_month_end]
            
            # Calculate income and expenses
            monthly_income = sum(t.get('amount', 0) for t in current_month_txns if t.get('txn_type') == 'CREDIT')
            monthly_expenses = sum(t.get('amount', 0) for t in current_month_txns if t.get('txn_type') == 'DEBIT')
            monthly_savings = monthly_income - monthly_expenses
            savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
            
            # AI-based goal estimation logic with detailed reasoning
            goal_name_lower = goal.name.lower()
            description_lower = (goal.description or "").lower()
            
            # Base estimation based on goal category and description
            base_amount = 0
            
            # Travel-related goals
            if any(word in goal_name_lower or word in description_lower for word in ['trip', 'travel', 'vacation', 'tour', 'europe', 'abroad']):
                if 'europe' in description_lower or 'europe' in goal_name_lower:
                    base_amount = 250000  # Europe trip
                    category_reasoning = "Europe trips typically cost ₹2.5L including flights, accommodation, food, and activities"
                elif 'international' in description_lower or 'abroad' in description_lower:
                    base_amount = 150000  # International travel
                    category_reasoning = "International travel costs around ₹1.5L for flights, hotels, and expenses"
                else:
                    base_amount = 80000   # Domestic travel
                    category_reasoning = "Domestic travel costs around ₹80K for flights, hotels, and activities"
            
            # Gadget-related goals
            elif any(word in goal_name_lower or word in description_lower for word in ['iphone', 'phone', 'laptop', 'gadget', 'device']):
                if 'iphone' in goal_name_lower or 'iphone' in description_lower:
                    base_amount = 120000  # iPhone
                    category_reasoning = "Latest iPhone models cost around ₹1.2L including taxes and accessories"
                elif 'laptop' in goal_name_lower or 'laptop' in description_lower:
                    base_amount = 80000   # Laptop
                    category_reasoning = "Good laptops cost around ₹80K for work and productivity"
                else:
                    base_amount = 50000   # Other gadgets
                    category_reasoning = "Other gadgets typically cost around ₹50K"
            
            # Education-related goals
            elif any(word in goal_name_lower or word in description_lower for word in ['course', 'education', 'study', 'certification']):
                base_amount = 100000  # Education
                category_reasoning = "Professional courses and certifications cost around ₹1L including materials"
            
            # Emergency fund
            elif any(word in goal_name_lower or word in description_lower for word in ['emergency', 'safety', 'backup']):
                base_amount = monthly_expenses * 6  # 6 months of expenses
                category_reasoning = f"Emergency fund should cover 6 months of expenses (₹{monthly_expenses:,.0f} × 6 = ₹{base_amount:,.0f})"
            
            # Home-related goals
            elif any(word in goal_name_lower or word in description_lower for word in ['home', 'house', 'property', 'down payment']):
                base_amount = 500000  # Down payment
                category_reasoning = "Home down payment typically requires ₹5L+ depending on property value"
            
            # Default estimation based on income
            else:
                base_amount = monthly_income * 3  # 3 months of income
                category_reasoning = f"General goal estimation based on 3 months of income (₹{monthly_income:,.0f} × 3)"
            
            # Adjust based on user's financial capacity
            if monthly_income > 0:
                # If user has high savings rate, they can afford more expensive goals
                if savings_rate > 30:
                    affordability_multiplier = 1.5
                    financial_reasoning = f"Your excellent savings rate of {savings_rate:.1f}% allows for more ambitious goals"
                elif savings_rate > 20:
                    affordability_multiplier = 1.2
                    financial_reasoning = f"Your good savings rate of {savings_rate:.1f}% supports this goal well"
                elif savings_rate > 10:
                    affordability_multiplier = 1.0
                    financial_reasoning = f"Your moderate savings rate of {savings_rate:.1f}% is suitable for this goal"
                else:
                    affordability_multiplier = 0.8
                    financial_reasoning = f"Your current savings rate of {savings_rate:.1f}% suggests a more conservative approach"
                
                adjusted_amount = base_amount * affordability_multiplier
                
                # Ensure the goal is achievable within the time frame
                max_monthly_savings = monthly_savings * 0.8  # Use 80% of current savings
                max_achievable = max_monthly_savings * months_to_achieve
                
                if adjusted_amount > max_achievable:
                    adjusted_amount = max_achievable
                    financial_reasoning += f" (adjusted to ₹{adjusted_amount:,.0f} based on achievable monthly savings)"
                
                target_amount = round(adjusted_amount, -3)  # Round to nearest thousand
            else:
                target_amount = base_amount
                financial_reasoning = "Using standard estimation as income data is limited"
            
            # Generate Finion Insights for goal achievement
            finion_insights = generate_goal_insights(
                goal_name=goal.name,
                category=goal.category,
                target_amount=target_amount,
                months_to_achieve=months_to_achieve,
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                monthly_savings=monthly_savings,
                savings_rate=savings_rate
            )
        
        goal_data = {
            'name': goal.name,
            'target_amount': target_amount,
            'current_amount': goal.current_amount,
            'target_date': target_date.isoformat(),
            'description': goal.description,
            'category': goal.category
        }
        
        # Add AI estimation info to goal_data if target_amount was estimated
        if goal.target_amount is None:
            goal_data.update({
                'ai_estimated': True,
                'estimation_reasoning': f"AI estimated ₹{target_amount:,} based on your financial profile and goal type",
                'detailed_reasoning': {
                    'category_basis': category_reasoning,
                    'financial_analysis': financial_reasoning,
                    'monthly_savings_needed': round(target_amount / months_to_achieve, 2),
                    'achievement_difficulty': 'Easy' if target_amount / months_to_achieve <= monthly_savings * 0.5 else 'Moderate' if target_amount / months_to_achieve <= monthly_savings else 'Challenging'
                },
                'finion_insights': finion_insights
            })
        
        created_goal = goals_manager.create_goal(sessionid, goal_data)
        
        # Add progress calculations to match GET response structure
        progress = goals_manager.calculate_goal_progress(created_goal)
        target_date = datetime.fromisoformat(created_goal['target_date'])
        remaining_days = (target_date - datetime.now()).days
        remaining_months = max(1, remaining_days // 30)
        remaining_amount = created_goal['target_amount'] - created_goal['current_amount']
        monthly_needed = remaining_amount / remaining_months if remaining_months > 0 else 0
        
        # Add progress fields to response
        created_goal.update({
            "progress_percentage": progress['progress_percentage'],
            "monthly_needed": round(monthly_needed, 2),
            "remaining_months": remaining_months,
            "remaining_amount": remaining_amount,
            "on_track": progress['on_track']
        })
        
        return created_goal
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create goal: {str(e)}")

@router.get("/api/goals/{goal_id}")
async def get_goal(
    goal_id: str,
    sessionid: str = Depends(get_sessionid)
):
    """Get a specific goal by ID."""
    goal = goals_manager.get_goal(sessionid, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.put("/api/goals/{goal_id}")
async def update_goal(
    goal_id: str,
    goal_update: GoalUpdate,
    sessionid: str = Depends(get_sessionid)
):
    """Update a goal's details."""
    updates = goal_update.dict(exclude_unset=True)
    if 'target_date' in updates and updates['target_date']:
        updates['target_date'] = updates['target_date'].isoformat()
    
    goal = goals_manager.update_goal(sessionid, goal_id, updates)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@router.delete("/api/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    sessionid: str = Depends(get_sessionid)
):
    """Delete a goal."""
    if not goals_manager.delete_goal(sessionid, goal_id):
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"message": "Goal deleted successfully"}

@router.get("/api/goals/{goal_id}/progress")
async def get_goal_progress(
    goal_id: str,
    sessionid: str = Depends(get_sessionid)
):
    """Calculate current progress and monthly savings needed for a goal."""
    goal = goals_manager.get_goal(sessionid, goal_id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return goals_manager.calculate_goal_progress(goal)

# Lifestyle Recommendations Endpoints
@router.get("/api/lifestyle-changes", response_model=List[LifestyleRecommendation])
async def get_lifestyle_recommendations(sessionid: str = Depends(get_sessionid)):
    """
    Get personalized lifestyle change recommendations based on spending patterns.
    """
    # Fetch user's transaction data
    bank_data = await mcp_client.get_bank_transactions(sessionid)
    
    # TODO: Analyze transactions and generate recommendations
    # For now, return mock recommendations
    recommendations = [
        LifestyleRecommendation(
            id="1",
            category="Dining Out",
            description="Reduce restaurant visits from 12 to 8 times per month",
            current_spending=1200.0,
            recommended_spending=800.0,
            potential_savings=400.0,
            difficulty="medium",
            impact="high"
        ),
        LifestyleRecommendation(
            id="2",
            category="Subscriptions",
            description="Cancel unused streaming services and gym membership",
            current_spending=150.0,
            recommended_spending=50.0,
            potential_savings=100.0,
            difficulty="easy",
            impact="medium"
        ),
        LifestyleRecommendation(
            id="3",
            category="Transportation",
            description="Use public transport 3 days a week instead of driving",
            current_spending=400.0,
            recommended_spending=250.0,
            potential_savings=150.0,
            difficulty="medium",
            impact="medium"
        )
    ]
    
    return recommendations

@router.post("/api/lifestyle-changes/apply")
async def apply_lifestyle_change(
    change: LifestyleChangeRequest,
    sessionid: str = Depends(get_sessionid)
):
    """
    Apply a lifestyle change and track it (mock - stored in memory only).
    """
    # In a real implementation, this would be persisted
    # For now, just return success
    monthly_savings = change.current_value - change.target_value
    annual_savings = monthly_savings * 12
    
    return {
        "message": "Lifestyle change applied successfully",
        "change_id": str(uuid.uuid4()),
        "projected_monthly_savings": monthly_savings,
        "projected_annual_savings": annual_savings
    } 

def convert_to_csv(export_data: Dict[str, Any]) -> str:
    """Convert export data to CSV format."""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write export info
    writer.writerow(["EXPORT INFO"])
    writer.writerow(["User ID", export_data["export_info"]["user_id"]])
    writer.writerow(["Export Date", export_data["export_info"]["export_date"]])
    writer.writerow(["Format", export_data["export_info"]["format"]])
    writer.writerow(["Version", export_data["export_info"]["version"]])
    writer.writerow([])
    
    # Write financial summaries
    if "financial_summaries" in export_data:
        writer.writerow(["FINANCIAL SUMMARIES"])
        writer.writerow(["Period", "Total Expenses", "Total Income", "Balance", "Transaction Count"])
        
        for period, summary in export_data["financial_summaries"].items():
            writer.writerow([
                period.replace("_", " ").title(),
                f"₹{summary['total_expenses']:,.2f}",
                f"₹{summary['total_income']:,.2f}",
                f"₹{summary['balance']:,.2f}",
                summary['transaction_count']
            ])
        writer.writerow([])
    
    # Write transactions
    if "unified_transactions" in export_data:
        transactions = export_data["unified_transactions"]["transactions"]
        if transactions:
            writer.writerow(["TRANSACTIONS"])
            writer.writerow(["Date", "Amount", "Narration", "Category", "Type", "Source", "Balance"])
            
            for txn in transactions:
                writer.writerow([
                    txn.get('date', ''),
                    f"₹{txn.get('amount', 0):,.2f}",
                    txn.get('narration', '')[:50],  # Truncate long descriptions
                    txn.get('category', ''),
                    txn.get('txn_type', ''),
                    txn.get('source', ''),
                    f"₹{txn.get('balance', 0):,.2f}" if txn.get('balance') else ''
                ])
            writer.writerow([])
    
    # Write goals
    if "financial_goals" in export_data and export_data["financial_goals"]["goals"]:
        writer.writerow(["FINANCIAL GOALS"])
        writer.writerow(["Name", "Target Amount", "Current Amount", "Progress %", "Days Remaining", "On Track"])
        
        for goal_data in export_data["financial_goals"]["goals"]:
            goal = goal_data["goal"]
            progress = goal_data["progress"]
            writer.writerow([
                goal.get('name', ''),
                f"₹{goal.get('target_amount', 0):,.2f}",
                f"₹{goal.get('current_amount', 0):,.2f}",
                f"{progress.get('progress_percentage', 0):.1f}%",
                progress.get('days_remaining', 0),
                "Yes" if progress.get('on_track', False) else "No"
            ])
        writer.writerow([])
    
    # Write data insights
    if "data_insights" in export_data:
        insights = export_data["data_insights"]
        writer.writerow(["DATA INSIGHTS"])
        writer.writerow(["Total Transactions", insights.get("total_transactions", 0)])
        writer.writerow(["Earliest Transaction", insights.get("date_range", {}).get("earliest_transaction", "N/A")])
        writer.writerow(["Latest Transaction", insights.get("date_range", {}).get("latest_transaction", "N/A")])
        writer.writerow(["Data Sources", ", ".join(insights.get("data_sources", []))])
        writer.writerow(["Export Complete", "Yes" if insights.get("export_complete", False) else "No"])
    
    return output.getvalue()

# AI Goal Estimation API
@router.post("/api/goals/estimate")
async def estimate_goal_amount(
    request: GoalEstimateRequest,
    sessionid: str = Depends(get_sessionid)
):
    """AI-powered goal amount estimation based on user's financial data."""
    try:
        from datetime import datetime, timedelta
        
        # Fetch user's financial data for AI analysis
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        mf_data = await mcp_client.get_mf_transactions(sessionid)
        stock_data = await mcp_client.get_stock_transactions(sessionid)
        
        # Get demo transactions
        demo_transactions = get_demo_transactions(sessionid)
        
        # Merge all transactions
        all_transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
        if demo_transactions:
            all_transactions.extend(demo_transactions)
        
        # Calculate user's financial profile
        now = datetime.now()
        current_month_start = datetime(now.year, now.month, 1)
        
        # For demo purposes, use 2024 data
        if now.year > 2024:
            current_month_start = datetime(2024, 7, 1)
            current_month_end = datetime(2024, 7, 31)
        else:
            current_month_end = now
        
        # Filter current month transactions
        current_month_txns = [t for t in all_transactions if 
                             current_month_start <= datetime.strptime(t['date'], '%Y-%m-%d') <= current_month_end]
        
        # Calculate income and expenses
        monthly_income = sum(t.get('amount', 0) for t in current_month_txns if t.get('txn_type') == 'CREDIT')
        monthly_expenses = sum(t.get('amount', 0) for t in current_month_txns if t.get('txn_type') == 'DEBIT')
        monthly_savings = monthly_income - monthly_expenses
        savings_rate = (monthly_savings / monthly_income * 100) if monthly_income > 0 else 0
        
        # AI-based goal estimation logic
        goal_name_lower = request.name.lower()
        description_lower = request.description.lower()
        
        # Base estimation based on goal category and description
        base_amount = 0
        
        # Travel-related goals
        if any(word in goal_name_lower or word in description_lower for word in ['trip', 'travel', 'vacation', 'tour', 'europe', 'abroad']):
            if 'europe' in description_lower or 'europe' in goal_name_lower:
                base_amount = 250000  # Europe trip
            elif 'international' in description_lower or 'abroad' in description_lower:
                base_amount = 150000  # International travel
            else:
                base_amount = 80000   # Domestic travel
        
        # Gadget-related goals
        elif any(word in goal_name_lower or word in description_lower for word in ['iphone', 'phone', 'laptop', 'gadget', 'device']):
            if 'iphone' in goal_name_lower or 'iphone' in description_lower:
                base_amount = 120000  # iPhone
            elif 'laptop' in goal_name_lower or 'laptop' in description_lower:
                base_amount = 80000   # Laptop
            else:
                base_amount = 50000   # Other gadgets
        
        # Education-related goals
        elif any(word in goal_name_lower or word in description_lower for word in ['course', 'education', 'study', 'certification']):
            base_amount = 100000  # Education
        
        # Emergency fund
        elif any(word in goal_name_lower or word in description_lower for word in ['emergency', 'safety', 'backup']):
            base_amount = monthly_expenses * 6  # 6 months of expenses
        
        # Home-related goals
        elif any(word in goal_name_lower or word in description_lower for word in ['home', 'house', 'property', 'down payment']):
            base_amount = 500000  # Down payment
        
        # Default estimation based on income
        else:
            base_amount = monthly_income * 3  # 3 months of income
        
        # Adjust based on user's financial capacity
        if monthly_income > 0:
            # If user has high savings rate, they can afford more expensive goals
            if savings_rate > 30:
                affordability_multiplier = 1.5
            elif savings_rate > 20:
                affordability_multiplier = 1.2
            elif savings_rate > 10:
                affordability_multiplier = 1.0
            else:
                affordability_multiplier = 0.8
            
            adjusted_amount = base_amount * affordability_multiplier
            
            # Ensure the goal is achievable within the time frame
            max_monthly_savings = monthly_savings * 0.8  # Use 80% of current savings
            max_achievable = max_monthly_savings * request.months_to_achieve
            
            if adjusted_amount > max_achievable:
                adjusted_amount = max_achievable
            
            final_amount = round(adjusted_amount, -3)  # Round to nearest thousand
        else:
            final_amount = base_amount
        
        # Calculate monthly needed
        monthly_needed = final_amount / request.months_to_achieve
        
        # Generate AI reasoning
        reasoning_parts = []
        
        if 'europe' in description_lower or 'europe' in goal_name_lower:
            reasoning_parts.append("Europe trips typically cost ₹2-3L including flights, accommodation, and daily expenses")
        elif 'iphone' in goal_name_lower or 'iphone' in description_lower:
            reasoning_parts.append("Latest iPhones cost ₹1-1.5L depending on the model")
        elif 'laptop' in goal_name_lower or 'laptop' in description_lower:
            reasoning_parts.append("Good laptops range from ₹50K to ₹1L based on specifications")
        
        reasoning_parts.append(f"Your monthly income is ₹{monthly_income:,.0f} with a savings rate of {savings_rate:.1f}%")
        reasoning_parts.append(f"This goal requires saving ₹{monthly_needed:,.0f} per month for {request.months_to_achieve} months")
        
        if savings_rate < 20:
            reasoning_parts.append("Consider increasing your savings rate to achieve this goal comfortably")
        
        reasoning = ". ".join(reasoning_parts) + "."
        
        # Calculate feasibility score
        feasibility_score = min(1.0, (monthly_savings / monthly_needed) if monthly_needed > 0 else 1.0)
        
        return {
            "estimated_amount": final_amount,
            "monthly_needed": round(monthly_needed, 2),
            "reasoning": reasoning,
            "feasibility_score": round(feasibility_score, 2),
            "user_financial_profile": {
                "monthly_income": monthly_income,
                "monthly_expenses": monthly_expenses,
                "monthly_savings": monthly_savings,
                "savings_rate": round(savings_rate, 1)
            },
            "goal_analysis": {
                "category": "travel" if any(word in goal_name_lower for word in ['trip', 'travel', 'vacation']) else "gadgets" if any(word in goal_name_lower for word in ['iphone', 'phone', 'laptop']) else "other",
                "time_horizon_months": request.months_to_achieve,
                "estimated_monthly_contribution": round(monthly_needed, 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to estimate goal: {str(e)}")

# Finion Insights API
@router.get("/api/insights")
async def get_finion_insights(sessionid: str = Depends(get_sessionid)):
    """Get smart AI-analyzed financial insights and recommendations based on user data."""
    try:
        from datetime import datetime, timedelta
        
        logger = logging.getLogger(__name__)
        logger.info(f"Generating insights for user: {sessionid}")
        
        # Fetch comprehensive user data for analysis
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        mf_data = await mcp_client.get_mf_transactions(sessionid)
        stock_data = await mcp_client.get_stock_transactions(sessionid)
        
        # Log data availability
        logger.info(f"Bank data keys: {list(bank_data.keys()) if isinstance(bank_data, dict) else 'Not dict'}")
        logger.info(f"MF data keys: {list(mf_data.keys()) if isinstance(mf_data, dict) else 'Not dict'}")
        logger.info(f"Stock data keys: {list(stock_data.keys()) if isinstance(stock_data, dict) else 'Not dict'}")
        
        # Get demo transactions
        demo_transactions = get_demo_transactions(sessionid)
        logger.info(f"Demo transactions count: {len(demo_transactions)}")
        
        # Merge all transactions
        all_transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
        if demo_transactions:
            all_transactions.extend(demo_transactions)
        
        logger.info(f"Total transactions after merge: {len(all_transactions)}")
        
        # If no transactions at all, return early with a clear message
        if not all_transactions:
            logger.info("No transactions found - returning generic insight")
            return {
                "insights": [{
                    "type": "no_data",
                    "category": "Data",
                    "message": "No transaction data available. Start adding transactions to get personalized insights!",
                    "severity": "info",
                    "action": "Add your first transaction",
                    "current_amount": 0,
                    "previous_amount": 0,
                    "change_percent": 0
                }],
                "generated_at": datetime.now().isoformat(),
                "data_period": {
                    "current_month": "No data",
                    "previous_month": "No data"
                },
                "total_insights": 1,
                "debug_info": {
                    "user_id": sessionid,
                    "bank_data_available": bool(bank_data and not bank_data.get('error')),
                    "mf_data_available": bool(mf_data and not mf_data.get('error')),
                    "stock_data_available": bool(stock_data and not stock_data.get('error')),
                    "demo_transactions_count": len(demo_transactions),
                    "total_transactions": 0
                }
            }
        
        # Get current and previous month data for comparison
        now = datetime.now()
        current_month_start = datetime(now.year, now.month, 1)
        current_month_end = now
        
        # For demo purposes, use 2024 data
        if now.year > 2024:
            current_month_start = datetime(2024, 7, 1)
            current_month_end = datetime(2024, 7, 31)
            prev_month_start = datetime(2024, 6, 1)
            prev_month_end = datetime(2024, 6, 30)
        else:
            prev_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
            prev_month_end = current_month_start - timedelta(days=1)
        
        # Filter transactions by month
        current_month_txns = [t for t in all_transactions if 
                             current_month_start <= datetime.strptime(t['date'], '%Y-%m-%d') <= current_month_end]
        prev_month_txns = [t for t in all_transactions if 
                          prev_month_start <= datetime.strptime(t['date'], '%Y-%m-%d') <= prev_month_end]
        
        logger.info(f"Current month transactions: {len(current_month_txns)}")
        logger.info(f"Previous month transactions: {len(prev_month_txns)}")
        
        # If no current month data, return early
        if not current_month_txns:
            logger.info("No current month transactions - returning generic insight")
            return {
                "insights": [{
                    "type": "no_current_data",
                    "category": "Data",
                    "message": "No transactions found for the current month. Add some transactions to get personalized insights!",
                    "severity": "info",
                    "action": "Add transactions for current month",
                    "current_amount": 0,
                    "previous_amount": 0,
                    "change_percent": 0
                }],
                "generated_at": datetime.now().isoformat(),
                "data_period": {
                    "current_month": current_month_start.strftime("%B %Y"),
                    "previous_month": prev_month_start.strftime("%B %Y")
                },
                "total_insights": 1,
                "debug_info": {
                    "user_id": sessionid,
                    "total_transactions": len(all_transactions),
                    "current_month_count": 0,
                    "previous_month_count": len(prev_month_txns)
                }
            }
        
        # Analyze spending patterns
        insights = []
        
        # 1. Category spending analysis
        current_categories = {}
        prev_categories = {}
        
        for txn in current_month_txns:
            if txn.get('txn_type') == 'DEBIT':
                category = txn.get('category', 'Others')
                amount = txn.get('amount', 0)
                current_categories[category] = current_categories.get(category, 0) + amount
        
        for txn in prev_month_txns:
            if txn.get('txn_type') == 'DEBIT':
                category = txn.get('category', 'Others')
                amount = txn.get('amount', 0)
                prev_categories[category] = prev_categories.get(category, 0) + amount
        
        logger.info(f"Current month categories: {current_categories}")
        logger.info(f"Previous month categories: {prev_categories}")
        
        # Generate category insights
        for category, current_amount in current_categories.items():
            prev_amount = prev_categories.get(category, 0)
            if prev_amount > 0:
                change_percent = ((current_amount - prev_amount) / prev_amount) * 100
                
                if change_percent > 20:
                    insights.append({
                        "type": "spending_increase",
                        "category": category,
                        "message": f"Your spending on {category.lower()} increased by {abs(change_percent):.0f}% compared to the previous month. Consider setting a budget for this category to manage your expenses better.",
                        "severity": "high" if change_percent > 50 else "medium",
                        "action": f"Set a monthly budget for {category}",
                        "current_amount": current_amount,
                        "previous_amount": prev_amount,
                        "change_percent": change_percent
                    })
                elif change_percent < -20:
                    insights.append({
                        "type": "spending_decrease",
                        "category": category,
                        "message": f"Great job! Your {category.lower()} spending decreased by {abs(change_percent):.0f}% this month. Keep up this positive trend!",
                        "severity": "positive",
                        "action": "Continue monitoring this category",
                        "current_amount": current_amount,
                        "previous_amount": prev_amount,
                        "change_percent": change_percent
                    })
        
        # 2. Investment insights
        investment_txns = [t for t in current_month_txns if t.get('category') == 'Investment']
        if investment_txns:
            total_investment = sum(t.get('amount', 0) for t in investment_txns)
            if total_investment > 0:
                insights.append({
                    "type": "investment_activity",
                    "category": "Investment",
                    "message": f"You've invested ₹{total_investment:,.0f} this month. This is a great step towards building wealth! Consider diversifying across different asset classes.",
                    "severity": "positive",
                    "action": "Review your investment portfolio",
                    "current_amount": total_investment,
                    "previous_amount": 0,
                    "change_percent": 0
                })
        
        # 3. Credit card payment insights
        cc_payments = [t for t in current_month_txns if t.get('category') == 'Credit Card Payment']
        if cc_payments:
            total_cc_payment = sum(t.get('amount', 0) for t in cc_payments)
            if total_cc_payment > 50000:
                insights.append({
                    "type": "high_credit_payment",
                    "category": "Credit Card Payment",
                    "message": f"Your credit card payment of ₹{total_cc_payment:,.0f} is quite high. Consider reviewing your credit card usage and look for ways to reduce expenses.",
                    "severity": "medium",
                    "action": "Review credit card statements",
                    "current_amount": total_cc_payment,
                    "previous_amount": 0,
                    "change_percent": 0
                })
        
        # 4. Income insights
        income_txns = [t for t in current_month_txns if t.get('txn_type') == 'CREDIT']
        if income_txns:
            total_income = sum(t.get('amount', 0) for t in income_txns)
            total_expenses = sum(t.get('amount', 0) for t in current_month_txns if t.get('txn_type') == 'DEBIT')
            savings_rate = ((total_income - total_expenses) / total_income) * 100 if total_income > 0 else 0
            
            if savings_rate < 10:
                insights.append({
                    "type": "low_savings",
                    "category": "Savings",
                    "message": f"Your savings rate is {savings_rate:.1f}% this month. Consider the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
                    "severity": "medium",
                    "action": "Create a savings plan",
                    "current_amount": total_income - total_expenses,
                    "previous_amount": 0,
                    "change_percent": 0
                })
            elif savings_rate > 30:
                insights.append({
                    "type": "excellent_savings",
                    "category": "Savings",
                    "message": f"Excellent! You're saving {savings_rate:.1f}% of your income. This puts you ahead of most people. Consider investing your savings for better returns.",
                    "severity": "positive",
                    "action": "Explore investment options",
                    "current_amount": total_income - total_expenses,
                    "previous_amount": 0,
                    "change_percent": 0
                })
        
        # 5. Recurring payment insights
        recurring_categories = {}
        for txn in current_month_txns:
            category = txn.get('category', 'Others')
            if category in ['Streaming', 'Shopping', 'Housing']:
                recurring_categories[category] = recurring_categories.get(category, 0) + 1
        
        for category, count in recurring_categories.items():
            if count >= 3:
                insights.append({
                    "type": "frequent_spending",
                    "category": category,
                    "message": f"You've made {count} transactions in {category.lower()} this month. Consider if all these expenses are necessary or if you can optimize your spending.",
                    "severity": "medium",
                    "action": f"Review {category} expenses",
                    "current_amount": count,
                    "previous_amount": 0,
                    "change_percent": 0
                })
        
        # Sort insights by severity (high > medium > positive)
        severity_order = {"high": 3, "medium": 2, "positive": 1}
        insights.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        # Limit to top 3 most important insights
        insights = insights[:3]
        
        # If no insights generated, provide a general positive message
        if not insights:
            insights = [{
                "type": "general",
                "category": "Overall",
                "message": "Your financial health looks good! Keep tracking your expenses and stay consistent with your financial goals.",
                "severity": "positive",
                "action": "Continue monitoring",
                "current_amount": 0,
                "previous_amount": 0,
                "change_percent": 0
            }]
        
        logger.info(f"Generated {len(insights)} insights for user {sessionid}")
        
        return {
            "insights": insights,
            "generated_at": datetime.now().isoformat(),
            "data_period": {
                "current_month": current_month_start.strftime("%B %Y"),
                "previous_month": prev_month_start.strftime("%B %Y")
            },
            "total_insights": len(insights),
            "debug_info": {
                "user_id": sessionid,
                "total_transactions": len(all_transactions),
                "current_month_count": len(current_month_txns),
                "previous_month_count": len(prev_month_txns),
                "categories_analyzed": list(current_categories.keys())
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating insights for user {sessionid}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

def format_indian_currency(amount):
    """Format amount in Indian currency (lakhs, crores)"""
    if amount == 0:
        return "₹0"
    
    # Convert to positive for formatting
    is_negative = amount < 0
    amount = abs(amount)
    
    if amount >= 10000000:  # 1 crore
        formatted = f"₹{amount/10000000:.2f} crore"
    elif amount >= 100000:  # 1 lakh
        formatted = f"₹{amount/100000:.2f} lakh"
    else:
        formatted = f"₹{amount:,.0f}"
    
    return f"-{formatted}" if is_negative else formatted

def format_percentage(percentage):
    """Format percentage with appropriate precision"""
    if percentage >= 1:
        return f"{percentage:.2f}%"
    elif percentage >= 0.01:
        return f"{percentage:.4f}%"
    else:
        return f"{percentage:.6f}%"

# Data Export API
@router.get("/api/export/data")
async def export_user_data(
    format: str = Query("json", description="Export format: json, csv"),
    include_transactions: bool = Query(True, description="Include transaction data"),
    include_summary: bool = Query(True, description="Include financial summaries"),
    include_goals: bool = Query(True, description="Include financial goals"),
    sessionid: str = Depends(get_sessionid),
    response: Response = None
):
    """Export all user financial data in JSON or CSV format with download headers."""
    try:
        from datetime import datetime
        import csv
        import io
        
        # Initialize export data structure
        export_data = {
            "export_info": {
                "user_id": sessionid,
                "export_date": datetime.now().isoformat(),
                "format": format,
                "version": "1.0",
                "data_sources": ["bank_transactions", "mf_transactions", "stock_transactions", "goals", "summaries"]
            },
            "user_profile": {
                "session_id": sessionid,
                "export_timestamp": datetime.now().isoformat()
            }
        }
        
        # Fetch all financial data
        if include_transactions:
            # Bank transactions
            bank_data = await mcp_client.get_bank_transactions(sessionid)
            export_data["bank_transactions"] = bank_data
            
            # MF transactions
            mf_data = await mcp_client.get_mf_transactions(sessionid)
            export_data["mutual_fund_transactions"] = mf_data
            
            # Stock transactions
            stock_data = await mcp_client.get_stock_transactions(sessionid)
            export_data["stock_transactions"] = stock_data
            
            # Demo transactions (user-created)
            demo_transactions = get_demo_transactions(sessionid)
            export_data["demo_transactions"] = {
                "count": len(demo_transactions),
                "transactions": demo_transactions
            }
            
            # Unified transactions (processed)
            from data_processor import TransactionProcessor
            unified_transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
            unified_transactions.extend(demo_transactions)
            unified_transactions.sort(key=lambda x: x['date'], reverse=True)
            
            export_data["unified_transactions"] = {
                "count": len(unified_transactions),
                "transactions": unified_transactions
            }
        
        if include_summary:
            # Financial summaries for different periods
            summaries = {}
            
            # Current month (July 2024)
            current_month_summary = await get_transaction_summary_internal(
                "2024-07-01", "2024-07-31", sessionid
            )
            summaries["current_month"] = current_month_summary
            
            # Last month (June 2024)
            last_month_summary = await get_transaction_summary_internal(
                "2024-06-01", "2024-06-30", sessionid
            )
            summaries["last_month"] = last_month_summary
            
            # Last 3 months
            three_month_summary = await get_transaction_summary_internal(
                "2024-05-01", "2024-07-31", sessionid
            )
            summaries["last_3_months"] = three_month_summary
            
            # All time
            all_time_summary = await get_transaction_summary_internal(
                "2020-01-01", "2025-12-31", sessionid
            )
            summaries["all_time"] = all_time_summary
            
            export_data["financial_summaries"] = summaries
        
        # Net worth and other financial data
        net_worth_data = await mcp_client.get_net_worth(sessionid)
        export_data["net_worth"] = net_worth_data
        
        credit_report_data = await mcp_client.get_credit_report(sessionid)
        export_data["credit_report"] = credit_report_data
        
        epf_data = await mcp_client.get_epf_details(sessionid)
        export_data["epf_details"] = epf_data
        
        if include_goals:
            # Goals data
            goals = goals_manager.list_goals(sessionid)
            if goals:
                goals_with_progress = []
                for goal in goals:
                    progress = goals_manager.calculate_goal_progress(goal)
                    goal_data = {
                        "goal": goal,
                        "progress": progress
                    }
                    goals_with_progress.append(goal_data)
                
                export_data["financial_goals"] = {
                    "count": len(goals_with_progress),
                    "goals": goals_with_progress
                }
            else:
                export_data["financial_goals"] = {
                    "count": 0,
                    "goals": []
                }
        
        # Add data insights
        export_data["data_insights"] = {
            "total_transactions": len(export_data.get("unified_transactions", {}).get("transactions", [])),
            "date_range": {
                "earliest_transaction": min([t['date'] for t in export_data.get("unified_transactions", {}).get("transactions", [])]) if export_data.get("unified_transactions", {}).get("transactions") else None,
                "latest_transaction": max([t['date'] for t in export_data.get("unified_transactions", {}).get("transactions", [])]) if export_data.get("unified_transactions", {}).get("transactions") else None
            },
            "data_sources": ["HDFC Bank", "Mutual Funds", "Stocks", "User Created"],
            "export_complete": True
        }
        
        # Handle different formats
        if format.lower() == "csv":
            # Convert to CSV format
            csv_data = convert_to_csv(export_data)
            
            # Set download headers
            filename = f"financial_data_{sessionid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-Type"] = "text/csv"
            
            return Response(content=csv_data, media_type="text/csv")
        else:
            # JSON format (default)
            filename = f"financial_data_{sessionid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            response.headers["Content-Disposition"] = f"attachment; filename={filename}"
            response.headers["Content-Type"] = "application/json"
            
            return export_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting data: {str(e)}")

async def get_transaction_summary_internal(from_date: str, to_date: str, sessionid: str) -> Dict[str, Any]:
    """Internal function to get transaction summary for export."""
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        mf_data = await mcp_client.get_mf_transactions(sessionid)
        stock_data = await mcp_client.get_stock_transactions(sessionid)
        
        transactions = TransactionProcessor.merge_all_transactions(bank_data, mf_data, stock_data)
        demo_transactions = get_demo_transactions(sessionid)
        transactions.extend(demo_transactions)
        
        # Filter transactions by date range
        filtered_transactions = [
            txn for txn in transactions 
            if from_date <= txn['date'] <= to_date
        ]
        
        # Calculate summary
        total_expenses = sum(
            txn['amount'] for txn in filtered_transactions 
            if txn.get('txn_type') == 'DEBIT' or txn.get('type') == 'expense'
        )
        
        total_income = sum(
            txn['amount'] for txn in filtered_transactions 
            if txn.get('txn_type') == 'CREDIT' or txn.get('type') == 'income'
        )
        
        balance = total_income - total_expenses
        
        # Get latest transaction date
        latest_date = max([txn['date'] for txn in filtered_transactions]) if filtered_transactions else None
        
        return {
            "total_expenses": round(total_expenses, 2),
            "total_income": round(total_income, 2),
            "balance": round(balance, 2),
            "from_date": from_date,
            "to_date": to_date,
            "transaction_count": len(filtered_transactions),
            "currency": "INR",
            "latest_transaction_date": latest_date
        }
        
    except Exception as e:
        return {
            "error": f"Error calculating summary: {str(e)}",
            "total_expenses": 0,
            "total_income": 0,
            "balance": 0,
            "transaction_count": 0
    } 

# Celebrity Comparison API
@router.post("/api/celebrity-comparison", response_model=CelebrityComparisonResponse)
async def compare_with_celebrity(
    request: CelebrityComparisonRequest,
    sessionid: str = Depends(get_sessionid)
):
    """Compare user's financial data with a celebrity's financial data."""
    try:
        from datetime import datetime
        from config import config
        
        # Use demo data for celebrity comparison (since MCP server might not be running)
        # Based on the test data we saw earlier
        user_net_worth = 1135627  # ₹11,35,627 from test data
        user_monthly_income = 120000  # ₹1,20,000 salary from test data
        user_investments = 760627  # ₹7,60,627 mutual funds from test data
        user_real_estate = user_net_worth * 0.6  # Estimate 60% of net worth
        
        # User data is already set above using demo values
        
        # Estimate real estate (assuming 60% of net worth for typical user)
        user_real_estate = user_net_worth * 0.6
        
        # Fetch celebrity data using Vertex AI or fallback to Gemini
        if config.USE_VERTEX_AI:
            print(f"🔧 Using Vertex AI for celebrity data: {request.celebrity_name}")
            try:
                from utils.vertex_ai_client import vertex_ai_client
                celebrity_data = await vertex_ai_client.get_celebrity_data(request.celebrity_name)
                print(f"✅ Vertex AI successful for {request.celebrity_name}")
            except Exception as e:
                print(f"❌ Vertex AI failed for {request.celebrity_name}: {str(e)}")
                print("🔄 Falling back to Gemini API...")
                # Fallback to Gemini if Vertex AI fails
                import google.generativeai as genai
                genai.configure(api_key=config.GOOGLE_API_KEY)
                model = genai.GenerativeModel(config.GEMINI_MODEL)
                
                celebrity_prompt = f"""
                Get current financial data for {request.celebrity_name}. Return ONLY a JSON object with these exact fields:
                {{
                    "name": "{request.celebrity_name}",
                    "net_worth": <number in USD>,
                    "monthly_income": <number in USD>,
                    "investments": <number in USD>,
                    "real_estate": <number in USD>,
                    "primary_income_sources": ["source1", "source2"],
                    "data_source": "Forbes/Wikipedia/etc",
                    "last_updated": "2024"
                }}
                
                Rules:
                - Use latest available data (2024-2025)
                - Convert all amounts to USD
                - Be accurate and realistic
                - For Shah Rukh Khan: net worth ~$600M, monthly income ~$2M
                - For Jeff Bezos: net worth ~$170B, monthly income ~$50M
                - For Elon Musk: net worth ~$230B, monthly income ~$100M
                - Return ONLY the JSON, no explanations
                """
                
                try:
                    celebrity_response = model.generate_content(celebrity_prompt)
                    celebrity_text = celebrity_response.text.strip()
                    
                    # Extract JSON from response (handle markdown formatting)
                    if '```json' in celebrity_text:
                        celebrity_text = celebrity_text.split('```json')[1].split('```')[0]
                    elif '```' in celebrity_text:
                        celebrity_text = celebrity_text.split('```')[1]
                    
                    import json
                    celebrity_data = json.loads(celebrity_text)
                    
                except Exception as gemini_error:
                    # Fallback to mock data if both Vertex AI and Gemini fail
                    celebrity_data = {
                        "name": request.celebrity_name,
                        "net_worth": 1000000000,  # 1 billion USD
                        "monthly_income": 5000000,  # 5 million USD
                        "investments": 500000000,  # 500 million USD
                        "real_estate": 200000000,  # 200 million USD
                        "primary_income_sources": ["Entertainment", "Business"],
                        "data_source": "Estimated",
                        "last_updated": "2024"
                    }
        else:
            # Use Gemini directly
            print(f"🔧 Using Gemini API directly for celebrity data: {request.celebrity_name}")
            import google.generativeai as genai
            genai.configure(api_key=config.GOOGLE_API_KEY)
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            
            celebrity_prompt = f"""
            Get current financial data for {request.celebrity_name}. Return ONLY a JSON object with these exact fields:
            {{
                "name": "{request.celebrity_name}",
                "net_worth": <number in USD>,
                "monthly_income": <number in USD>,
                "investments": <number in USD>,
                "real_estate": <number in USD>,
                "primary_income_sources": ["source1", "source2"],
                "data_source": "Forbes/Wikipedia/etc",
                "last_updated": "2024"
            }}
            
            Rules:
            - Use latest available data (2024-2025)
            - Convert all amounts to USD
            - Be accurate and realistic
            - For Shah Rukh Khan: net worth ~$600M, monthly income ~$2M
            - For Jeff Bezos: net worth ~$170B, monthly income ~$50M
            - For Elon Musk: net worth ~$230B, monthly income ~$100M
            - Return ONLY the JSON, no explanations
            """
            
            try:
                celebrity_response = model.generate_content(celebrity_prompt)
                celebrity_text = celebrity_response.text.strip()
                
                # Extract JSON from response (handle markdown formatting)
                if '```json' in celebrity_text:
                    celebrity_text = celebrity_text.split('```json')[1].split('```')[0]
                elif '```' in celebrity_text:
                    celebrity_text = celebrity_text.split('```')[1]
                
                import json
                celebrity_data = json.loads(celebrity_text)
                
            except Exception as e:
                # Fallback to mock data if Gemini fails
                celebrity_data = {
                    "name": request.celebrity_name,
                    "net_worth": 1000000000,  # 1 billion USD
                    "monthly_income": 5000000,  # 5 million USD
                    "investments": 500000000,  # 500 million USD
                    "real_estate": 200000000,  # 200 million USD
                    "primary_income_sources": ["Entertainment", "Business"],
                    "data_source": "Estimated",
                    "last_updated": "2024"
                }
        
        # Convert celebrity data from USD to INR (approximate rate: 1 USD = 83 INR)
        usd_to_inr = 83
        celebrity_net_worth_inr = celebrity_data['net_worth'] * usd_to_inr
        celebrity_monthly_income_inr = celebrity_data['monthly_income'] * usd_to_inr
        celebrity_investments_inr = celebrity_data['investments'] * usd_to_inr
        celebrity_real_estate_inr = celebrity_data['real_estate'] * usd_to_inr
        
        # Calculate comparison percentages
        net_worth_percentage = (user_net_worth / celebrity_net_worth_inr) * 100 if celebrity_net_worth_inr > 0 else 0
        income_percentage = (user_monthly_income / celebrity_monthly_income_inr) * 100 if celebrity_monthly_income_inr > 0 else 0
        investment_percentage = (user_investments / celebrity_investments_inr) * 100 if celebrity_investments_inr > 0 else 0
        real_estate_percentage = (user_real_estate / celebrity_real_estate_inr) * 100 if celebrity_real_estate_inr > 0 else 0
        
        # Generate motivational message with Indian formatting
        if net_worth_percentage > 1:
            motivational_message = f"🎉 Amazing! You're {format_percentage(net_worth_percentage)} of {celebrity_data['name']}'s net worth! You're already in the elite league!"
        elif net_worth_percentage > 0.1:
            motivational_message = f"🚀 Impressive! You're {format_percentage(net_worth_percentage)} of {celebrity_data['name']}'s net worth. Keep building your empire!"
        elif net_worth_percentage > 0.01:
            motivational_message = f"💪 You're {format_percentage(net_worth_percentage)} of {celebrity_data['name']}'s net worth. Every journey starts with a single step!"
        else:
            motivational_message = f"🌟 You're {format_percentage(net_worth_percentage)} of {celebrity_data['name']}'s net worth. Dream big, work hard!"
        
        # Generate achievement insight
        if user_monthly_income > 0:
            years_to_1_percent = (celebrity_net_worth_inr * 0.01 - user_net_worth) / (user_monthly_income * 12)
            if years_to_1_percent > 0 and years_to_1_percent < 50:
                achievement_insight = f"At your current savings rate, you could reach 1% of {celebrity_data['name']}'s net worth in {years_to_1_percent:.1f} years!"
            else:
                achievement_insight = f"Focus on increasing your income and investments to accelerate your wealth building journey!"
        else:
            achievement_insight = "Start tracking your income to see your progress towards financial goals!"
        
        # Generate next milestone with Indian formatting
        if net_worth_percentage < 0.01:
            milestone_amount = format_indian_currency(celebrity_net_worth_inr * 0.0001)
            next_milestone = f"Reach 0.01% of {celebrity_data['name']}'s net worth ({milestone_amount})"
        elif net_worth_percentage < 0.1:
            milestone_amount = format_indian_currency(celebrity_net_worth_inr * 0.001)
            next_milestone = f"Reach 0.1% of {celebrity_data['name']}'s net worth ({milestone_amount})"
        elif net_worth_percentage < 1:
            milestone_amount = format_indian_currency(celebrity_net_worth_inr * 0.01)
            next_milestone = f"Reach 1% of {celebrity_data['name']}'s net worth ({milestone_amount})"
        else:
            next_milestone = f"Maintain your elite status and aim for 10% of {celebrity_data['name']}'s net worth!"
        
        # Handle "Not Available" cases
        def format_value(value, is_currency=True):
            if value == 0:
                return "Not Available"
            if is_currency:
                return format_indian_currency(value)
            return str(value)
        
        return CelebrityComparisonResponse(
            user_data=UserFinancialData(
                net_worth=user_net_worth,
                monthly_income=user_monthly_income,
                investments=user_investments,
                real_estate=user_real_estate
            ),
            celebrity_data=CelebrityData(
                name=celebrity_data['name'],
                net_worth=celebrity_net_worth_inr,  # Converted to INR
                monthly_income=celebrity_monthly_income_inr,  # Converted to INR
                investments=celebrity_investments_inr,  # Converted to INR
                real_estate=celebrity_real_estate_inr,  # Converted to INR
                primary_income_sources=celebrity_data['primary_income_sources'],
                data_source=celebrity_data['data_source'],
                last_updated=celebrity_data['last_updated']
            ),
            comparison=ComparisonInsights(
                net_worth_percentage=net_worth_percentage,
                income_percentage=income_percentage,
                investment_percentage=investment_percentage,
                real_estate_percentage=real_estate_percentage,
                motivational_message=motivational_message,
                achievement_insight=achievement_insight,
                next_milestone=next_milestone
            ),
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate celebrity comparison: {str(e)}")