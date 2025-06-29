#!/usr/bin/env python3
"""
Setup script for Kalshi API Trading Data Explorer
"""

import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def check_key_file():
    """Check if the private key file exists"""
    key_file = "kalshi-key-pkcs8.key"
    if os.path.exists(key_file):
        print(f"✅ Private key file found: {key_file}")
        return True
    else:
        print(f"⚠️  Warning: Private key file not found: {key_file}")
        print("   You'll need to add your Kalshi private key file to run the application")
        return False

def check_configuration():
    """Check basic configuration"""
    print("\n🔧 Checking configuration...")
    
    # Check if key file path is correct in the client
    try:
        with open("kalshi_api_client.py", "r") as f:
            content = f.read()
            if "kalshi-key-pkcs8.key" in content:
                print("✅ Key file path configured correctly")
            else:
                print("⚠️  Warning: Key file path may need updating")
    except FileNotFoundError:
        print("❌ Error: kalshi_api_client.py not found")
        return False
    
    return True

def create_sample_config():
    """Create a sample configuration file"""
    config_content = """# Kalshi API Configuration
# Update these values with your actual credentials

# Your Kalshi API access key
ACCESS_KEY = "your-access-key-here"

# Path to your private key file
KEY_FILE = "kalshi-key-pkcs8.key"

# API base URL (usually doesn't need to change)
BASE_URL = "https://api.elections.kalshi.com"

# Default ticker to fetch
DEFAULT_TICKER = "LEAVEPOWELL-25-DEC31"
"""
    
    if not os.path.exists("config_sample.txt"):
        with open("config_sample.txt", "w") as f:
            f.write(config_content)
        print("📝 Created config_sample.txt with configuration template")

def main():
    """Main setup function"""
    print("🚀 Kalshi API Trading Data Explorer - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check configuration
    check_configuration()
    
    # Check key file
    check_key_file()
    
    # Create sample config
    create_sample_config()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed!")
    print("\n📋 Next steps:")
    print("1. Add your Kalshi private key file (kalshi-key-pkcs8.key)")
    print("2. Update your access key in kalshi_api_client.py")
    print("3. Run the application:")
    print("   - Windows: Double-click run.bat")
    print("   - Mac/Linux: ./run.sh")
    print("   - Or manually: python app.py")
    print("\n🌐 The web interface will be available at: http://localhost:5015")

if __name__ == "__main__":
    main() 