import base64
import requests
import datetime
import getpass
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
                salt_length=padding.PSS.DIGEST_LENGTH
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
                   data: dict = None) -> requests.Response:
    """
    Make an authenticated API call to Kalshi.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        path: API endpoint path
        base_url: Base URL for the API
        key_file_path: Path to the private key file
        access_key: Kalshi access key
        data: Request data for POST requests
        
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
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, json=data)
    elif method.upper() == 'PUT':
        response = requests.put(url, headers=headers, json=data)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    return response


def main():
    """
    Example usage of the Kalshi API client.
    """
    # Example: Get portfolio balance
    try:
        response = call_kalshi_api(
            method="GET",
            path="/trade-api/v2/markets/trades"
        )
        
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)
        
        if response.status_code == 200:
            print("API call successful!")
        else:
            print("API call failed!")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 