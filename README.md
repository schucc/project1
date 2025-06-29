# Kalshi API Trading Data Explorer

A web-based application for fetching, analyzing, and visualizing trading data from the Kalshi API. This tool provides real-time data fetching, interactive statistics, and comprehensive trading analysis.

## Features

- **Real-time Data Fetching**: Connect to Kalshi API with RSA-PSS authentication
- **Interactive Web Interface**: Modern, responsive UI with sorting and filtering
- **Comprehensive Analytics**: Statistics, metrics, and visualizations
- **Data Export**: Export data to CSV format
- **Chart Generation**: Multiple chart types for data analysis

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. **Download and Extract**

   - Download the project files
   - Extract to a folder on your computer

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Credentials**

   - Place your Kalshi private key file in the project directory
   - Update the access key in `kalshi_api_client.py` (line 108)
   - Default key file name: `kalshi-key-pkcs8.key`

4. **Run the Application**

   ```bash
   python app.py
   ```

5. **Access the Web Interface**
   - Open your browser
   - Go to: `http://localhost:5015`

## Configuration

### API Credentials

1. **Private Key**: Your RSA private key file (PKCS#8 format)

   - Default filename: `kalshi-key-pkcs8.key`
   - Update path in `kalshi_api_client.py` if different

2. **Access Key**: Your Kalshi API access key
   - Update in `kalshi_api_client.py` line 108
   - Current default: `'09c2a50e-18ff-4965-befb-f7f6a1b0b043'`

### Customization

- **Port**: Change port in `app.py` line 202 (default: 5015)
- **Base URL**: Update API base URL in `kalshi_api_client.py` line 107
- **Default Ticker**: Modify default ticker in `kalshi_api_client.py` line 110

## Usage

### Fetching Data

1. **Enter Parameters**:

   - **Ticker**: Market ticker (e.g., `LEAVEPOWELL-25-DEC31`)
   - **Limit**: Number of trades per page (1-1000)
   - **Date Range**: Optional start/end timestamps
   - **Fetch All**: Check to get all available data

2. **Click "Fetch Data"** to retrieve trading data

### Analyzing Data

1. **View Statistics**: Basic trading statistics and metrics
2. **Advanced Metrics**: Detailed analysis and correlations
3. **Charts**: Visual representations of the data
4. **Combined Analysis**: All analyses in one view

### Data Management

- **Sort**: Click column headers to sort data
- **Filter**: Use the search box to filter results
- **Export**: Download data as CSV file

## File Structure

```
Kalshi-Api/
├── app.py                 # Flask web server
├── kalshi_api_client.py   # Kalshi API client with authentication
├── data_analysis.py       # Data analysis and chart generation
├── index.html            # Web interface
├── styles.css            # CSS styling
├── script.js             # Frontend JavaScript
├── requirements.txt      # Python dependencies
├── setup.py              # Automated setup script
├── run.bat               # Windows launcher
├── run.sh                # Mac/Linux launcher
├── README.md            # This file
├── INSTALL.md           # Quick installation guide
├── PACKAGE_INFO.md      # Package information
├── .gitignore           # Excludes sensitive files
└── kalshi-key-pkcs8.key # Your private key (not included)
```

## API Endpoints

- `GET /` - Main web interface
- `POST /api/trades` - Fetch trading data
- `GET /api/analysis/stats` - Get basic statistics
- `GET /api/analysis/metrics` - Get advanced metrics
- `GET /api/analysis/chart/<type>` - Generate charts
- `GET /api/analysis/all` - Get all analyses

## Easy Setup Options

### Automated Setup

```bash
python setup.py
```

### Quick Launch

- **Windows**: Double-click `run.bat`
- **Mac/Linux**: `./run.sh`
- **Manual**: `python app.py`

## Troubleshooting

### Common Issues

1. **"No module named 'cryptography'"**

   - Run: `pip install cryptography`

2. **"Private key not found"**

   - Ensure your key file is in the project directory
   - Check the filename matches the configuration

3. **"401 Unauthorized"**

   - Verify your access key is correct
   - Check that your private key is valid

4. **"Port already in use"**
   - Change the port number in `app.py`
   - Or stop other applications using port 5015

### Getting Help

- Check the console output for error messages
- Verify your API credentials are correct
- Ensure all dependencies are installed
- See `INSTALL.md` for detailed troubleshooting

## Security Notes

- Keep your private key file secure
- Don't share your API credentials
- The key file is not included in this package for security
- All sensitive files are listed in `.gitignore`

## Dependencies

- Flask: Web framework
- requests: HTTP client
- cryptography: RSA encryption
- pandas: Data manipulation
- matplotlib: Chart generation
- seaborn: Statistical visualizations
- numpy: Numerical computing

## Recent Updates

- Added comprehensive data analysis with statistics and charts
- Fixed JSON serialization issues with NumPy data types
- Added automated setup script (`setup.py`)
- Created cross-platform launcher scripts (`run.bat`, `run.sh`)
- Added detailed installation guides (`INSTALL.md`, `PACKAGE_INFO.md`)
- Improved error handling and debugging
- Enhanced frontend with better data display and analysis features

## License

This project is for educational and personal use. Please respect Kalshi's API terms of service.

## Support

For issues or questions:

1. Check the troubleshooting section
2. Verify your API credentials
3. Ensure all dependencies are installed correctly
4. See `INSTALL.md` for step-by-step instructions
