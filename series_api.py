import requests
import json
from typing import Dict, List, Optional
from kalshi_api_client import call_kalshi_api


def get_series_list(base_url: str = 'https://api.elections.kalshi.com',
                   key_file_path: str = 'kalshi-key-pkcs8.key',
                   access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043',
                   category: str = None,
                   include_product_metadata: bool = False) -> List[Dict]:
    """
    Fetch series list from Kalshi API.
    
    Args:
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        category: Category to filter series by (required)
        include_product_metadata: Whether to include product metadata in response
        
    Returns:
        List of series data
    """
    try:
        # Build query parameters
        params = {}
        if category:
            params["category"] = category
        if include_product_metadata:
            params["include_product_metadata"] = str(include_product_metadata).lower()
        
        print(f"Fetching series list with params: {params}")
        
        # Make API call
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/series/",
            base_url=base_url,
            key_file_path=key_file_path,
            access_key=access_key,
            params=params
        )
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
        
        # Parse response
        data = response.json()
        series = data.get("series", [])
        
        print(f"Retrieved {len(series)} series")
        return series
        
    except Exception as e:
        print(f"Error fetching series list: {e}")
        return []


def get_all_categories(base_url: str = 'https://api.elections.kalshi.com',
                      key_file_path: str = 'kalshi-key-pkcs8.key',
                      access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043') -> List[str]:
    """
    Get all available categories by fetching series without category filter.
    
    Args:
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        
    Returns:
        List of unique categories
    """
    try:
        # Fetch series without category filter to get all categories
        series = get_series_list(
            base_url=base_url,
            key_file_path=key_file_path,
            access_key=access_key
        )
        
        # Extract unique categories
        categories = set()
        for s in series:
            category = s.get('category')
            if category:
                categories.add(category)
        
        return sorted(list(categories))
        
    except Exception as e:
        print(f"Error getting categories: {e}")
        return []


def get_series_by_category(category: str,
                         base_url: str = 'https://api.elections.kalshi.com',
                         key_file_path: str = 'kalshi-key-pkcs8.key',
                         access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043',
                         include_product_metadata: bool = False) -> List[Dict]:
    """
    Get series for a specific category.
    
    Args:
        category: Category to filter by
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        include_product_metadata: Whether to include product metadata
        
    Returns:
        List of series for the specified category
    """
    return get_series_list(
        base_url=base_url,
        key_file_path=key_file_path,
        access_key=access_key,
        category=category,
        include_product_metadata=include_product_metadata
    )


def get_series_by_tag(tag: str,
                     base_url: str = 'https://api.elections.kalshi.com',
                     key_file_path: str = 'kalshi-key-pkcs8.key',
                     access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043') -> List[Dict]:
    """
    Get series that contain a specific tag.
    
    Args:
        tag: Tag to search for
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        
    Returns:
        List of series containing the specified tag
    """
    try:
        # Get all series first (since API doesn't support tag filtering directly)
        all_series = get_series_list(
            base_url=base_url,
            key_file_path=key_file_path,
            access_key=access_key
        )
        
        # Filter by tag
        filtered_series = []
        for series in all_series:
            tags = series.get('tags', [])
            if tag.lower() in [t.lower() for t in tags]:
                filtered_series.append(series)
        
        return filtered_series
        
    except Exception as e:
        print(f"Error getting series by tag: {e}")
        return []


def organize_series_by_category(series: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Organize series by category for easier frontend consumption.
    
    Args:
        series: List of series dictionaries
        
    Returns:
        Dictionary with category as key and list of series as value
    """
    organized = {}
    
    for s in series:
        category = s.get('category', 'Unknown')
        if category not in organized:
            organized[category] = []
        organized[category].append(s)
    
    return organized


def get_unique_tags(series: List[Dict]) -> List[str]:
    """
    Get a list of unique tags from the series data.
    
    Args:
        series: List of series dictionaries
        
    Returns:
        List of unique tags, sorted alphabetically
    """
    tags = set()
    for s in series:
        series_tags = s.get('tags', [])
        if series_tags:  # Check if tags is not None and not empty
            tags.update(series_tags)
    
    return sorted(list(tags))


def save_series_to_json(series: List[Dict], filename: str = "series_data.json") -> None:
    """
    Save series data to a JSON file.
    
    Args:
        series: List of series dictionaries
        filename: Output JSON filename
    """
    with open(filename, 'w') as f:
        json.dump(series, f, indent=2)
    print(f"Series data saved to {filename}")


def print_series_summary(series: List[Dict]) -> None:
    """
    Print a summary of series data.
    
    Args:
        series: List of series dictionaries
    """
    if not series:
        print("No series data available")
        return
    
    print(f"\nSeries Summary:")
    print(f"Total series: {len(series)}")
    
    # Get categories
    categories = set()
    for s in series:
        categories.add(s.get('category', 'Unknown'))
    
    print(f"Categories: {len(categories)}")
    for category in sorted(categories):
        count = len([s for s in series if s.get('category') == category])
        print(f"  - {category}: {count} series")
    
    # Get tags
    tags = get_unique_tags(series)
    print(f"Tags: {len(tags)}")
    print(f"  Sample tags: {', '.join(tags[:10])}")
    
    # Show first few series
    print(f"\nFirst 3 series:")
    for i, s in enumerate(series[:3]):
        ticker = s.get('ticker', 'N/A')
        title = s.get('title', 'N/A')
        category = s.get('category', 'N/A')
        frequency = s.get('frequency', 'N/A')
        
        print(f"  {i+1}. {ticker}")
        print(f"     Title: {title}")
        print(f"     Category: {category}")
        print(f"     Frequency: {frequency}")
        print()


def get_series_with_market_data(category: str,
                              base_url: str = 'https://api.elections.kalshi.com',
                              key_file_path: str = 'kalshi-key-pkcs8.key',
                              access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043') -> List[Dict]:
    """
    Get series for a specific category with market metadata.
    
    Args:
        category: Category to filter by
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        
    Returns:
        List of series with market metadata
    """
    try:
        # Import here to avoid circular imports
        from markets_api import get_all_markets
        
        # Get series for the category
        series = get_series_by_category(category, base_url, key_file_path, access_key)
        
        # Get all markets to find metadata for each series
        markets = get_all_markets(base_url=base_url, key_file_path=key_file_path, access_key=access_key)
        
        # Create a lookup for markets by series_ticker
        markets_by_series = {}
        for market in markets:
            series_ticker = market.get('series_ticker')
            if series_ticker:
                if series_ticker not in markets_by_series:
                    markets_by_series[series_ticker] = []
                markets_by_series[series_ticker].append(market)
        
        # Combine series data with market metadata
        series_with_metadata = []
        for s in series:
            series_ticker = s.get('ticker')
            series_markets = markets_by_series.get(series_ticker, [])
            
            # Calculate aggregated metadata from all markets in this series
            total_volume = sum(m.get('volume', 0) for m in series_markets)
            
            # Get the most recent last_price from active/open markets
            last_price = None
            for market in series_markets:
                if market.get('status') in ['active', 'open'] and market.get('last_price'):
                    last_price = market.get('last_price')
                    break
            
            # If no active markets, get from any market
            if last_price is None:
                for market in series_markets:
                    if market.get('last_price'):
                        last_price = market.get('last_price')
                        break
            
            # Get earliest open_time and latest close_time
            open_times = [m.get('open_time') for m in series_markets if m.get('open_time')]
            close_times = [m.get('close_time') for m in series_markets if m.get('close_time')]
            
            earliest_open = min(open_times) if open_times else None
            latest_close = max(close_times) if close_times else None
            
            # Determine overall status based on market statuses
            statuses = [m.get('status') for m in series_markets if m.get('status')]
            if 'active' in statuses or 'open' in statuses:
                overall_status = 'active'
            elif 'closed' in statuses:
                overall_status = 'closed'
            elif 'settled' in statuses:
                overall_status = 'settled'
            elif 'unopened' in statuses:
                overall_status = 'unopened'
            else:
                overall_status = 'unknown'
            
            # Create enhanced series object
            enhanced_series = {
                **s,  # Include all original series data
                'status': overall_status,
                'volume': total_volume,
                'last_price': last_price,
                'open_time': earliest_open,
                'close_time': latest_close,
                'market_count': len(series_markets)
            }
            
            series_with_metadata.append(enhanced_series)
        
        return series_with_metadata
        
    except Exception as e:
        print(f"Error getting series with market data: {e}")
        # Fallback to original series data without metadata
        return get_series_by_category(category, base_url, key_file_path, access_key)


def main():
    """
    Example usage of the series API functions.
    """
    try:
        print("Fetching series list from Kalshi API...")
        
        # Get all series
        all_series = get_series_list()
        
        if all_series:
            print_series_summary(all_series)
            
            # Get categories
            categories = get_all_categories()
            print(f"\nAvailable categories: {categories}")
            
            # Test getting series by category (if categories exist)
            if categories:
                first_category = categories[0]
                print(f"\nTesting series by category '{first_category}':")
                category_series = get_series_by_category(first_category)
                print(f"Found {len(category_series)} series in category '{first_category}'")
            
            # Save to JSON file
            save_series_to_json(all_series, "series_data.json")
            
            # Also save organized version
            organized_series = organize_series_by_category(all_series)
            with open("series_by_category.json", 'w') as f:
                json.dump(organized_series, f, indent=2)
            print("Organized series saved to series_by_category.json")
            
        else:
            print("No series data retrieved")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 