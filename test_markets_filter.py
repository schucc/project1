#!/usr/bin/env python3
"""
Test script for markets API with date filters
"""

import datetime
from markets_api import get_all_markets

def test_markets_with_date_filters():
    """Test markets API with yesterday and tomorrow as close timestamp filters"""
    
    # Calculate yesterday and tomorrow timestamps
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    tomorrow = today + datetime.timedelta(days=1)
    
    # Convert to Unix timestamps
    min_close_ts = int(yesterday.timestamp())
    max_close_ts = int(tomorrow.timestamp())
    
    print(f"Testing markets API with date filters:")
    print(f"Yesterday: {yesterday.strftime('%Y-%m-%d %H:%M:%S')} (timestamp: {min_close_ts})")
    print(f"Tomorrow: {tomorrow.strftime('%Y-%m-%d %H:%M:%S')} (timestamp: {max_close_ts})")
    print("-" * 60)
    
    try:
        # Call the markets API with date filters
        markets = get_all_markets(
            min_close_ts=min_close_ts,
            max_close_ts=max_close_ts
        )
        
        print(f"\nResults:")
        print(f"Total markets found: {len(markets)}")
        
        if markets:
            print(f"\nFirst 5 markets with close times:")
            for i, market in enumerate(markets[:5]):
                ticker = market.get('ticker', 'N/A')
                event_ticker = market.get('event_ticker', 'N/A')
                status = market.get('status', 'N/A')
                close_time = market.get('close_time', 'N/A')
                expiration_time = market.get('expiration_time', 'N/A')
                
                print(f"  {i+1}. {ticker}")
                print(f"     Event: {event_ticker}")
                print(f"     Status: {status}")
                print(f"     Close Time: {close_time}")
                print(f"     Expiration Time: {expiration_time}")
                print()
        else:
            print("No markets found with the specified date range.")
            
    except Exception as e:
        print(f"Error: {e}")

def test_markets_without_filters():
    """Test markets API without any filters for comparison (defaults to active status)"""
    
    print(f"Testing markets API with default filters (active status):")
    print("-" * 60)
    
    try:
        # Call the markets API without filters (will default to active status)
        markets = get_all_markets()
        
        print(f"\nResults:")
        print(f"Total markets found: {len(markets)}")
        
        if markets:
            print(f"\nFirst 3 markets:")
            for i, market in enumerate(markets[:3]):
                ticker = market.get('ticker', 'N/A')
                event_ticker = market.get('event_ticker', 'N/A')
                status = market.get('status', 'N/A')
                close_time = market.get('close_time', 'N/A')
                
                print(f"  {i+1}. {ticker}")
                print(f"     Event: {event_ticker}")
                print(f"     Status: {status}")
                print(f"     Close Time: {close_time}")
                print()
        else:
            print("No markets found.")
            
    except Exception as e:
        print(f"Error: {e}")

def test_markets_all_statuses():
    """Test markets API with all statuses to compare with active-only"""
    
    print(f"Testing markets API with all statuses:")
    print("-" * 60)
    
    try:
        # Call the markets API with all statuses
        markets = get_all_markets(status="")
        
        print(f"\nResults:")
        print(f"Total markets found: {len(markets)}")
        
        if markets:
            print(f"\nFirst 3 markets:")
            for i, market in enumerate(markets[:3]):
                ticker = market.get('ticker', 'N/A')
                event_ticker = market.get('event_ticker', 'N/A')
                status = market.get('status', 'N/A')
                close_time = market.get('close_time', 'N/A')
                
                print(f"  {i+1}. {ticker}")
                print(f"     Event: {event_ticker}")
                print(f"     Status: {status}")
                print(f"     Close Time: {close_time}")
                print()
        else:
            print("No markets found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== TEST 1: Markets with date filters ===")
    test_markets_with_date_filters()
    
    print("\n" + "="*80 + "\n")
    
    print("=== TEST 2: Markets with default filters (active status) ===")
    test_markets_without_filters()
    
    print("\n" + "="*80 + "\n")
    
    print("=== TEST 3: Markets with all statuses ===")
    test_markets_all_statuses() 