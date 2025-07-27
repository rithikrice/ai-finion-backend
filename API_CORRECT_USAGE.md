# Complete API Usage Guide - Finance AI Agent

## Authentication
All APIs require session authentication using the `sessionid` cookie.

### Login
Login using phone number and get session cookie for subsequent API calls.

```bash
# Basic login (uses phone number as session ID)
curl -X POST "https://finion-backend-119044850014.asia-south1.run.app/api/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "8888888888"}'

# Login with custom session ID
curl -X POST "https://finion-backend-119044850014.asia-south1.run.app/api/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "8888888888", "session_id": "8888888888"}'

# Login and save cookie to file
curl -X POST "https://finion-backend-119044850014.asia-south1.run.app/api/login" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "8888888888"}' \
  -c cookies.txt

# Example successful response:
# {
#   "success": true,
#   "message": "Login successful",
#   "phone_number": "8888888888",
#   "session_id": "8888888888",
#   "expires_in": 86400,
#   "demo_note": "Session cookie set. Use this sessionid in subsequent API calls."
# }

# Example error response (invalid phone):
# {
#   "detail": "Invalid phone number format. Please provide a 10-digit phone number."
# }
```

**Demo Session ID: `8888888888`**

---

## 1. AI Assistant APIs

### Ask AI (Personal CFO)
```bash
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/ask-ai \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{"query": "What is my current net worth?"}'
```

### Ask AI (Streaming)
```bash
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/stream/ask \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{"prompt": "Analyze my spending patterns"}'
```

### Quick Insights
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/quick-insights
```

---

## 2. Financial Data APIs (REST)

### Net Worth
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/net_worth
```

### Credit Report
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/credit_report
```

### EPF Details
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/epf_details
```

### Mutual Fund Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/mf_transactions
```

### Bank Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/bank_transactions
```

### Stock Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/stock_transactions
```

---

## 3. Transaction Management APIs

### Get All Transactions (Unified)
**Note**: This endpoint returns a unified list of transactions from both MCP server (bank, mutual funds, stocks) and user-created demo transactions, all with unique IDs for full CRUD operations.

```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/transactions
```

### Get Transaction Summary
Get transaction summary (expenses, income, balance) for a date range.

**Parameters:**
- `from_date`: Start date (YYYY-MM-DD) - **Required**
- `to_date`: End date (YYYY-MM-DD) - **Required**

```bash
# Current month summary (July 2024)
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/transactions/summary?from_date=2024-07-01&to_date=2024-07-31"

# Last month summary (June 2024)
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/transactions/summary?from_date=2024-06-01&to_date=2024-06-30"

# Last 2 months summary
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/transactions/summary?from_date=2024-06-01&to_date=2024-07-31"

# Custom date range
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/transactions/summary?from_date=2024-06-15&to_date=2024-07-15"
```

**Response:**
```json
{
  "total_expenses": 107600.0,
  "total_income": 120000.0,
  "balance": 12400.0,
  "from_date": "2024-07-01",
  "to_date": "2024-07-31",
  "transaction_count": 10,
  "currency": "INR",
  "last_updated": "2025-07-25T17:14:56.148834",
  "latest_transaction_date": "2024-07-25"
}
```

### Finion Insights
Get smart AI-analyzed financial insights and recommendations based on user data (perfect for "AI Insights" section in UI).

```bash
# Get smart financial insights
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/insights"

# Example response:
# {
#   "insights": [
#     {
#       "type": "spending_increase",
#       "category": "Shopping",
#       "message": "Your spending on shopping increased by 49% compared to the previous month. Consider setting a budget for this category to manage your expenses better.",
#       "severity": "medium",
#       "action": "Set a monthly budget for Shopping",
#       "current_amount": 4700.0,
#       "previous_amount": 3150.0,
#       "change_percent": 49.2
#     }
#   ],
#   "generated_at": "2025-07-25T17:59:36.587575",
#   "data_period": {
#     "current_month": "July 2024",
#     "previous_month": "June 2024"
#   },
#   "total_insights": 2
# }
```

### Export All Financial Data
Export complete financial data in JSON or CSV format with download headers (like app export feature).

**Parameters:**
- `format`: Export format (default: "json", options: "json", "csv")
- `include_transactions`: Include transaction data (default: true)
- `include_summary`: Include financial summaries (default: true)
- `include_goals`: Include financial goals (default: true)

```bash
# Export all data as JSON (default)
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data"

# Export all data as CSV
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data?format=csv"

# Export only summaries as CSV (no transactions)
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data?format=csv&include_transactions=false"

# Export only goals as JSON
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data?format=json&include_transactions=false&include_summary=false&include_goals=true"

# Download files directly
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data?format=json" -o my_financial_data.json

curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/export/data?format=csv" -o my_financial_data.csv
```

**Response Structure:**
```json
{
  "export_info": {
    "user_id": "8888888888",
    "export_date": "2025-07-25T17:36:25.692334",
    "format": "json",
    "version": "1.0",
    "data_sources": ["bank_transactions", "mf_transactions", "stock_transactions", "goals", "summaries"]
  },
  "user_profile": {...},
  "bank_transactions": {...},
  "mutual_fund_transactions": {...},
  "stock_transactions": {...},
  "demo_transactions": {...},
  "unified_transactions": {...},
  "financial_summaries": {
    "current_month": {...},
    "last_month": {...},
    "last_3_months": {...},
    "all_time": {...}
  },
  "net_worth": {...},
  "credit_report": {...},
  "epf_details": {...},
  "financial_goals": {...},
  "data_insights": {
    "total_transactions": 20,
    "date_range": {
      "earliest_transaction": "2024-06-01",
      "latest_transaction": "2024-07-25"
    },
    "data_sources": ["HDFC Bank", "Mutual Funds", "Stocks", "User Created"],
    "export_complete": true
  }
}
```

### Create Transaction
```bash
**Note:** The `date` field is optional. If not provided, the API will use today's date. The date should be in `YYYY-MM-DD` format (e.g., "2024-07-15").

curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "amount": 1500,
    "narration": "Coffee at Starbucks",
    "date": "2024-07-15",
    "type": "expense"
  }'
```

### Update Transaction
```bash
curl -X PUT https://finion-backend-119044850014.asia-south1.run.app/api/transactions/transaction-id-here \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "amount": 2000,
    "narration": "Coffee and Pastry",
    "type": "expense"
  }'
```

### Delete Transaction
```bash
curl -X DELETE https://finion-backend-119044850014.asia-south1.run.app/api/transactions/transaction-id-here \
  -H "Cookie: sessionid=8888888888"
```

### Get Single Transaction
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/transactions/transaction-id-here
```

---

## 4. Spending Analysis APIs

**Note**: All spending APIs now include both MCP server data and user-created demo transactions for comprehensive analysis.

### Daily Spending
```bash
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/spend_daily?from_date=2024-06-01&to_date=2024-07-31"
```

### Monthly Spending
```bash
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/spend_monthly?from_date=2024-01-01&to_date=2024-12-31"
```

### Spending by Category
```bash
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/spend_by_category?from_date=2024-06-01&to_date=2024-07-31"
```

### Payment Nudges
```bash
# Get payment nudges
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/nudges

# Delete a specific nudge by category
# Note: Use URL encoding (%20) for categories with spaces
curl -X DELETE -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/nudges/Netflix

# Delete nudge with spaces (use %20 for spaces)
curl -X DELETE -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/nudges/Kotak%20MF%20SIP

curl -X DELETE -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/nudges/AMEX%20Card%20Payment

# Delete nudge (case-insensitive)
curl -X DELETE -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/nudges/rent

# Example successful response:
# {
#   "success": true,
#   "message": "Payment nudge for 'Kotak MF SIP' has been removed",
#   "deleted_nudge": {
#     "category": "Kotak MF SIP",
#     "amount": 10000,
#     "due": "2025-07-31",
#     "last_paid": "2024-07-05",
#     "merchant": "ACH D-KOTAKMF-SIP/20240705/KMF12345",
#     "autopay_eligible": true
#   },
#   "demo_note": "Nudge removed from your preferences and will no longer appear in the list"
# }

# Common URL encodings for spaces:
# Space: %20
# Ampersand: %26
# Plus: %2B
# Forward slash: %2F
```

---

## 5. Goal Management APIs

### AI Goal Estimation
Get AI-powered goal amount estimation based on user's financial data.

```bash
# Estimate Europe trip goal
curl -X POST "https://finion-backend-119044850014.asia-south1.run.app/api/goals/estimate" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "Europe Tour",
    "description": "10 day Europe trip in December 2025",
    "months_to_achieve": 6
  }'

# Estimate iPhone goal
curl -X POST "https://finion-backend-119044850014.asia-south1.run.app/api/goals/estimate" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "New iPhone",
    "description": "Buy latest iPhone 15 Pro",
    "months_to_achieve": 2
  }'

# Example response:
# {
#   "estimated_amount": 250000,
#   "monthly_needed": 41667,
#   "reasoning": "Europe trips typically cost ₹2-3L including flights, accommodation, and daily expenses. Your monthly income is ₹120,000 with a savings rate of 10.3%. This goal requires saving ₹41,667 per month for 6 months.",
#   "feasibility_score": 0.85,
#   "user_financial_profile": {
#     "monthly_income": 120000,
#     "monthly_expenses": 107600,
#     "monthly_savings": 12400,
#     "savings_rate": 10.3
#   },
#   "goal_analysis": {
#     "category": "travel",
#     "time_horizon_months": 6,
#     "estimated_monthly_contribution": 41667
#   }
# }
```

### List All Goals (Enhanced)
Get all goals with progress calculations and monthly needed amounts.

```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/goals

# Example response:
# {
#   "goals": [
#     {
#       "name": "Europe Tour",
#       "target_amount": 250000,
#       "current_amount": 75000,
#       "progress_percentage": 30.0,
#       "monthly_needed": 35000.0,
#       "remaining_months": 6,
#       "remaining_amount": 175000,
#       "on_track": true
#     }
#   ],
#   "total_goals": 1,
#   "total_target": 250000,
#   "total_saved": 75000,
#   "overall_progress": 30.0
# }
```

### Create Goal (AI-First with Finion Insights)
```bash
# Simplified AI-Estimated Goal (recommended)
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "Europe Vacation",
    "description": "Save for Europe trip",
    "category": "travel",
    "time_frame_months": 6
  }'

# Response includes:
# - AI-estimated target_amount
# - detailed_reasoning (category_basis, financial_analysis, monthly_savings_needed, achievement_difficulty)
# - finion_insights (savings_strategy, lifestyle_recommendations, investment_opportunities, risk_assessment, success_probability)

# AI-Estimated Goal with current amount
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "iPhone 15",
    "current_amount": 15000,
    "description": "Buy new iPhone",
    "category": "gadgets",
    "time_frame_months": 3
  }'

# Emergency Fund Goal
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "Emergency Fund",
    "description": "6 months of expenses backup",
    "category": "emergency",
    "time_frame_months": 12
  }'

# Manual Goal with target date (for backward compatibility)
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "Europe Vacation",
    "target_amount": 100000,
    "current_amount": 25000,
    "target_date": "2024-12-31T00:00:00",
    "description": "Save for Europe trip",
    "category": "vacation"
  }'
```

**Enhanced Response Format:**
```json
{
  "id": "goal-id",
  "name": "Europe Trip",
  "target_amount": 60000.0,
  "ai_estimated": true,
  "detailed_reasoning": {
    "category_basis": "Europe trips typically cost ₹2.5L including flights, accommodation, food, and activities",
    "financial_analysis": "Your moderate savings rate of 10.3% is suitable for this goal",
    "monthly_savings_needed": 10000.0,
    "achievement_difficulty": "Moderate"
  },
  "finion_insights": {
    "savings_strategy": [
      "🎯 You're already saving enough! Maintain your current savings rate.",
      "✈️ Book flights 6-8 months in advance for better prices"
    ],
    "lifestyle_recommendations": [
      "🏠 Consider home-sharing or budget accommodations",
      "🍽️ Plan meals to avoid expensive tourist restaurants"
    ],
    "investment_opportunities": [
      "💰 High-yield savings accounts or liquid funds"
    ],
    "risk_assessment": "Low - Goal is achievable with current or slightly improved savings",
    "success_probability": "Very High (95%)"
  }
}
```

### Get Goal by ID
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/goals/goal-id-here
```

### Update Goal
```bash
curl -X PUT https://finion-backend-119044850014.asia-south1.run.app/api/goals/goal-id-here \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "current_amount": 30000
  }'
```

### Delete Goal
```bash
curl -X DELETE https://finion-backend-119044850014.asia-south1.run.app/api/goals/goal-id-here \
  -H "Cookie: sessionid=8888888888"
```

### Get Goal Progress
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/goals/goal-id-here/progress
```

---

## 6. What-If Simulator APIs

### Mutual Fund Returns
```bash
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/whatif \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "scenario": "mf_return",
    "amount": 100000,
    "horizon_months": 24,
    "annual_rate": 0.12
  }'
```

### Spend Reduction Impact
```bash
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/whatif \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "scenario": "spend_reduction",
    "percent": 20
  }'
```

---

## 7. Lifestyle Recommendations APIs

### Get Recommendations
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/api/lifestyle-changes
```

### Apply Lifestyle Change
```bash
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/lifestyle-changes/apply \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "change_type": "reduce_dining",
    "current_value": 5000,
    "target_value": 3000
  }'
```

---

## 8. Streaming APIs (SSE)

### Stream Net Worth
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/net_worth
```

### Stream Credit Report
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/credit_report
```

### Stream EPF Details
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/epf_details
```

### Stream Mutual Fund Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/mf_transactions
```

### Stream Bank Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/bank_transactions
```

### Stream Stock Transactions
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/stock_transactions
```

### Stream Daily Spending
```bash
curl -H "Cookie: sessionid=8888888888" \
  https://finion-backend-119044850014.asia-south1.run.app/stream/spend_daily
```

---

## 9. System APIs

### Health Check
```bash
curl https://finion-backend-119044850014.asia-south1.run.app/health
```

### Root Endpoint
```bash
curl https://finion-backend-119044850014.asia-south1.run.app/
```

### API Documentation
```bash
# Open in browser
open https://finion-backend-119044850014.asia-south1.run.app/docs
```

---

## Demo Script Examples

### 1. Complete Financial Overview
```bash
# Get net worth
curl -H "Cookie: sessionid=8888888888" https://finion-backend-119044850014.asia-south1.run.app/api/net_worth

# Get quick insights
curl -H "Cookie: sessionid=8888888888" https://finion-backend-119044850014.asia-south1.run.app/api/quick-insights

# Ask AI about finances
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/ask-ai \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{"query": "What should I focus on financially?"}'
```

### 2. Transaction Management Demo
```bash
# Create transaction
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/transactions \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{"amount": 2500, "narration": "Grocery shopping", "type": "expense"}'

# List all transactions
curl -H "Cookie: sessionid=8888888888" https://finion-backend-119044850014.asia-south1.run.app/api/transactions

# Get spending analysis
curl -H "Cookie: sessionid=8888888888" \
  "https://finion-backend-119044850014.asia-south1.run.app/api/spend_by_category?from_date=2024-07-01&to_date=2024-07-31"
```

### 3. Goal Tracking Demo
```bash
# List goals
curl -H "Cookie: sessionid=8888888888" https://finion-backend-119044850014.asia-south1.run.app/api/goals

# Create new goal
curl -X POST https://finion-backend-119044850014.asia-south1.run.app/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "name": "Emergency Fund",
    "target_amount": 50000,
    "current_amount": 15000,
    "target_date": "2024-12-31T00:00:00",
    "category": "emergency"
  }'
```

---

## Common Issues and Solutions

### 1. "login required" Error
- **Solution**: Use correct session ID: `8888888888`
- **Example**: `-H "Cookie: sessionid=8888888888"`

### 2. "Field required" Error
- **Solution**: Use correct parameter names (`from_date`, `to_date`)
- **Example**: `?from_date=2024-07-01&to_date=2024-07-31`

### 3. "Goal not found" Error
- **Solution**: Use actual UUID from goals list, not slug
- **Example**: Use `c122f7f9-90a4-4142-bf06-02aa0c9dc0da` not `emergency-fund`

### 4. "Unknown scenario" Error
- **Solution**: Only `mf_return` and `spend_reduction` are supported
- **Example**: Use `"scenario": "mf_return"` not `"scenario": "increase_sip"`

---

## Performance Tips

1. **Use session ID `8888888888`** - Has complete demo data
2. **For AI queries** - Use `/api/ask-ai` for intelligent responses
3. **For streaming** - Use SSE endpoints for real-time updates
4. **For analysis** - Use spending APIs with date ranges
5. **For goals** - Use the unified `/api/goals` endpoint

---

## All APIs Summary

| Category | Endpoints | Count |
|----------|-----------|-------|
| AI Assistant | `/api/ask-ai`, `/stream/ask`, `/api/quick-insights` | 3 |
| Financial Data | `/api/net_worth`, `/api/credit_report`, etc. | 6 |
| Transactions | `/api/transactions` (CRUD) | 5 |
| Spending Analysis | `/api/spend_daily`, `/api/spend_monthly`, etc. | 4 |
| Goals | `/api/goals` (CRUD) | 6 |
| What-If | `/api/whatif` | 1 |
| Lifestyle | `/api/lifestyle-changes` | 2 |
| Streaming | `/stream/*` | 7 |
| System | `/health`, `/` | 2 |

**Total: 36 API endpoints** - All working with session ID `8888888888` 

# Celebrity Comparison API

## Compare with Celebrity

Compare your financial data with famous personalities.

**Endpoint:** `POST /api/celebrity-comparison`

**Request Body:**
```json
{
  "celebrity_name": "Shah Rukh Khan",
  "comparison_type": "all"
}
```

**Response:**
```json
{
  "user_data": {
    "net_worth": 5000000,
    "monthly_income": 150000,
    "investments": 2000000,
    "real_estate": 3000000
  },
  "celebrity_data": {
    "name": "Shah Rukh Khan",
    "net_worth": 49800000000,
    "monthly_income": 166000000,
    "investments": 33200000000,
    "real_estate": 16600000000,
    "primary_income_sources": ["Entertainment", "Business"],
    "data_source": "Forbes 2024",
    "last_updated": "2024"
  },
  "comparison": {
    "net_worth_percentage": 0.0100,
    "income_percentage": 0.0904,
    "investment_percentage": 0.0602,
    "real_estate_percentage": 0.1807,
    "motivational_message": "💪 You're 0.0100% of Shah Rukh Khan's net worth. Every journey starts with a single step!",
    "achievement_insight": "At your current savings rate, you could reach 1% of Shah Rukh Khan's net worth in 8.3 years!",
    "next_milestone": "Reach 0.1% of Shah Rukh Khan's net worth (₹4.98 crore)"
  },
  "generated_at": "2025-07-26T17:30:00.000000"
}
```

**Example Usage:**
```bash
# Compare with Shah Rukh Khan
curl -X POST "http://localhost:8000/api/celebrity-comparison" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "celebrity_name": "Shah Rukh Khan"
  }'

# Compare with Jeff Bezos
curl -X POST "http://localhost:8000/api/celebrity-comparison" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "celebrity_name": "Jeff Bezos"
  }'

# Compare with Elon Musk
curl -X POST "http://localhost:8000/api/celebrity-comparison" \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "celebrity_name": "Elon Musk"
  }'
```

**Features:**
- Real-time celebrity data via Gemini AI
- Side-by-side financial comparison in Indian Rupees (₹)
- Indian number formatting (lakhs, crores) for easy reading
- Motivational messages and insights
- Achievement tracking and milestones
- Multiple comparison metrics (net worth, income, investments, real estate)
- USD to INR conversion (1 USD = 83 INR) 