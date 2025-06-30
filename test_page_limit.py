#!/usr/bin/env python3
"""
Test script to demonstrate the 10-page limit functionality
"""

from markets_api import get_all_markets

def test_page_limit():
    """Test the 10-page limit functionality"""
    
    print("Testing markets API with 10-page limit:")
    print("-" * 60)
    
    try:
        # Call the markets API with default settings (10-page limit)
        markets = get_all_markets()
        
        print(f"\nResults:")
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
            
    except Exception as e:
        print(f"Error: {e}")

def test_custom_page_limit():
    """Test with a custom page limit"""
    
    print("\nTesting markets API with 3-page limit:")
    print("-" * 60)
    
    try:
        # Call the markets API with a 3-page limit
        markets = get_all_markets(max_pages=3)
        
        print(f"\nResults:")
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
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_page_limit()
    test_custom_page_limit() 