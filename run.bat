@echo off
echo Kalshi API Trading Data Explorer
echo ================================
echo.
echo Starting the application...
echo.
echo Make sure you have:
echo 1. Python installed
echo 2. Dependencies installed (pip install -r requirements.txt)
echo 3. Your Kalshi private key file in this directory
echo 4. Updated your access key in kalshi_api_client.py
echo.
echo The web interface will open at: http://localhost:5015
echo.
echo Press Ctrl+C to stop the server
echo.
python app.py
pause 