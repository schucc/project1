import requests
import json
from typing import Dict, List, Optional
from kalshi_api_client import call_kalshi_api


def get_all_markets(base_url: str = 'https://api.elections.kalshi.com',
                   key_file_path: str = 'kalshi-key-pkcs8.key',
                   access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043',
                   limit: int = 1000,
                   event_ticker: str = None,
                   series_ticker: str = None,
                   min_close_ts: int = None,
                   max_close_ts: int = None,
                   status: str = None,
                   tickers: str = None,
                   max_pages: int = 10) -> List[Dict]:
    """
    Fetch all markets data using cursor-based pagination.
    
    Args:
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        limit: Number of results per page (1-1000, default 1000 for efficiency)
        event_ticker: Event ticker to filter by
        series_ticker: Series ticker to filter by
        min_close_ts: Minimum close timestamp filter
        max_close_ts: Maximum close timestamp filter
        status: Market status filter (unopened, open, closed, settled, active). Defaults to None (all statuses).
        tickers: Comma-separated list of tickers to filter by
        max_pages: Maximum number of pages to fetch (default 10 to prevent excessive API calls)
        
    Returns:
        List of all markets across all pages
    """
    all_markets = []
    cursor = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"Fetching markets page {page_count}...")
        
        # Check if we've reached the maximum number of pages
        if page_count > max_pages:
            print(f"Reached maximum page limit ({max_pages}). Stopping pagination.")
            break
        
        # Build query parameters
        params = {"limit": str(limit)}
        if cursor:
            params["cursor"] = cursor
        if event_ticker:
            params["event_ticker"] = event_ticker
        if series_ticker:
            params["series_ticker"] = series_ticker
        if min_close_ts:
            params["min_close_ts"] = str(min_close_ts)
        if max_close_ts:
            params["max_close_ts"] = str(max_close_ts)
        if status:
            params["status"] = status
        if tickers:
            params["tickers"] = tickers
        
        # Make API call
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/markets",
            base_url=base_url,
            key_file_path=key_file_path,
            access_key=access_key,
            params=params
        )
        
        if response.status_code != 200:
            print(f"Error on page {page_count}: {response.status_code}")
            print(f"Response: {response.text}")
            break
        
        # Parse response
        try:
            data = response.json()
            markets = data.get("markets", [])
            print(f"Cursor: {data.get('cursor')}")
            print(f"Page {page_count}: Retrieved {len(markets)} markets")
            
            if len(markets) == 0:
                print(f"No new markets returned on page {page_count}. Stopping pagination.")
                break
            
            all_markets.extend(markets)
            
            # Check if there are more pages
            cursor = data.get("cursor")
            if not cursor:
                print(f"No more pages. Total markets retrieved: {len(all_markets)}")
                break
                
        except Exception as e:
            print(f"Error parsing response on page {page_count}: {e}")
            break
    
    return all_markets


def organize_markets_by_event(markets: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organize markets by event_ticker for easier frontend consumption.
    
    Args:
        markets: List of market dictionaries
        
    Returns:
        Dictionary with event_ticker as key and list of markets as value
    """
    organized = {}
    
    for market in markets:
        event_ticker = market.get('event_ticker', 'Unknown')
        if event_ticker not in organized:
            organized[event_ticker] = []
        organized[event_ticker].append(market)
    
    return organized


def get_markets_for_event_ticker(markets: List[Dict], event_ticker: str) -> List[Dict]:
    """
    Get all markets for a specific event ticker.
    
    Args:
        markets: List of all markets
        event_ticker: The event ticker to filter by
        
    Returns:
        List of markets for the specified event ticker
    """
    return [market for market in markets if market.get('event_ticker') == event_ticker]


def get_unique_event_tickers(markets: List[Dict]) -> List[str]:
    """
    Get a list of unique event tickers from the markets data.
    
    Args:
        markets: List of market dictionaries
        
    Returns:
        List of unique event tickers, sorted alphabetically
    """
    event_tickers = set()
    for market in markets:
        event_ticker = market.get('event_ticker')
        if event_ticker:
            event_tickers.add(event_ticker)
    
    return sorted(list(event_tickers))


def filter_markets_by_status(markets: List[Dict], status: str = 'open') -> List[Dict]:
    """
    Filter markets by their status (e.g., 'open', 'closed', 'settled').
    
    Args:
        markets: List of market dictionaries
        status: Status to filter by (default: 'open')
        
    Returns:
        List of markets with the specified status
    """
    return [market for market in markets if market.get('status') == status]


def save_markets_to_json(markets: List[Dict], filename: str = "markets_data.json") -> None:
    """
    Save markets data to a JSON file.
    
    Args:
        markets: List of market dictionaries
        filename: Output JSON filename
    """
    with open(filename, 'w') as f:
        json.dump(markets, f, indent=2)
    print(f"Markets data saved to {filename}")


def main():
    """
    Example usage of the markets API functions.
    """
    try:
        print("Fetching all markets from Kalshi API...")
        all_markets = get_all_markets()
        
        print(f"\nTotal markets retrieved: {len(all_markets)}")
        
        # Get unique event tickers
        event_tickers = get_unique_event_tickers(all_markets)
        print(f"\nUnique event tickers found: {len(event_tickers)}")
        print("First 10 event tickers:", event_tickers[:10])
        
        # Organize by event ticker
        organized_markets = organize_markets_by_event(all_markets)
        print(f"\nOrganized into {len(organized_markets)} event groups")
        
        # Show example for first event ticker
        if event_tickers:
            first_event = event_tickers[0]
            markets_for_event = organized_markets[first_event]
            print(f"\nExample - Markets for '{first_event}':")
            for market in markets_for_event[:3]:  # Show first 3
                print(f"  - {market.get('ticker')} (Status: {market.get('status')})")
        
        # Save to JSON file
        save_markets_to_json(all_markets, "markets_data.json")
        
        # Also save organized version
        with open("markets_by_event.json", 'w') as f:
            json.dump(organized_markets, f, indent=2)
        print("Organized markets saved to markets_by_event.json")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 