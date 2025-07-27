"""
Data processor for analyzing financial transactions and generating insights.
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import json
import re

class TransactionProcessor:
    """Process and analyze transaction data from MCP."""
    
    # Category mappings
    CATEGORY_MAPPINGS = {
        'GROCERIES': 'Groceries',
        'DINING': 'Dining',
        'CREDIT CARD': 'Credit Card Payment',
        'BILL PAYMENT': 'Bills',
        'BILLPAY': 'Bills',
        'MUTUAL FUND': 'Investment',
        'LUMPSUM INV': 'Investment',
        'SIP': 'Investment',
        'ZERODHA': 'Investment',
        'GOLD ETF': 'Investment',
        'RD': 'Savings',
        'FD': 'Savings',
        'FIXED DEPOSIT': 'Savings',
        'NEFT': 'Transfer',
        'IMPS': 'Transfer',
        'UPI': 'Shopping',
        'EMI': 'Loan',
        'INSTALLMENT': 'Loan',
        # New autopay-eligible categories
        'NETFLIX': 'Streaming',
        'SONYLIV': 'Streaming',
        'HOTSTAR': 'Streaming',
        'AMAZON PRIME': 'Streaming',
        'SPOTIFY': 'Streaming',
        'YOUTUBE': 'Streaming',
        'ACT BROADBAND': 'Internet',
        'AIRTEL': 'Telecom',
        'JIO': 'Telecom',
        'VODAFONE': 'Telecom',
        'TATASKY': 'DTH',
        'DISHTV': 'DTH',
        'INSURANCE': 'Insurance',
        'LIC': 'Insurance',
        'POLICY': 'Insurance',
        # Credit card payments
        'CARD_PAYMENT': 'Credit Card Payment',
        'AMEX': 'Credit Card Payment',
        'HDFC CREDIT CARD': 'Credit Card Payment',
        'ICICI CREDIT CARD': 'Credit Card Payment',
        'SBI CARD': 'Credit Card Payment',
        # Housing
        'RENT': 'Housing'
    }
    
    # Categories eligible for autopay nudges
    AUTOPAY_CATEGORIES = [
        'Housing',           # Rent
        'Utilities',         # Electricity, Water
        'Streaming',         # Netflix, Prime, etc.
        'Internet',          # Broadband
        'Telecom',           # Mobile bills
        'DTH',              # TV subscriptions
        'Insurance',         # Insurance premiums
        'Loan',             # EMI payments
        'Investment',        # SIP investments
        'Savings',          # RD installments
        'Credit Card Payment'  # Credit card bills
    ]
    
    @staticmethod
    def categorize_transaction(narration: str, merchant: str = "") -> str:
        """Categorize a transaction based on narration and merchant."""
        combined = f"{narration} {merchant}".upper()
        
        # Priority order: Check specific services/merchants first
        priority_keywords = [
            # Streaming services
            'NETFLIX', 'SONYLIV', 'HOTSTAR', 'AMAZON PRIME', 'SPOTIFY', 'YOUTUBE',
            # Utilities and services
            'ACT BROADBAND', 'AIRTEL', 'JIO', 'VODAFONE', 'TATASKY', 'DISHTV',
            # Insurance
            'INSURANCE', 'LIC', 'POLICY',
            # Credit cards
            'CARD_PAYMENT', 'AMEX', 'HDFC CREDIT CARD', 'ICICI CREDIT CARD', 'SBI CARD',
            # Investments
            'SIP', 'MUTUAL FUND', 'LUMPSUM INV', 'ZERODHA', 'GOLD ETF',
            # Savings
            'RD', 'FD', 'FIXED DEPOSIT',
            # Loans
            'EMI', 'INSTALLMENT',
            # Housing
            'RENT'
        ]
        
        # Check priority keywords first
        for keyword in priority_keywords:
            if keyword in combined:
                return TransactionProcessor.CATEGORY_MAPPINGS.get(keyword, 'Others')
        
        # Then check remaining mappings
        for keyword, category in TransactionProcessor.CATEGORY_MAPPINGS.items():
            if keyword in combined:
                return category
        
        return "Others"
    
    @staticmethod
    def parse_bank_transactions(bank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse bank transactions into normalized format."""
        transactions = []
        
        if 'bankTransactions' not in bank_data:
            return transactions
            
        for bank in bank_data.get('bankTransactions', []):
            bank_name = bank.get('bank', 'Unknown Bank')
            
            for txn in bank.get('txns', []):
                # txn format: [amount, narration, date, type, mode, balance]
                if len(txn) >= 6:
                    amount = float(txn[0])
                    narration = txn[1]
                    date_str = txn[2]
                    txn_type = int(txn[3])  # 1=CREDIT, 2=DEBIT
                    mode = txn[4]
                    balance = float(txn[5])
                    
                    # Categorize transaction using both narration and mode
                    category = TransactionProcessor.categorize_transaction(narration, mode)
                    
                    transactions.append({
                        'amount': amount,
                        'narration': narration,
                        'date': date_str,
                        'txn_type': 'CREDIT' if txn_type == 1 else 'DEBIT',
                        'mode': mode,
                        'balance': balance,
                        'category': category,
                        'bank': bank_name
                    })
        
        return transactions
    
    @staticmethod
    def parse_mf_transactions(mf_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse mutual fund transactions into normalized format."""
        transactions = []
        
        # MF data structure varies, this is a basic parser
        # You might need to adjust based on actual data structure
        if isinstance(mf_data, dict):
            # Extract any transaction-like data
            # For now, return empty as the structure needs investigation
            pass
            
        return transactions
    
    @staticmethod
    def parse_stock_transactions(stock_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse stock transactions into normalized format."""
        transactions = []
        
        # Stock data structure varies, this is a basic parser
        if isinstance(stock_data, dict):
            # Extract any transaction-like data
            pass
            
        return transactions
    
    @staticmethod
    def merge_all_transactions(bank_data: Dict, mf_data: Dict, stock_data: Dict) -> List[Dict]:
        """Merge all transaction types into a unified list."""
        all_txns = []
        
        # Parse each type
        bank_txns = TransactionProcessor.parse_bank_transactions(bank_data)
        mf_txns = TransactionProcessor.parse_mf_transactions(mf_data)
        stock_txns = TransactionProcessor.parse_stock_transactions(stock_data)
        
        # Add unique IDs to bank transactions
        for i, txn in enumerate(bank_txns):
            txn['id'] = f"bank_{i}_{hash(txn['narration'] + str(txn['amount']) + txn['date'])}"
            txn['source'] = 'bank'
            all_txns.append(txn)
        
        # Add unique IDs to MF transactions
        for i, txn in enumerate(mf_txns):
            txn['id'] = f"mf_{i}_{hash(txn.get('narration', '') + str(txn.get('amount', 0)) + txn.get('date', ''))}"
            txn['source'] = 'mutual_fund'
            all_txns.append(txn)
        
        # Add unique IDs to stock transactions
        for i, txn in enumerate(stock_txns):
            txn['id'] = f"stock_{i}_{hash(txn.get('narration', '') + str(txn.get('amount', 0)) + txn.get('date', ''))}"
            txn['source'] = 'stock'
            all_txns.append(txn)
        
        # Sort by date descending
        all_txns.sort(key=lambda x: x['date'], reverse=True)
        
        return all_txns
    
    @staticmethod
    def get_payment_nudges(bank_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate payment nudges from recurring transactions."""
        transactions = TransactionProcessor.parse_bank_transactions(bank_data)
        
        # Find recurring debits in autopay categories
        recurring_patterns = defaultdict(list)
        
        for txn in transactions:
            # Look for DEBIT transactions in autopay categories
            if txn['txn_type'] == 'DEBIT' and txn['category'] in TransactionProcessor.AUTOPAY_CATEGORIES:
                
                # Extract a clean description for grouping
                narration = txn['narration'].upper()
                
                # Special handling for different types
                if txn['category'] == 'Investment' and 'SIP' in narration:
                    # Extract fund name from SIP transactions
                    if 'KOTAKMF' in narration:
                        key = ('Kotak MF SIP', int(txn['amount']))
                    elif 'ADITYABIRLAMF' in narration:
                        key = ('Aditya Birla MF SIP', int(txn['amount']))
                    elif 'ICICIPRUMF' in narration:
                        key = ('ICICI Pru MF SIP', int(txn['amount']))
                    elif 'HDFCMF' in narration:
                        key = ('HDFC MF SIP', int(txn['amount']))
                    else:
                        key = ('SIP Investment', int(txn['amount']))
                elif txn['category'] == 'Streaming':
                    # Group streaming services by name
                    service = 'Streaming Service'
                    for svc in ['NETFLIX', 'SONYLIV', 'HOTSTAR', 'SPOTIFY', 'AMAZON PRIME', 'YOUTUBE']:
                        if svc in narration:
                            service = svc.title()
                            break
                    key = (service, int(txn['amount']))
                elif txn['category'] == 'Internet' and 'ACT BROADBAND' in narration:
                    key = ('ACT Broadband', int(txn['amount']))
                elif txn['category'] == 'Loan' and 'EMI' in narration:
                    key = ('EMI Payment', int(txn['amount']))
                elif txn['category'] == 'Savings' and 'RD' in narration:
                    key = ('RD Installment', int(txn['amount']))
                elif txn['category'] == 'Housing' and 'RENT' in narration:
                    key = ('Rent', int(txn['amount']))
                elif txn['category'] == 'Credit Card Payment':
                    # Extract card info
                    if 'AMEX' in narration:
                        key = ('AMEX Card Payment', int(txn['amount']))
                    else:
                        key = ('Credit Card Payment', int(txn['amount']))
                else:
                    # Group by category and amount (rounded to nearest 100)
                    amount_key = int(txn['amount'] / 100) * 100
                    key = (txn['category'], amount_key)
                
                recurring_patterns[key].append(txn)
        
        nudges = []
        current_date = datetime.now()
        
        # Track which categories we've already added
        added_categories = set()
        
        # Sort patterns by transaction count (most frequent first) and amount (highest first)
        sorted_patterns = sorted(recurring_patterns.items(), 
                               key=lambda x: (len(x[1]), x[0][1]), 
                               reverse=True)
        
        for (description, amount), txns in sorted_patterns:
            # Determine the broader category for deduplication
            if 'SIP' in description:
                category_key = 'SIP'
            elif 'Card Payment' in description:
                category_key = 'CreditCard'
            elif 'Rent' in description:
                category_key = 'Rent'
            elif 'EMI' in description:
                category_key = 'EMI'
            elif 'RD' in description:
                category_key = 'RD'
            else:
                category_key = description.split()[0] if ' ' in description else description
            
            # Skip if we already have a nudge for this category
            if category_key in added_categories:
                continue
                
            # Get the latest transaction
            latest = max(txns, key=lambda x: x['date'])
            latest_date = datetime.strptime(latest['date'], '%Y-%m-%d')
            
            # For demo: Calculate next due date
            # For future dates (test data), use current date + cycle
            if latest_date > current_date:
                # Test data is in future, calculate from current date
                if 'SIP' in description or 'RD' in description:
                    next_due = current_date + timedelta(days=30)  # Monthly
                elif 'EMI' in description or 'Rent' in description:
                    next_due = current_date + timedelta(days=30)  # Monthly
                elif description in ['Netflix', 'Sonyliv', 'ACT Broadband', 'Spotify', 'Youtube']:
                    next_due = current_date + timedelta(days=30)  # Monthly
                else:
                    next_due = current_date + timedelta(days=30)
            else:
                # Normal calculation for past dates
                days_since = (current_date - latest_date).days
                if days_since > 25:
                    next_due = current_date + timedelta(days=5)
                else:
                    next_due = latest_date + timedelta(days=30)
            
            # Create nudge with clean description
            nudges.append({
                'category': description,
                'amount': amount,
                'due': next_due.strftime('%Y-%m-%d'),
                'last_paid': latest['date'],
                'merchant': latest.get('narration', '')[:50],  # First 50 chars
                'autopay_eligible': True
            })
            
            # Mark this category as added
            added_categories.add(category_key)
        
        # Sort by due date
        nudges.sort(key=lambda x: x['due'])
        return nudges
    
    @staticmethod
    def calculate_daily_spend(transactions: List[Dict], from_date: str, to_date: str) -> List[Dict]:
        """Calculate daily spend aggregates."""
        daily_spend = defaultdict(float)
        
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')
        
        for txn in transactions:
            if txn['txn_type'] == 'DEBIT':
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if from_dt <= txn_date <= to_dt:
                    date_key = txn['date']
                    daily_spend[date_key] += txn['amount']
        
        # Convert to list format
        result = []
        current = from_dt
        while current <= to_dt:
            date_str = current.strftime('%Y-%m-%d')
            result.append({
                'date': date_str,
                'amount': daily_spend.get(date_str, 0)
            })
            current += timedelta(days=1)
        
        return result
    
    @staticmethod
    def calculate_monthly_spend(transactions: List[Dict], from_date: str, to_date: str) -> List[Dict]:
        """Calculate monthly spend aggregates."""
        monthly_spend = defaultdict(float)
        
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')
        
        for txn in transactions:
            if txn['txn_type'] == 'DEBIT':
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if from_dt <= txn_date <= to_dt:
                    month_key = txn_date.strftime('%Y-%m')
                    monthly_spend[month_key] += txn['amount']
        
        # Convert to list format
        result = []
        for month, amount in sorted(monthly_spend.items()):
            result.append({
                'month': month,
                'amount': amount
            })
        
        return result
    
    @staticmethod
    def calculate_category_breakdown(transactions: List[Dict], from_date: str, to_date: str) -> Dict[str, Any]:
        """Calculate spending breakdown by category."""
        category_spend = defaultdict(float)
        total_spend = 0
        
        from_dt = datetime.strptime(from_date, '%Y-%m-%d')
        to_dt = datetime.strptime(to_date, '%Y-%m-%d')
        
        for txn in transactions:
            if txn['txn_type'] == 'DEBIT':
                txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
                if from_dt <= txn_date <= to_dt:
                    category_spend[txn['category']] += txn['amount']
                    total_spend += txn['amount']
        
        # Calculate percentages
        breakdown = []
        for category, amount in sorted(category_spend.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spend * 100) if total_spend > 0 else 0
            breakdown.append({
                'category': category,
                'amount': amount,
                'percentage': round(percentage, 2)
            })
        
        return {
            'total': total_spend,
            'breakdown': breakdown
        }
    
    @staticmethod
    def whatif_simulator(scenario: str, **kwargs) -> Dict[str, Any]:
        """Simple what-if financial simulator."""
        if scenario == 'mf_return':
            # Simple MF return calculation at 12% p.a.
            amount = kwargs.get('amount', 0)
            months = kwargs.get('horizon_months', 12)
            annual_rate = kwargs.get('annual_rate', 0.12)
            
            monthly_rate = annual_rate / 12
            final_value = amount * ((1 + monthly_rate) ** months)
            returns = final_value - amount
            
            return {
                'scenario': 'mf_return',
                'initial_amount': amount,
                'horizon_months': months,
                'annual_rate_percent': annual_rate * 100,
                'projected_value': round(final_value, 2),
                'projected_returns': round(returns, 2)
            }
            
        elif scenario == 'spend_reduction':
            # Calculate potential savings from spend reduction
            percent = kwargs.get('percent', 10)
            monthly_spend = kwargs.get('avg_monthly_spend', 50000)  # Default
            
            monthly_savings = monthly_spend * (percent / 100)
            annual_savings = monthly_savings * 12
            
            return {
                'scenario': 'spend_reduction',
                'reduction_percent': percent,
                'current_monthly_spend': monthly_spend,
                'monthly_savings': round(monthly_savings, 2),
                'annual_savings': round(annual_savings, 2)
            }
        
        return {'error': 'Unknown scenario'} 