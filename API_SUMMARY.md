# Finance AI Agent API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
All endpoints require a `sessionid` cookie for authentication.

### Test Session IDs:
- `9999999999` - Demo user with complete data and goals
- `8888888888` - User with bank transactions and investments
- `2121212121` - FIRE (Financial Independence) focused user

---

## 1. AI Assistant Endpoints

### Ask AI - Personal CFO (Enhanced with Intelligent Data Fetching)
Your intelligent financial advisor that uses query analysis to fetch only relevant data, providing faster and more focused responses.

**Endpoint:** `POST /api/ask-ai`

**Key Features:**
- **Selective API Calling**: Only fetches data relevant to your question
- **Intent Recognition**: Understands spending, investment, credit, goals queries
- **Mobile-Optimized**: Concise responses under 100 words
- **Performance Tracking**: Shows which APIs were called

**Curl Example:**
```bash
curl -X POST http://localhost:8000/api/ask-ai \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "query": "What'\''s my spending trend?"
  }'
```

**Frontend Usage (JavaScript/React):**
```javascript
const askAI = async (query) => {
  const response = await fetch('/api/ask-ai', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include', // Important for cookies
    body: JSON.stringify({ query })
  });
  return response.json();
};

// Usage examples
const spendingTrend = await askAI("What's my spending trend?");
const creditScore = await askAI("What is my credit score?");
const investments = await askAI("How are my investments performing?");
```

**Response Format:**
```json
{
  "query": "What's my spending trend?",
  "response": "Hey there! Based on your data, you've spent ₹208.9K across 20 transactions. Your spending is up 6% from last month. Your biggest expenses are Credit Card Payments (₹86.85K), Housing (₹60K), and Investments (₹53K).\n\nYour investment spending is positive 💰! Consider tracking your credit card payments more closely to better understand monthly spending 📈.",
  "analysis": {
    "intent": "spending_analysis",
    "data_sources_used": ["bank_transactions", "spending_analysis"],
    "time_period": "all_time",
    "specific_focus": ["trend"]
  },
  "performance": {
    "apis_called": 2,
    "selective_fetching": true,
    "response_optimized": true
  },
    "has_bank_data": true,
    "has_investments": true,
    "has_credit_info": true,
    "has_goals": true,
    "upcoming_payments": 4
  },
  "timestamp": "2025-07-23T00:00:00.000000"
}
```

### Quick Insights
Pre-computed financial insights for fast mobile experience.

**Endpoint:** `GET /api/quick-insights`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=9999999999" \
  http://localhost:8000/api/quick-insights
```

**Frontend Usage:**
```javascript
const getQuickInsights = async () => {
  const response = await fetch('/api/quick-insights', {
    credentials: 'include'
  });
  return response.json();
};
```

**Response Format:**
```json
{
  "insights": [
    {
      "type": "net_worth",
      "title": "Net Worth",
      "value": "₹1,135,627",
      "icon": "💰"
    },
    {
      "type": "next_payment",
      "title": "Next Payment",
      "value": "Rent - ₹30,000",
      "subtitle": "Due: 2025-07-28",
      "icon": "📅"
    }
  ],
  "quick_actions": [
    {
      "label": "What should I focus on?",
      "query": "What's my top financial priority right now?"
    }
  ]
}
```

---

## 2. Financial Data Endpoints

### Net Worth
Get user's complete net worth breakdown.

**Endpoint:** `GET /api/net_worth`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/net_worth
```

### Bank Transactions
Retrieve all bank transactions.

**Endpoint:** `GET /api/bank_transactions`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/bank_transactions
```

### Credit Report
Get credit score and credit history.

**Endpoint:** `GET /api/credit_report`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/credit_report
```

### EPF Details
Employee Provident Fund information.

**Endpoint:** `GET /api/epf_details`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/epf_details
```

### Mutual Fund Transactions
Get all mutual fund investments and transactions.

**Endpoint:** `GET /api/mf_transactions`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/mf_transactions
```

### Stock Transactions
Get stock portfolio and trading history.

**Endpoint:** `GET /api/stock_transactions`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/stock_transactions
```

---

## 3. Analytics Endpoints

### Daily Spending
Get daily spending breakdown.

**Endpoint:** `GET /api/spend_daily`

**Query Parameters:**
- `from` (optional): Start date (YYYY-MM-DD)
- `to` (optional): End date (YYYY-MM-DD)

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  "http://localhost:8000/api/spend_daily?from_date=2024-06-01&to_date=2024-07-31"
```

**Frontend Usage:**
```javascript
const getDailySpending = async (fromDate, toDate) => {
  const params = new URLSearchParams();
  if (fromDate) params.append('from', fromDate);
  if (toDate) params.append('to', toDate);
  
  const response = await fetch(`/api/spend_daily?${params}`, {
    credentials: 'include'
  });
  return response.json();
};
```

**Response Format:**
```json
{
  "daily_spending": [
    {
      "date": "2024-07-01",
      "amount": 40000,
      "transactions": 2
    }
  ],
  "total": 157900,
  "average": 7895,
  "period": {
    "from": "2024-06-01",
    "to": "2024-07-31"
  }
}
```

### Monthly Spending
Get monthly spending summary.

**Endpoint:** `GET /api/spend_monthly`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  "http://localhost:8000/api/spend_monthly?from_date=2024-01-01&to_date=2024-12-31"
```

### Spending by Category
Get spending breakdown by categories.

**Endpoint:** `GET /api/spend_by_category`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  "http://localhost:8000/api/spend_by_category?from_date=2024-06-01&to_date=2024-07-31"
```

**Response Format:**
```json
{
  "breakdown": [
    {
      "category": "Housing",
      "amount": 60000,
      "percentage": 38,
      "transaction_count": 2
    },
    {
      "category": "Credit Card Payment",
      "amount": 86850,
      "percentage": 55,
      "transaction_count": 2
    }
  ],
  "total": 157900,
  "period": {
    "from": "2024-06-01",
    "to": "2024-07-31"
  }
}
```

### Payment Nudges
Get upcoming recurring payments and reminders.

**Endpoint:** `GET /api/nudges`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/api/nudges
```

**Frontend Usage:**
```javascript
const getPaymentNudges = async () => {
  const response = await fetch('/api/nudges', {
    credentials: 'include'
  });
  return response.json();
};
```

**Response Format:**
```json
[
  {
    "category": "Rent",
    "amount": 30000,
    "due": "2025-07-28",
    "last_paid": "2024-07-01",
    "merchant": "IMPS-123456789-ANNA VARGHESE-JULY RENT",
    "autopay_eligible": true
  },
  {
    "category": "Netflix",
    "amount": 750,
    "due": "2025-07-28",
    "last_paid": "2024-07-18",
    "merchant": "UPI-NETFLIX-NFLX@ICICI",
    "autopay_eligible": true
  }
]
```

---

## 4. Goals Management

### List Goals
Get all financial goals.

**Endpoint:** `GET /api/goals`

**Curl Example:**
```bash
curl -H "Cookie: sessionid=9999999999" \
  http://localhost:8000/api/goals
```

### Create Goal
Create a new financial goal.

**Endpoint:** `POST /api/goals`

**Curl Example:**
```bash
curl -X POST http://localhost:8000/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=9999999999" \
  -d '{
    "name": "New Car",
    "target_amount": 800000,
    "target_date": "2026-12-31",
    "category": "vehicle",
    "monthly_contribution": 20000
  }'
```

**Frontend Usage:**
```javascript
const createGoal = async (goalData) => {
  const response = await fetch('/api/goals', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    body: JSON.stringify(goalData)
  });
  return response.json();
};
```

### Goal Progress
Get detailed progress for a specific goal.

**Endpoint:** `GET /api/goals/{goal_id}/progress`

**Curl Example:**
```bash
# First get the goal ID from the goals list
curl -H "Cookie: sessionid=9999999999" \
  http://localhost:8000/api/goals

# Then use the actual UUID (example)
curl -H "Cookie: sessionid=9999999999" \
  http://localhost:8000/api/goals/25809baa-d242-450d-a40f-631d21bd393d/progress
```

**Response Format:**
```json
{
  "goal": {
    "id": "emergency-fund",
    "name": "Emergency Fund",
    "target_amount": 300000,
    "current_amount": 15000,
    "target_date": "2025-12-31"
  },
  "progress": {
    "percentage": 5,
    "amount_remaining": 285000,
    "days_remaining": 526,
    "on_track": false,
    "monthly_required": 18095,
    "projected_completion": "2027-06-15"
  }
}
```

---

## 5. Simulation Endpoints

### What-If Analysis
Simulate financial scenarios.

**Endpoint:** `POST /api/whatif`

**Curl Example:**
```bash
# Mutual Fund Return Projection
curl -X POST http://localhost:8000/api/whatif \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "scenario": "mf_return",
    "amount": 100000,
    "horizon_months": 12
  }'

# Spend Reduction Impact
curl -X POST http://localhost:8000/api/whatif \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=8888888888" \
  -d '{
    "scenario": "spend_reduction",
    "percent": 20
  }'
```

---

## 6. Streaming Endpoints

### Net Worth Stream
Real-time net worth updates (SSE).

**Endpoint:** `GET /stream/net_worth`

**Curl Example:**
```bash
curl -N -H "Cookie: sessionid=8888888888" \
  http://localhost:8000/stream/net_worth
```

**Frontend Usage (React):**
```javascript
const streamNetWorth = () => {
  const eventSource = new EventSource('/stream/net_worth', {
    withCredentials: true
  });
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Net worth update:', data.net_worth);
  };
  
  eventSource.onerror = (error) => {
    console.error('Stream error:', error);
    eventSource.close();
  };
  
  return eventSource;
};
```

### Daily Spend Stream
Real-time spending updates.

**Endpoint:** `GET /stream/spend_daily`

---

## Error Handling

All endpoints return appropriate HTTP status codes:

- `200` - Success
- `401` - No session cookie found
- `404` - Resource not found
- `500` - Internal server error

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Frontend Integration Best Practices

### 1. Setup Axios/Fetch with Defaults
```javascript
// axios setup
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  withCredentials: true, // Important for cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// Usage
const response = await api.post('/api/ask-ai', { query: "Help me budget" });
```

### 2. React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useFinancialInsights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('/api/quick-insights', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        setInsights(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);
  
  return { insights, loading };
};
```

### 3. Mobile-Optimized Chat Component
```javascript
const FinanceChat = () => {
  const [messages, setMessages] = useState([]);
  
  const sendMessage = async (text) => {
    // Add user message
    setMessages(prev => [...prev, { type: 'user', text }]);
    
    // Get AI response
    const response = await fetch('/api/ask-ai', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ query: text })
    });
    
    const data = await response.json();
    
    // Add AI response
    setMessages(prev => [...prev, { 
      type: 'ai', 
      text: data.response 
    }]);
  };
  
  return (
    <ChatInterface messages={messages} onSend={sendMessage} />
  );
};
```

---

## Testing

To test the APIs, first ensure the MCP server is running:
```bash
# Terminal 1: Start MCP server
cd fi-mcp-dev
npm start

# Terminal 2: Start Finance AI Agent
cd python-agent
source venv/bin/activate
python main.py
```

Then use the provided curl commands or integrate with your frontend application. 