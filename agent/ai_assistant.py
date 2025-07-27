# agent/ai_assistant.py
"""
AI Assistant with ADK integration for intelligent, focused responses.
Uses selective API calling based on query context with chat history.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import google.generativeai as genai
from config import config
import hashlib
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=config.GOOGLE_API_KEY)

class ChatMessage:
    """Represents a single chat message with metadata."""
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

class ChatSession:
    """Manages chat history for a user session."""
    def __init__(self, sessionid: str, max_age_minutes: int = 30):
        self.sessionid = sessionid
        self.messages: List[ChatMessage] = []
        self.max_age = timedelta(minutes=max_age_minutes)
        self.last_activity = datetime.now()
    
    def add_message(self, role: str, content: str):
        """Add a new message to the chat history."""
        self.messages.append(ChatMessage(role, content))
        self.last_activity = datetime.now()
        self._cleanup_old_messages()
    
    def get_recent_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent messages for context (last N messages)."""
        self._cleanup_old_messages()
        recent_messages = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages
        return [{"role": msg.role, "content": msg.content} for msg in recent_messages]
    
    def get_summary_context(self) -> str:
        """Get a summary of the conversation for context."""
        if len(self.messages) < 3:
            return ""
        
        # Create a brief summary of the conversation
        user_messages = [msg.content for msg in self.messages if msg.role == 'user']
        if len(user_messages) > 1:
            return f"Previous conversation context: User has asked about {', '.join(user_messages[-3:])}"
        return ""
    
    def _cleanup_old_messages(self):
        """Remove messages older than max_age."""
        cutoff_time = datetime.now() - self.max_age
        self.messages = [msg for msg in self.messages if msg.timestamp > cutoff_time]

class SmartFinanceAssistant:
    """
    Intelligent finance assistant that uses ADK to selectively call APIs
    based on the user's query, providing focused and specific responses.
    """
    
    def __init__(self, mcp_client, goals_manager):
        self.mcp_client = mcp_client
        self.goals_manager = goals_manager
        self.model = genai.GenerativeModel(model_name=config.GEMINI_MODEL)
        
        # Enhanced caching system
        self.response_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Chat sessions storage
        self.chat_sessions: Dict[str, ChatSession] = defaultdict(lambda: None)
        
        # Performance tracking
        self.query_times = {}
        
    def _get_or_create_chat_session(self, sessionid: str) -> ChatSession:
        """Get or create a chat session for the user."""
        if self.chat_sessions[sessionid] is None:
            self.chat_sessions[sessionid] = ChatSession(sessionid)
        return self.chat_sessions[sessionid]
        
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze the user's query to determine what data is needed.
        Uses pattern matching for common queries, AI for complex ones.
        """
        query_lower = query.lower()
        
        # Fast pattern matching for common queries
        # Check travel planning first (before spending) as it's more specific
        if any(word in query_lower for word in ['trip', 'travel', 'vacation', 'holiday', 'europe', 'abroad']):
            # Travel planning needs comprehensive financial analysis
            return {
                "intent": "travel_planning",
                "data_needed": ["bank_transactions", "net_worth", "goals"],
                "time_period": "last_3_months",
                "specific_focus": ["budget", "savings", "planning"],
                "requires_calculation": True
            }
        
        elif any(word in query_lower for word in ['credit score', 'credit report', 'cibil']):
            return {
                "intent": "credit_health",
                "data_needed": ["credit_report"],
                "time_period": None,
                "specific_focus": None,
                "requires_calculation": False
            }
        
        elif any(word in query_lower for word in ['spending', 'spent', 'expenses', 'spend']):
            # Determine time period with better date detection
            time_period = "last_month"
            specific_focus = ["amount", "category"]
            
            # Check for specific dates first
            if 'june 2024' in query_lower:
                time_period = "june_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'july 2024' in query_lower:
                time_period = "july_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'may 2024' in query_lower:
                time_period = "may_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'april 2024' in query_lower:
                time_period = "april_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'march 2024' in query_lower:
                time_period = "march_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'february 2024' in query_lower or 'feb 2024' in query_lower:
                time_period = "february_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'january 2024' in query_lower or 'jan 2024' in query_lower:
                time_period = "january_2024"
                specific_focus = ["monthly", "specific_month"]
            elif 'trend' in query_lower:
                time_period = "all_time"
                specific_focus = ["trend"]
            elif 'today' in query_lower or 'daily' in query_lower:
                time_period = "last_week"
                specific_focus = ["daily"]
            elif 'month' in query_lower:
                time_period = "last_month"
                specific_focus = ["monthly"]
            elif 'year' in query_lower:
                time_period = "last_year"
                specific_focus = ["yearly"]
            elif 'week' in query_lower:
                time_period = "last_week"
                specific_focus = ["weekly"]
            else:
                time_period = "last_month"
                specific_focus = ["monthly"]
            
            return {
                "intent": "spending_analysis",
                "data_needed": ["bank_transactions"],
                "time_period": time_period,
                "specific_focus": specific_focus,
                "requires_calculation": True
            }
        
        elif any(word in query_lower for word in ['invest', 'investment', 'mutual fund', 'mf', 'stocks', 'portfolio']):
            return {
                "intent": "investment_analysis",
                "data_needed": ["mf_transactions", "stock_transactions", "net_worth"],
                "time_period": "last_3_months",
                "specific_focus": ["returns", "performance", "allocation"],
                "requires_calculation": True
            }
        
        elif any(word in query_lower for word in ['goal', 'target', 'save', 'saving']):
            return {
                "intent": "goal_management",
                "data_needed": ["goals", "bank_transactions"],
                "time_period": "last_month",
                "specific_focus": ["progress", "planning"],
                "requires_calculation": True
            }
        
        elif any(word in query_lower for word in ['net worth', 'wealth', 'assets', 'liabilities']):
            return {
                "intent": "wealth_analysis",
                "data_needed": ["net_worth"],
                "time_period": None,
                "specific_focus": None,
                "requires_calculation": False
            }
        
        elif any(word in query_lower for word in ['budget', 'planning', 'financial plan']):
            return {
                "intent": "financial_planning",
                "data_needed": ["bank_transactions", "goals", "net_worth"],
                "time_period": "last_3_months",
                "specific_focus": ["budgeting", "planning"],
                "requires_calculation": True
            }
        
        # Default for general questions
        else:
            logger.info(f"No specific intent matched for query: {query}")
            return {
            "intent": "general_inquiry",
            "data_needed": ["bank_transactions", "net_worth"],
                "time_period": "last_month",
            "specific_focus": ["overview"],
            "requires_calculation": False
            }
    
    async def fetch_relevant_data(self, sessionid: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch only the data needed based on the analysis.
        Uses parallel processing for speed.
        """
        data_needed = analysis.get('data_needed', [])
        context = {}
        
        # Create tasks for parallel execution
        tasks = []
        
        if 'bank_transactions' in data_needed:
            tasks.append(self._fetch_bank_data(sessionid, analysis))
        
        if 'net_worth' in data_needed:
            tasks.append(self._fetch_net_worth(sessionid))
        
        if 'credit_report' in data_needed:
            tasks.append(self._fetch_credit_report(sessionid))
        
        if 'mf_transactions' in data_needed:
            tasks.append(self._fetch_mf_transactions(sessionid))
        
        if 'stock_transactions' in data_needed:
            tasks.append(self._fetch_stock_transactions(sessionid))
        
        if 'goals' in data_needed:
            tasks.append(self._fetch_goals(sessionid))
        
        # Execute all tasks in parallel
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching data: {result}")
                    continue
                    
                if result:
                    context.update(result)
        
        return context
    
    async def _fetch_net_worth(self, sessionid: str) -> Dict[str, Any]:
        """Fetch net worth data."""
        try:
            logger.info(f"Fetching net worth for sessionid: {sessionid}")
            logger.info(f"MCP client type: {type(self.mcp_client)}")
            net_worth = await self.mcp_client.get_net_worth(sessionid)
            logger.info(f"Net worth data received: {net_worth is not None}")
            if net_worth:
                logger.info(f"Net worth keys: {net_worth.keys() if isinstance(net_worth, dict) else 'not a dict'}")
            return {"net_worth": net_worth}
        except Exception as e:
            logger.error(f"Error fetching net worth: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    async def _fetch_credit_report(self, sessionid: str) -> Dict[str, Any]:
        """Fetch credit report data."""
        try:
            credit_report = await self.mcp_client.get_credit_report(sessionid)
            return {"credit_report": credit_report}
        except Exception as e:
            logger.error(f"Error fetching credit report: {e}")
            return {}

    async def _fetch_mf_transactions(self, sessionid: str) -> Dict[str, Any]:
        """Fetch mutual fund transactions."""
        try:
            mf_data = await self.mcp_client.get_mf_transactions(sessionid)
            return {"mf_transactions": mf_data}
        except Exception as e:
            logger.error(f"Error fetching MF transactions: {e}")
            return {}

    async def _fetch_stock_transactions(self, sessionid: str) -> Dict[str, Any]:
        """Fetch stock transactions."""
        try:
            stock_data = await self.mcp_client.get_stock_transactions(sessionid)
            return {"stock_transactions": stock_data}
        except Exception as e:
            logger.error(f"Error fetching stock transactions: {e}")
            return {}
    
    async def _fetch_bank_data(self, sessionid: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch and process bank transaction data based on the analysis.
        """
        try:
            bank_data = await self.mcp_client.get_bank_transactions(sessionid)
            
            if not bank_data or 'transactions' not in bank_data:
                return {"bank_transactions": {"transactions": [], "summary": {}}}
            
            transactions = bank_data['transactions']
            
            # Process transactions based on time period
            time_period = analysis.get('time_period', 'last_month')
                    
            # For demo purposes, use 2024 data
            now = datetime.now()
            if now.year > 2024:
                if time_period == "june_2024":
                    start_date = datetime(2024, 6, 1)
                    end_date = datetime(2024, 6, 30)
                elif time_period == "july_2024":
                    start_date = datetime(2024, 7, 1)
                    end_date = datetime(2024, 7, 31)
                elif time_period == "may_2024":
                    start_date = datetime(2024, 5, 1)
                    end_date = datetime(2024, 5, 31)
                elif time_period == "april_2024":
                    start_date = datetime(2024, 4, 1)
                    end_date = datetime(2024, 4, 30)
                elif time_period == "march_2024":
                    start_date = datetime(2024, 3, 1)
                    end_date = datetime(2024, 3, 31)
                elif time_period == "february_2024":
                    start_date = datetime(2024, 2, 1)
                    end_date = datetime(2024, 2, 29)
                elif time_period == "january_2024":
                    start_date = datetime(2024, 1, 1)
                    end_date = datetime(2024, 1, 31)
                else:
                    # Default to current month
                    start_date = datetime(2024, 7, 1)
                    end_date = datetime(2024, 7, 31)
            else:
                # Use actual current date logic
                if time_period == "last_month":
                    start_date = (now.replace(day=1) - timedelta(days=1)).replace(day=1)
                    end_date = now.replace(day=1) - timedelta(days=1)
                elif time_period == "last_week":
                    start_date = now - timedelta(days=7)
                    end_date = now
                elif time_period == "last_year":
                    start_date = now.replace(month=1, day=1)
                    end_date = now
                else:
                    start_date = now.replace(day=1)
                    end_date = now
            
            # Filter transactions by date
            filtered_transactions = []
            for txn in transactions:
                try:
                    txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                    if start_date <= txn_date <= end_date:
                        filtered_transactions.append(txn)
                except:
                    continue
            
            # Calculate summary statistics
            total_debits = sum(t.get('amount', 0) for t in filtered_transactions if t.get('txn_type') == 'DEBIT')
            total_credits = sum(t.get('amount', 0) for t in filtered_transactions if t.get('txn_type') == 'CREDIT')
            
            # Category-wise spending
            category_spending = {}
            for txn in filtered_transactions:
                if txn.get('txn_type') == 'DEBIT':
                    category = txn.get('category', 'Others')
                    amount = txn.get('amount', 0)
                    category_spending[category] = category_spending.get(category, 0) + amount
            
            summary = {
                "total_debits": total_debits,
                "total_credits": total_credits,
                "net_flow": total_credits - total_debits,
                "transaction_count": len(filtered_transactions),
                "category_spending": category_spending,
                "period": {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d'),
                    "time_period": time_period
                }
            }
            
            return {
                "bank_transactions": {
                    "transactions": filtered_transactions,
                    "summary": summary
                }
            }
            
        except Exception as e:
            logger.error(f"Error fetching bank data: {e}")
            return {"bank_transactions": {"transactions": [], "summary": {}}}
    
    async def _fetch_goals(self, sessionid: str) -> List[Dict[str, Any]]:
        """Fetch user's financial goals."""
        try:
            goals = self.goals_manager.list_goals(sessionid)
            return {"goals": goals}
        except Exception as e:
            logger.error(f"Error fetching goals: {e}")
            return {"goals": {"goals": []}}
    
    def build_focused_prompt(self, query: str, analysis: Dict[str, Any], context: Dict[str, Any], chat_history: List[Dict[str, str]] = None) -> str:
        """
        Build a focused, context-aware prompt for the AI model.
        Enhanced with chat history and stronger instructions.
        """
        intent = analysis.get('intent', 'general')
        time_period = analysis.get('time_period', 'recent')
        
        prompt_lines = [
            "You are Finion, an intelligent financial assistant. You have access to the user's financial data and chat history.",
            "CRITICAL RULES:",
            "1. ALWAYS use ₹ (Indian Rupees) - NEVER use P (Peso) or $ (Dollar)",
            "2. Be specific with numbers and percentages",
            "3. Provide actionable insights based on their actual data",
            "4. Keep responses concise but informative (2-3 sentences max)",
            "5. If user asks for specific month (like 'June 2024'), use that exact period",
            "6. Use the chat history to provide contextual responses",
            "",
            f"USER QUERY: {query}",
            f"QUERY INTENT: {intent}",
            f"TIME PERIOD: {time_period}",
            ""
        ]
        
        # Add chat history context if available
        if chat_history and len(chat_history) > 1:
            prompt_lines.append("CHAT HISTORY CONTEXT:")
            for msg in chat_history[-3:]:  # Last 3 messages
                prompt_lines.append(f"{msg['role'].title()}: {msg['content']}")
            prompt_lines.append("")
        
        # Add financial data context
        if 'bank_transactions' in context:
            bank_data = context['bank_transactions']
            if 'summary' in bank_data:
                summary = bank_data['summary']
                prompt_lines.extend([
                    "FINANCIAL DATA:",
                    f"Total Expenses: ₹{summary.get('total_debits', 0):,.0f}",
                    f"Total Income: ₹{summary.get('total_credits', 0):,.0f}",
                    f"Net Flow: ₹{summary.get('net_flow', 0):,.0f}",
                    f"Transaction Count: {summary.get('transaction_count', 0)}",
                    ""
                ])
                
                # Add category spending if available
                if 'category_spending' in summary and summary['category_spending']:
                    prompt_lines.append("TOP SPENDING CATEGORIES:")
                    sorted_categories = sorted(summary['category_spending'].items(), key=lambda x: x[1], reverse=True)
                    for category, amount in sorted_categories[:5]:
                        prompt_lines.append(f"  {category}: ₹{amount:,.0f}")
                    prompt_lines.append("")
        
        if 'net_worth' in context:
            net_worth_data = context['net_worth']
            if 'netWorthResponse' in net_worth_data:
                net_worth = net_worth_data['netWorthResponse']
                total = net_worth.get('totalNetWorthValue', {})
                if total:
                    value = int(total.get('units', '0'))
                    prompt_lines.extend([
                        "NET WORTH:",
                        f"Total Net Worth: ₹{value:,}",
                        ""
                    ])
        
        if 'goals' in context:
            goals_data = context['goals']
            if 'goals' in goals_data and goals_data['goals']:
                prompt_lines.append("FINANCIAL GOALS:")
                for goal in goals_data['goals'][:3]:  # Top 3 goals
                    progress = (goal.get('current_amount', 0) / goal.get('target_amount', 1)) * 100
                    prompt_lines.append(f"  {goal.get('name', 'Goal')}: ₹{goal.get('current_amount', 0):,.0f} / ₹{goal.get('target_amount', 0):,.0f} ({progress:.1f}%)")
                prompt_lines.append("")
        
        # Add intent-specific instructions
        if intent == "spending_analysis":
            prompt_lines.extend([
                "SPENDING ANALYSIS INSTRUCTIONS:",
                "- Focus on the specific time period requested",
                "- Highlight top spending categories",
                "- Compare with previous periods if relevant",
                "- Suggest specific spending optimizations",
                "- Use exact amounts from their data"
            ])
        elif intent == "travel_planning":
            prompt_lines.extend([
                "TRAVEL PLANNING INSTRUCTIONS:",
                "- Provide realistic budget based on their savings capacity",
                "- Suggest specific spending cuts from their actual expenses",
                "- Create actionable monthly savings plan",
                "- Consider their existing financial commitments"
            ])
        elif intent == "investment_analysis":
            prompt_lines.extend([
                "INVESTMENT ANALYSIS INSTRUCTIONS:",
                "- Analyze portfolio performance",
                "- Suggest diversification opportunities",
                "- Consider their risk profile and goals"
            ])
        
        # Add response format instructions
        prompt_lines.extend([
            "",
            "RESPONSE FORMAT:",
            "1. Direct answer with specific numbers from their data",
            "2. One key insight or comparison",
            "3. One actionable recommendation (if relevant)",
            "",
            "Remember: Be friendly, use their actual data, and keep it concise!"
        ])
        
        return "\n".join(prompt_lines)
    
    def _get_cache_key(self, sessionid: str, query: str, analysis: Dict[str, Any]) -> str:
        """Generate a cache key for the query."""
        # Include sessionid, query, and intent in cache key
        key_data = f"{sessionid}:{query}:{analysis.get('intent', '')}:{analysis.get('time_period', '')}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _check_cache(self, cache_key: str) -> Optional[str]:
        """Check if we have a cached response."""
        if cache_key in self.response_cache:
            cached_data = self.response_cache[cache_key]
            if datetime.now() - cached_data['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached_data['response']
            else:
                # Expired, remove from cache
                del self.response_cache[cache_key]
        return None
    
    def _generate_direct_response(self, query: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate a direct response based on the data when Gemini API is not available.
        """
        intent = analysis.get('intent', 'general')
        
        if intent == "wealth_analysis" and 'net_worth' in context:
            net_worth_data = context['net_worth']
            if 'netWorthResponse' in net_worth_data:
                net_worth = net_worth_data['netWorthResponse']
                total = net_worth.get('totalNetWorthValue', {})
                if total:
                    value = int(total.get('units', '0'))
                    return f"Your current net worth is ₹{value:,}. This includes your mutual funds, EPF, and savings accounts."
        
        elif intent == "spending_analysis" and 'bank_transactions' in context:
            bank_data = context['bank_transactions']
            if 'summary' in bank_data:
                summary = bank_data['summary']
                total_debits = summary.get('total_debits', 0)
                total_credits = summary.get('total_credits', 0)
                period = summary.get('period', {}).get('time_period', 'the period')
                return f"Your total spending in {period} was ₹{total_debits:,.0f} and income was ₹{total_credits:,.0f}."
        
        elif intent == "investment_analysis" and ('mf_transactions' in context or 'stock_transactions' in context):
            return "I can see your investment portfolio data. You have mutual funds and stocks with good diversification."
        
        elif intent == "credit_health" and 'credit_report' in context:
            return "I can access your credit report data. Your credit score and history are available for analysis."
        
        elif intent == "goal_management" and 'goals' in context:
            goals_data = context['goals']
            if 'goals' in goals_data and goals_data['goals']:
                return f"You have {len(goals_data['goals'])} active financial goals. I can help you track your progress."
        
        # Default response
        return f"I can see your financial data for {intent.replace('_', ' ')}. The information is available and ready for analysis."
    
    async def process_query(self, sessionid: str, query: str) -> Dict[str, Any]:
        """
        Main method to process a user query with intelligent data fetching.
        Enhanced with chat history and performance tracking.
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing query: '{query}' for sessionid: {sessionid}")
            
            # Get or create chat session
            chat_session = self._get_or_create_chat_session(sessionid)
            
            # Step 1: Analyze the query (fast pattern matching)
            analysis = await self.analyze_query(query)
            logger.info(f"Query analysis: {analysis}")
            
            # Check cache for common queries
            cache_key = self._get_cache_key(sessionid, query, analysis)
            cached_response = self._check_cache(cache_key)
            
            if cached_response:
                logger.info("Using cached response")
                # Add to chat history
                chat_session.add_message("user", query)
                chat_session.add_message("assistant", cached_response)
                
                return {
                    "response": cached_response,
                    "analysis": analysis,
                    "data_used": analysis.get('data_needed', []),
                    "cached": True,
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Step 2: Fetch only relevant data (parallel processing)
            context = await self.fetch_relevant_data(sessionid, analysis)
            
            # Step 3: Get chat history for context
            chat_history = chat_session.get_recent_context(max_messages=6)
            
            # Step 4: Build focused prompt with chat history
            prompt = self.build_focused_prompt(query, analysis, context, chat_history)
            
            # Step 5: Generate response
            try:
                response = self.model.generate_content(prompt)
                response_text = response.text
            except Exception as e:
                logger.warning(f"Gemini API error: {e}")
                # If Gemini API fails, generate a direct response based on the data
                response_text = self._generate_direct_response(query, analysis, context)
            
            # Step 6: Add to chat history
            chat_session.add_message("user", query)
            chat_session.add_message("assistant", response_text)
            
            # Step 7: Cache the response
            self.response_cache[cache_key] = {
                'response': response_text,
                'timestamp': datetime.now()
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Track performance
            self.query_times[analysis.get('intent', 'unknown')] = processing_time
            
            return {
                "response": response_text,
                "analysis": analysis,
                "data_used": list(context.keys()),
                "processing_time": processing_time,
                "chat_context_used": len(chat_history) > 0
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            logger.error(f"Exception type: {type(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Add fallback response instead of generic error
            return {
                "response": "I'm having trouble accessing your financial data right now. Please try again in a moment.",
                "fallback": True,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }

# Create singleton instance
smart_assistant = None

def get_smart_assistant(mcp_client, goals_manager):
    """Get or create the smart assistant instance."""
    global smart_assistant
    if smart_assistant is None:
        smart_assistant = SmartFinanceAssistant(mcp_client, goals_manager)
    return smart_assistant 