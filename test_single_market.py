#!/usr/bin/env python3
"""
Test script to examine the structure of a single market response
"""

from kalshi_api_client import call_kalshi_api
import json

def test_single_market_response():
    """Test a single markets API call to examine the response structure"""
    
    try:
        # Make a single API call with limit=1 to get just one market
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/markets",
            params={"limit": "1"}
        )
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", [])
            
            print(f"API Response Status: {response.status_code}")
            print(f"Number of markets returned: {len(markets)}")
            print(f"Cursor: {data.get('cursor')}")
            print("-" * 60)
            
            if markets:
                market = markets[0]
                print("First market structure:")
                print(json.dumps(market, indent=2))
                
                print("\nAvailable fields:")
                for key, value in market.items():
                    print(f"  {key}: {type(value).__name__} = {value}")
            else:
                print("No markets returned")
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_single_market_response() 