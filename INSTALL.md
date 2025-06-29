# Quick Installation Guide

## For Windows Users

1. **Download and Extract**

   - Download the project files
   - Extract to a folder (e.g., `C:\Kalshi-Api`)

2. **Install Python** (if not already installed)

   - Download from: https://www.python.org/downloads/
   - Make sure to check "Add Python to PATH" during installation

3. **Run Setup**

   - Double-click `run.bat` to start the setup
   - Or open Command Prompt in the folder and run: `python setup.py`

4. **Add Your Credentials**

   - Place your Kalshi private key file in the folder
   - Rename it to: `kalshi-key-pkcs8.key`
   - Edit `kalshi_api_client.py` and update your access key

5. **Start the Application**

   - Double-click `run.bat`
   - Or run: `python app.py`

6. **Open in Browser**
   - Go to: http://localhost:5015

## For Mac/Linux Users

1. **Download and Extract**

   ```bash
   # Extract the files
   tar -xzf kalshi-api.tar.gz
   cd Kalshi-Api
   ```

2. **Install Python** (if not already installed)

   ```bash
   # Mac (using Homebrew)
   brew install python3

   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip
   ```

3. **Run Setup**

   ```bash
   python3 setup.py
   ```

4. **Add Your Credentials**

   - Place your Kalshi private key file in the folder
   - Rename it to: `kalshi-key-pkcs8.key`
   - Edit `kalshi_api_client.py` and update your access key

5. **Start the Application**

   ```bash
   ./run.sh
   # Or manually:
   python3 app.py
   ```

6. **Open in Browser**
   - Go to: http://localhost:5015

## Troubleshooting

### Common Issues

**"Python not found"**

- Install Python from https://www.python.org/downloads/
- Make sure it's added to your system PATH

**"pip not found"**

- Python 3.4+ includes pip by default
- If missing: `python -m ensurepip --upgrade`

**"Permission denied" (Mac/Linux)**

- Make scripts executable: `chmod +x run.sh setup.py`

**"Port already in use"**

- Change port in `app.py` line 202
- Or stop other applications using port 5015

**"Private key not found"**

- Ensure your key file is named `kalshi-key-pkcs8.key`
- Check it's in the same folder as the other files

### Getting Help

1. Check the console output for error messages
2. Verify your API credentials are correct
3. Ensure all dependencies are installed
4. Check the main README.md for detailed instructions

## File Checklist

Make sure you have these files in your folder:

- ✅ `app.py`
- ✅ `kalshi_api_client.py`
- ✅ `data_analysis.py`
- ✅ `index.html`
- ✅ `styles.css`
- ✅ `script.js`
- ✅ `requirements.txt`
- ✅ `README.md`
- ✅ `run.bat` (Windows)
- ✅ `run.sh` (Mac/Linux)
- ✅ `setup.py`
- ✅ `kalshi-key-pkcs8.key` (your private key)
