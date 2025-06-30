#!/usr/bin/env python3
"""
Test script to examine the structure of a single series response
"""

from series_api import get_series_list
import json

def test_single_series():
    """Test to examine the structure of series data"""
    
    try:
        # Get a few series to examine
        series = get_series_list()
        
        if series:
            print(f"Retrieved {len(series)} series")
            print("-" * 60)
            
            # Show first series structure
            first_series = series[0]
            print("First series structure:")
            print(json.dumps(first_series, indent=2))
            
            print("\nAvailable fields:")
            for key, value in first_series.items():
                if isinstance(value, list):
                    print(f"  {key}: list[{len(value)}] = {value[:3] if value else '[]'}")
                elif isinstance(value, dict):
                    print(f"  {key}: dict = {list(value.keys())}")
                else:
                    print(f"  {key}: {type(value).__name__} = {value}")
            
            # Show a few more series for comparison
            print(f"\nSample series tickers:")
            for i, s in enumerate(series[:5]):
                ticker = s.get('ticker', 'N/A')
                title = s.get('title', 'N/A')
                category = s.get('category', 'N/A')
                print(f"  {i+1}. {ticker} ({category})")
                print(f"     {title}")
                print()
        else:
            print("No series returned")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_single_series() 