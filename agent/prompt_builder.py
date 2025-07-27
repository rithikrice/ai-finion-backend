# agent/prompt_builder.py
"""
Prompt builder for the Finance AI Agent.
"""
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

def build_system_prompt() -> str:
    """
    Build the system prompt for the AI agent.
    Reads from the template file if available.
    """
    template_path = Path("templates/system_prompt.txt")
    
    if template_path.exists():
        with open(template_path, 'r') as f:
            base_prompt = f.read().strip()
    else:
        base_prompt = """You are Finion, a personal-finance AI assistant. 
Incorporate the user's net worth, transactions, credit report, EPF, mutual funds, bank and stock data 
when answering. Be concise, actionable, and friendly."""
    
    # Add context about available data
    context_info = """

You have access to the following user financial data:
- Net Worth: Total assets and liabilities breakdown
- Bank Transactions: Detailed transaction history with categories
- Credit Report: Credit score and history
- EPF Details: Employee Provident Fund balance and contributions
- Mutual Fund Transactions: Investment portfolio and performance
- Stock Transactions: Stock portfolio and trading history
- Spending Analysis: Daily/monthly spend patterns and category breakdowns
- Financial Goals: User's savings goals and progress tracking

Always provide personalized advice based on the actual data available.
When discussing spending, reference specific categories and amounts.
When discussing investments, mention actual holdings and performance.
Be specific with numbers and dates when available.
"""
    
    return base_prompt + context_info

def build_prompt(user_prompt: str, context: dict) -> str:
    """
    Enhanced prompt builder that includes comprehensive financial analysis.
    Structures data for optimal AI understanding and response generation.
    """
    lines = [build_system_prompt()]
    
    if context:
        lines.append("\n=== COMPREHENSIVE FINANCIAL PROFILE ===")
        
        # 1. Financial Overview
        lines.append("\n## FINANCIAL OVERVIEW")
        
        # Net worth summary
        if 'net_worth' in context:
            net_worth_data = context['net_worth']
            if 'netWorthResponse' in net_worth_data:
                nw_response = net_worth_data['netWorthResponse']
                total = nw_response.get('totalNetWorthValue', {})
                if total:
                    total_value = int(total.get('units', '0'))
                    lines.append(f"Total Net Worth: ₹{total_value:,}")
                
                # Asset breakdown
                if 'assetValue' in nw_response:
                    assets = nw_response['assetValue']
                    asset_value = int(assets.get('units', '0'))
                    lines.append(f"Total Assets: ₹{asset_value:,}")
                
                # Liability breakdown
                if 'liabilityValue' in nw_response:
                    liabilities = nw_response['liabilityValue']
                    liability_value = int(liabilities.get('units', '0'))
                    lines.append(f"Total Liabilities: ₹{liability_value:,}")
        
        # 2. Cash Flow Analysis
        lines.append("\n## CASH FLOW ANALYSIS")
        
        # Monthly spending
        if 'spending_summary' in context:
            spend_data = context['spending_summary']
            lines.append(f"Average Monthly Spending: ₹{spend_data.get('monthly_avg', '0'):,.2f}")
            
            if 'top_categories' in spend_data:
                lines.append("Top Spending Categories:")
                for cat in spend_data['top_categories'][:5]:
                    lines.append(f"  - {cat['category']}: ₹{cat['amount']:,.2f} ({cat['percentage']}%)")
        
        # Average daily spend
        if 'avg_daily_spend' in context:
            lines.append(f"Average Daily Spend (last 30 days): ₹{context['avg_daily_spend']:,.2f}")
        
        # 3. Upcoming Obligations
        if 'upcoming_payments' in context:
            lines.append("\n## UPCOMING PAYMENTS")
            for payment in context['upcoming_payments']:
                amount = int(payment['amount'])
                lines.append(f"  - {payment['category']}: ₹{amount:,} due {payment['due']}")
        
        # 4. Investment Portfolio
        lines.append("\n## INVESTMENT PORTFOLIO")
        
        # Mutual Funds
        if 'mf_transactions' in context:
            mf_data = context['mf_transactions']
            if 'mfTransactions' in mf_data:
                mf_count = len(mf_data['mfTransactions'])
                lines.append(f"Mutual Fund Holdings: {mf_count} funds")
        
        # Stocks
        if 'stock_transactions' in context:
            stock_data = context['stock_transactions']
            if 'stockTransactions' in stock_data:
                stock_count = len(stock_data['stockTransactions'])
                lines.append(f"Stock Holdings: {stock_count} securities")
        
        # EPF
        if 'epf_details' in context:
            epf_data = context['epf_details']
            if 'epfDetailsResponse' in epf_data:
                details = epf_data['epfDetailsResponse'].get('epfDetails', [])
                if details and 'balance' in details[0]:
                    balance = details[0]['balance']
                    current_balance = balance.get('current_pf_balance', '0')
                    lines.append(f"EPF Balance: ₹{current_balance}")
        
        # 5. Credit Profile
        if 'credit_report' in context:
            lines.append("\n## CREDIT PROFILE")
            credit_data = context['credit_report']
            if 'creditReportResponse' in credit_data:
                report = credit_data['creditReportResponse']
                if 'scoreInformation' in report:
                    score_info = report['scoreInformation']
                    score = score_info.get('score', 'N/A')
                    lines.append(f"Credit Score: {score}")
        
        # 6. Financial Goals
        if 'goals' in context and context['goals']:
            lines.append("\n## FINANCIAL GOALS")
            lines.append(f"Active Goals: {len(context['goals'])}")
            for goal in context['goals'][:5]:
                progress = goal.get('progress_percentage', 0)
                current = int(goal['current_amount'])
                target = int(goal['target_amount'])
                lines.append(f"  - {goal['name']}: ₹{current:,}/₹{target:,} ({progress}% complete)")
                if 'monthly_contribution' in goal:
                    monthly = int(goal['monthly_contribution'])
                    lines.append(f"    Monthly contribution: ₹{monthly:,}")
        
        # 7. Recent Large Transactions
        if 'recent_large_transactions' in context:
            lines.append("\n## RECENT LARGE TRANSACTIONS")
            for txn in context['recent_large_transactions'][:5]:
                lines.append(f"  - {txn['date']}: {txn['narration'][:50]} - ₹{txn['amount']:,.2f}")
        
        # 8. Key Financial Ratios
        lines.append("\n## KEY FINANCIAL METRICS")
        
        # Calculate savings rate if possible
        if 'spending_summary' in context and 'bank_transactions' in context:
            try:
                # Rough calculation - would need income data for accuracy
                monthly_spend = context['spending_summary'].get('monthly_avg', 0)
                if monthly_spend > 0:
                    lines.append(f"Note: Income data needed for savings rate calculation")
            except:
                pass
        
        # Add raw data for reference (limited)
        lines.append("\n## RAW DATA AVAILABLE")
        for key in context.keys():
            if key not in ['spending_summary', 'goals', 'upcoming_payments', 'avg_daily_spend', 'recent_large_transactions']:
                lines.append(f"- {key.replace('_', ' ').title()}")
    
    lines.append(f"\n## USER QUERY\n{user_prompt}\n")
    lines.append("\n## RESPONSE GUIDELINES")
    lines.append("- Use specific numbers from the data provided")
    lines.append("- Provide actionable recommendations")
    lines.append("- Explain financial concepts clearly")
    lines.append("- Identify opportunities and risks")
    
    return "\n".join(lines)

def build_prompt_mobile(user_prompt: str, context: dict) -> str:
    """
    Mobile-optimized prompt builder - concise and focused.
    """
    lines = [build_system_prompt()]
    
    if context:
        lines.append("\n=== USER FINANCIAL SNAPSHOT ===")
        
        # Only key metrics
        if 'net_worth' in context:
            net_worth_data = context['net_worth']
            if 'netWorthResponse' in net_worth_data:
                nw_response = net_worth_data['netWorthResponse']
                total = nw_response.get('totalNetWorthValue', {})
                if total:
                    total_value = int(total.get('units', '0'))
                    lines.append(f"Net Worth: ₹{total_value:,}")
        
        # Quick spending summary
        if 'spending_summary' in context:
            spend_data = context['spending_summary']
            monthly_avg = spend_data.get('monthly_avg', 0)
            if monthly_avg > 0:
                lines.append(f"Monthly Spend: ₹{int(monthly_avg):,}")
                
                # Top 2 categories only
                if 'top_categories' in spend_data and spend_data['top_categories']:
                    top_cats = spend_data['top_categories'][:2]
                    cats_str = ", ".join([f"{cat['category']} ({cat['percentage']}%)" for cat in top_cats])
                    lines.append(f"Top Categories: {cats_str}")
        
        # Next payment only
        if 'upcoming_payments' in context and context['upcoming_payments']:
            next_payment = context['upcoming_payments'][0]
            amount = int(next_payment['amount'])
            lines.append(f"Next Payment: {next_payment['category']} - ₹{amount:,} on {next_payment['due']}")
        
        # Credit score if available
        if 'credit_report' in context:
            credit_data = context['credit_report']
            if 'creditReportResponse' in credit_data:
                report = credit_data['creditReportResponse']
                if 'scoreInformation' in report:
                    score = report['scoreInformation'].get('score', 'N/A')
                    if score != 'N/A':
                        lines.append(f"Credit Score: {score}")
        
        # Active goals count
        if 'goals' in context and context['goals']:
            lines.append(f"Active Goals: {len(context['goals'])}")
            # Show closest goal to completion
            if context['goals']:
                closest_goal = max(context['goals'], key=lambda x: x.get('progress_percentage', 0))
                if closest_goal['progress_percentage'] > 0:
                    lines.append(f"Closest Goal: {closest_goal['name']} ({closest_goal['progress_percentage']}% done)")
        
        # Key insights
        if 'recent_large_transactions' in context and context['recent_large_transactions']:
            largest = context['recent_large_transactions'][0]
            lines.append(f"Recent Large Expense: ₹{int(largest['amount']):,} - {largest['narration'][:30]}")
    
    lines.append(f"\n=== USER QUESTION ===\n{user_prompt}")
    lines.append("\nREMEMBER: Keep response concise and mobile-friendly!")
    
    return "\n".join(lines)

async def build_enhanced_context(sessionid: str, mcp_client, goals_manager=None) -> Dict[str, Any]:
    """
    Build enhanced context with spending analysis and goals.
    """
    from data_processor import TransactionProcessor
    
    context = {}
    
    # Fetch all MCP data
    try:
        context['net_worth'] = await mcp_client.get_net_worth(sessionid)
    except:
        pass
    
    try:
        context['credit_report'] = await mcp_client.get_credit_report(sessionid)
    except:
        pass
    
    try:
        context['epf_details'] = await mcp_client.get_epf_details(sessionid)
    except:
        pass
    
    try:
        context['mf_transactions'] = await mcp_client.get_mf_transactions(sessionid)
    except:
        pass
    
    try:
        bank_data = await mcp_client.get_bank_transactions(sessionid)
        context['bank_transactions'] = bank_data
        
        # Calculate spending summary
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        if transactions:
            # Last 30 days spending
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            monthly_spend = TransactionProcessor.calculate_monthly_spend(
                transactions,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            category_breakdown = TransactionProcessor.calculate_category_breakdown(
                transactions,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            context['spending_summary'] = {
                'monthly_avg': sum(m['amount'] for m in monthly_spend) / max(len(monthly_spend), 1),
                'top_categories': category_breakdown.get('breakdown', [])[:5]
            }
    except:
        pass
    
    try:
        context['stock_transactions'] = await mcp_client.get_stock_transactions(sessionid)
    except:
        pass
    
    # Add goals if available
    if goals_manager:
        try:
            goals = goals_manager.list_goals(sessionid)
            if goals:
                # Add progress info to each goal
                goals_with_progress = []
                for goal in goals[:5]:  # Limit to 5 goals
                    progress = goals_manager.calculate_goal_progress(goal)
                    goal['progress_percentage'] = progress['progress_percentage']
                    goals_with_progress.append(goal)
                context['goals'] = goals_with_progress
        except:
            pass
    
    return context
