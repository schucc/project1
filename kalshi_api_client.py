import base64
import requests
import datetime
import getpass
import csv
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature


def load_private_key_from_file(key_file_path: str) -> rsa.RSAPrivateKey:
    """
    Load RSA private key from a PEM file.
    
    Args:
        key_file_path: Path to the private key file
        
    Returns:
        RSA private key object
    """
    try:
        with open(key_file_path, 'rb') as key_file:
            key_data = key_file.read()
            
        # First try without password
        try:
            private_key = serialization.load_pem_private_key(key_data, password=None)
            return private_key
        except ValueError:
            # If that fails, try with password
            password = getpass.getpass("Enter password for private key: ")
            private_key = serialization.load_pem_private_key(key_data, password=password.encode())
            return private_key
            
    except Exception as e:
        raise ValueError(f"Failed to load private key from {key_file_path}: {e}")


def sign_pss_text(private_key: rsa.RSAPrivateKey, text: str) -> str:
    """
    Sign text using RSA-PSS with SHA256.
    
    Args:
        private_key: RSA private key object
        text: Text to sign
        
    Returns:
        Base64 encoded signature
    """
    # Convert the text to bytes
    message = text.encode('utf-8')

    try:
        signature = private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return base64.b64encode(signature).decode('utf-8')
    except InvalidSignature as e:
        raise ValueError("RSA sign PSS failed") from e


def get_kalshi_headers(private_key: rsa.RSAPrivateKey, method: str, path: str, 
                      access_key: str) -> dict:
    """
    Generate headers required for Kalshi API authentication.
    
    Args:
        private_key: RSA private key object
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        access_key: Kalshi access key
        
    Returns:
        Dictionary containing authentication headers
    """
    # Get current timestamp in milliseconds
    current_time = datetime.datetime.now()
    timestamp = current_time.timestamp()
    current_time_milliseconds = int(timestamp * 1000)
    timestamp_str = str(current_time_milliseconds)
    
    # Create message string for signing
    msg_string = timestamp_str + method + path
    
    # Sign the message
    signature = sign_pss_text(private_key, msg_string)
    
    # Create headers
    headers = {
        'KALSHI-ACCESS-KEY': access_key,
        'KALSHI-ACCESS-SIGNATURE': signature,
        'KALSHI-ACCESS-TIMESTAMP': timestamp_str
    }
    
    return headers


def call_kalshi_api(method: str, path: str, base_url: str = 'https://api.elections.kalshi.com',
                   key_file_path: str = 'kalshi-key-pkcs8.key',
                   access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043',
                   data: dict = None, params: dict = None) -> requests.Response:
    """
    Make an authenticated API call to Kalshi.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        data: Request data for POST requests
        params: Query parameters for GET requests
        
    Returns:
        Response object from the API call
    """
    # Load private key
    private_key = load_private_key_from_file(key_file_path)
    
    # Get authentication headers
    headers = get_kalshi_headers(private_key, method, path, access_key)
    
    # Make the API call
    url = base_url + path
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers, params=params)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response


def get_all_trades(base_url: str = 'https://api.elections.kalshi.com',
                   key_file_path: str = 'kalshi-key-pkcs8.key',
                   access_key: str = '09c2a50e-18ff-4965-befb-f7f6a1b0b043',
                   ticker: str = None, limit: int = 1000, 
                   min_ts: int = None, max_ts: int = None) -> list:
    """
    Fetch all trades data using cursor-based pagination.
    
    Args:
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        ticker: Specific market ticker to filter by
        limit: Number of results per page (1-1000, default 1000 for efficiency)
        min_ts: Minimum timestamp filter
        max_ts: Maximum timestamp filter
        
    Returns:
        List of all trades across all pages
    """
    all_trades = []
    cursor = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"Fetching page {page_count}...")
        
        # Build query parameters
        params = {"limit": str(limit)}
        if ticker:
            params["ticker"] = ticker
        if min_ts:
            params["min_ts"] = str(min_ts)
        if max_ts:
            params["max_ts"] = str(max_ts)
        if cursor:
            params["cursor"] = cursor
        
        # Make API call
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/markets/trades",
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
            trades = data.get("trades", [])
            all_trades.extend(trades)
            
            print(f"Page {page_count}: Retrieved {len(trades)} trades")
            
            # Check if there are more pages
            cursor = data.get("cursor")
            if not cursor:
                print(f"No more pages. Total trades retrieved: {len(all_trades)}")
                break
                
        except Exception as e:
            print(f"Error parsing response on page {page_count}: {e}")
            break
    
    return all_trades


def trades_to_csv(trades: list, filename: str = "trades_data.csv") -> None:
    """
    Convert trades data to CSV format and save to file.
    
    Args:
        trades: List of trade dictionaries
        filename: Output CSV filename
    """
    if not trades:
        print("No trades data to convert to CSV")
        return
    
    # Get all possible field names from the trades data
    fieldnames = set()
    for trade in trades:
        fieldnames.update(trade.keys())
    
    # Convert to sorted list for consistent column order
    fieldnames = sorted(list(fieldnames))
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write data rows
        for trade in trades:
            # Ensure all fields are present (fill missing with empty string)
            row = {field: trade.get(field, '') for field in fieldnames}
            writer.writerow(row)
    
    print(f"CSV file saved as: {filename}")
    print(f"Columns: {', '.join(fieldnames)}")


def main():
    """
    Example usage of the Kalshi API client.
    """
    # Example: Get all trades for a specific ticker
    try:
        print("Fetching all trades for LEAVEPOWELL-25-DEC31...")
        all_trades = get_all_trades(
            ticker="LEAVEPOWELL-25-DEC31",
            limit=1000  # Maximum limit for efficiency
        )
        
        print(f"\nTotal trades retrieved: {len(all_trades)}")
        
        # Display first few trades as example
        if all_trades:
            print("\nFirst 3 trades:")
            for i, trade in enumerate(all_trades[:3]):
                print(f"Trade {i+1}: {trade}")
        
        # Save to JSON file
        with open("trades_data.json", "w") as f:
            json.dump(all_trades, f, indent=2)
        print(f"\nAll trades saved to trades_data.json")
        
        # Convert to CSV and save
        trades_to_csv(all_trades, "trades_data.csv")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 