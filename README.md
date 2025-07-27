# Finance AI Agent 🚀

A personal finance AI agent powered by Google Gemini and Vertex AI that provides intelligent financial insights and recommendations based on real user data.

## Features

- **AI-Powered Financial Assistant**: Natural language queries about your finances using Google Gemini 1.5 Flash
- **Vertex AI Integration**: Enhanced celebrity data retrieval with enterprise-grade AI capabilities and robust fallback mechanisms
- **Real-time Data Integration**: Connects to Go MCP server for live financial data
- **Goal Management**: Create, track, and manage financial goals with progress calculations
- **Lifestyle Recommendations**: Get personalized spending optimization suggestions
- **Celebrity Comparisons**: Compare your financial status with celebrities using AI-powered data with automatic fallback (Vertex AI → Gemini API → Mock data)
- **Streaming Support**: Real-time SSE streaming for both AI responses and financial data

## Prerequisites

- Python 3.8+
- Google API Key for Gemini
- Go MCP server running at `http://localhost:8080` (optional)
- Google Cloud Project with Vertex AI enabled (optional, for enhanced celebrity data)

## Quick Start

1. Clone and enter the directory:
```bash
git clone <repository-url>
cd python-agent
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your Google API key:
```bash
export GOOGLE_API_KEY="your_api_key_here"
# Or create a .env file with: GOOGLE_API_KEY=your_api_key_here
```

5. Run the application:
```bash
python main.py
```

6. Open API docs: http://localhost:8000/docs

7. **For demo**: Use cookie `sessionid=demo_session_123` to access pre-loaded demo data!

## API Endpoints

**AI Agent**: `POST /api/ask`, `POST /stream/ask` | **Financial Data (REST)**: `GET /api/net_worth`, `GET /api/credit_report`, `GET /api/epf_details`, `GET /api/mf_transactions`, `GET /api/bank_transactions`, `GET /api/stock_transactions` | **Financial Data (SSE)**: `GET /stream/net_worth`, `GET /stream/credit_report`, `GET /stream/epf_details`, `GET /stream/mf_transactions`, `GET /stream/bank_transactions`, `GET /stream/stock_transactions` | **Goal Management**: `GET /api/goals`, `POST /api/goals`, `GET /api/goals/{goal_id}`, `PUT /api/goals/{goal_id}`, `DELETE /api/goals/{goal_id}`, `GET /api/goals/{goal_id}/progress` | **Lifestyle**: `GET /api/lifestyle-changes`, `POST /api/lifestyle-changes/apply` | **Celebrity**: `POST /api/celebrity-comparison`

## Demo Usage Examples

### Ask the AI Agent

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=demo_session_123" \
  -d '{"prompt": "What is my current net worth?"}'
```

### View Demo Goals

```bash
curl http://localhost:8000/api/goals \
  -H "Cookie: sessionid=demo_session_123"
```

### Create a Financial Goal

```bash
curl -X POST http://localhost:8000/api/goals \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=demo_session_123" \
  -d '{
    "name": "New Car Fund",
    "target_amount": 30000,
    "current_amount": 5000,
    "target_date": "2024-12-31T00:00:00",
    "category": "vehicle"
  }'
```

### Stream AI Response

```javascript
const eventSource = new EventSource('/stream/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Cookie': 'sessionid=demo_session_123'
  },
  body: JSON.stringify({ prompt: "Analyze my spending patterns" })
});

eventSource.onmessage = (event) => {
  console.log('AI Response:', event.data);
};
```

### Compare with Celebrity

```bash
curl -X POST http://localhost:8000/api/celebrity-comparison \
  -H "Content-Type: application/json" \
  -H "Cookie: sessionid=demo_session_123" \
  -d '{
    "celebrity_name": "Shah Rukh Khan",
    "comparison_type": "all"
  }'
```

## Key Features

1. **Instant Setup** - In-memory database means no configuration needed
2. **Live AI Integration** - Real-time financial advice using Google Gemini
3. **Vertex AI Integration** - Enterprise-grade AI for celebrity data with fallback support
4. **Comprehensive API** - Full REST & SSE support for all operations
5. **Goal Tracking** - Smart calculations for monthly savings needed
6. **Lifestyle Optimization** - Actionable recommendations for saving money
7. **Celebrity Comparisons** - AI-powered financial comparisons with motivational insights
8. **Production Ready** - Proper error handling, logging, and documentation

## Technical Highlights

- **FastAPI** for high-performance async API
- **Google Generative AI** for intelligent responses
- **Vertex AI** for enterprise-grade AI capabilities with robust fallback mechanisms
- **SQLAlchemy** with in-memory SQLite for data persistence
- **SSE (Server-Sent Events)** for real-time streaming
- **Pydantic** for data validation and response structure consistency
- **HTTPX** for async HTTP client
- **Clean Architecture** with separation of concerns
- **Production-Ready** with comprehensive error handling and logging

## License

[Your License Here]
