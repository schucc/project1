#!/usr/bin/env python3
"""
Test script to debug series_ticker filter issue
"""

from markets_api import get_all_markets
import json

def test_series_ticker_filter():
    """Test the series_ticker filter with a known series"""
    
    # Test with the series ticker from the error message
    series_ticker = "KXCORIVER"
    
    print(f"Testing markets API with series_ticker: {series_ticker}")
    print("-" * 60)
    
    try:
        # Call the markets API with series_ticker filter
        markets = get_all_markets(series_ticker=series_ticker)
        
        print(f"Results:")
        print(f"Total markets found: {len(markets)}")
        
        if markets:
            print(f"\nFirst 3 markets:")
            for i, market in enumerate(markets[:3]):
                ticker = market.get('ticker', 'N/A')
                event_ticker = market.get('event_ticker', 'N/A')
                status = market.get('status', 'N/A')
                
                print(f"  {i+1}. {ticker}")
                print(f"     Event: {event_ticker}")
                print(f"     Status: {status}")
                print()
        else:
            print("No markets found.")
            
            # Let's also test without any filters to see if the API is working
            print("\nTesting without filters to see if API is working:")
            all_markets = get_all_markets()
            print(f"Total markets without filters: {len(all_markets)}")
            
            if all_markets:
                # Look for markets that might be related to the series
                related_markets = []
                for market in all_markets:
                    ticker = market.get('ticker', '')
                    if 'CORIVER' in ticker or 'LAKE' in ticker.upper() or 'MEAD' in ticker.upper():
                        related_markets.append(market)
                
                print(f"\nFound {len(related_markets)} potentially related markets:")
                for market in related_markets[:5]:
                    print(f"  - {market.get('ticker')} (Event: {market.get('event_ticker')})")
            
    except Exception as e:
        print(f"Error: {e}")

def test_api_parameters():
    """Test what parameters are actually being sent to the API"""
    
    from kalshi_api_client import call_kalshi_api
    
    series_ticker = "KXCORIVER"
    
    print(f"Testing API call parameters for series_ticker: {series_ticker}")
    print("-" * 60)
    
    try:
        # Build query parameters
        params = {"limit": "1000", "series_ticker": series_ticker}
        
        print(f"Query parameters: {params}")
        
        # Make API call
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/markets",
            params=params
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            markets = data.get("markets", [])
            print(f"Markets returned: {len(markets)}")
            
            if markets:
                print("First market:")
                print(json.dumps(markets[0], indent=2))
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== TEST 1: Series ticker filter ===")
    test_series_ticker_filter()
    
    print("\n" + "="*80 + "\n")
    
    print("=== TEST 2: API parameters ===")
    test_api_parameters() 