#!/usr/bin/env python3
"""
Demo script for celebrity comparison feature.
"""
import asyncio
import httpx
import json
from datetime import datetime

async def demo_celebrity_comparison():
    """Demo the celebrity comparison feature."""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    # Demo session ID
    session_id = "demo_session_123"
    
    # Celebrities to compare with
    celebrities = [
        "Shah Rukh Khan",
        "Jeff Bezos", 
        "Elon Musk",
        "Amitabh Bachchan",
        "Ratan Tata"
    ]
    
    print("🎬 Celebrity Comparison Demo")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        for celebrity in celebrities:
            print(f"\n🔍 Comparing with: {celebrity}")
            print("-" * 30)
            
            try:
                # Make API call
                response = await client.post(
                    f"{base_url}/api/celebrity-comparison",
                    headers={
                        "Content-Type": "application/json",
                        "Cookie": f"sessionid={session_id}"
                    },
                    json={
                        "celebrity_name": celebrity,
                        "comparison_type": "all"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Display results
                    user_data = data["user_data"]
                    celebrity_data = data["celebrity_data"]
                    comparison = data["comparison"]
                    
                    print(f"👤 Your Financial Status:")
                    print(f"   Net Worth: ₹{user_data['net_worth']:,}")
                    print(f"   Monthly Income: ₹{user_data['monthly_income']:,}")
                    print(f"   Investments: ₹{user_data['investments']:,}")
                    print(f"   Real Estate: ₹{user_data['real_estate']:,}")
                    
                    print(f"\n⭐ {celebrity_data['name']}'s Financial Status:")
                    print(f"   Net Worth: ₹{celebrity_data['net_worth']:,}")
                    print(f"   Monthly Income: ₹{celebrity_data['monthly_income']:,}")
                    print(f"   Investments: ₹{celebrity_data['investments']:,}")
                    print(f"   Real Estate: ₹{celebrity_data['real_estate']:,}")
                    print(f"   Income Sources: {', '.join(celebrity_data['primary_income_sources'])}")
                    print(f"   Data Source: {celebrity_data['data_source']}")
                    
                    print(f"\n📊 Comparison:")
                    print(f"   Net Worth: {comparison['net_worth_percentage']:.6f}%")
                    print(f"   Income: {comparison['income_percentage']:.6f}%")
                    print(f"   Investments: {comparison['investment_percentage']:.6f}%")
                    print(f"   Real Estate: {comparison['real_estate_percentage']:.6f}%")
                    
                    print(f"\n💬 {comparison['motivational_message']}")
                    print(f"🎯 {comparison['achievement_insight']}")
                    print(f"🚀 Next Milestone: {comparison['next_milestone']}")
                    
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error comparing with {celebrity}: {str(e)}")
            
            # Small delay between requests
            await asyncio.sleep(1)
    
    print(f"\n✅ Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    print("Starting Celebrity Comparison Demo...")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    asyncio.run(demo_celebrity_comparison()) 