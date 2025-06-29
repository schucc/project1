# Kalshi API Trading Data Explorer - Package Information

## Package Contents

This package contains a complete web application for fetching and analyzing Kalshi API trading data.

### Core Files

- `app.py` - Flask web server (main application)
- `kalshi_api_client.py` - Kalshi API client with RSA-PSS authentication
- `data_analysis.py` - Data analysis and chart generation
- `index.html` - Web interface
- `styles.css` - CSS styling
- `script.js` - Frontend JavaScript
- `requirements.txt` - Python dependencies

### Setup and Run Scripts

- `setup.py` - Automated setup script
- `run.bat` - Windows launcher
- `run.sh` - Mac/Linux launcher
- `INSTALL.md` - Quick installation guide
- `README.md` - Comprehensive documentation

### Configuration

- `.gitignore` - Excludes sensitive files
- `PACKAGE_INFO.md` - This file

## What's NOT Included

For security reasons, the following are NOT included:

- Private key files (_.key, _.pem, \*.p8)
- API credentials
- Generated data files (_.csv, _.json)

## Installation Instructions

### Quick Start

1. Extract all files to a folder
2. Run: `python setup.py` (or double-click `run.bat` on Windows)
3. Add your Kalshi private key file
4. Update your access key in `kalshi_api_client.py`
5. Run: `python app.py` (or use the launcher scripts)
6. Open: http://localhost:5015

### Detailed Instructions

See `INSTALL.md` for step-by-step instructions for Windows, Mac, and Linux.

## System Requirements

- Python 3.8 or higher
- pip (Python package installer)
- Web browser (Chrome, Firefox, Safari, Edge)
- Kalshi API account with:
  - Access key
  - RSA private key file

## Dependencies

The application will automatically install these Python packages:

- Flask (web framework)
- requests (HTTP client)
- cryptography (RSA encryption)
- pandas (data manipulation)
- matplotlib (chart generation)
- seaborn (statistical visualizations)
- numpy (numerical computing)

## Security Notes

- Private key files are excluded from this package
- Users must add their own API credentials
- The application runs locally and doesn't transmit credentials
- All sensitive files are listed in `.gitignore`

## Support

For help:

1. Check `INSTALL.md` for troubleshooting
2. Review `README.md` for detailed documentation
3. Check console output for error messages
4. Verify API credentials are correct

## Version Information

- Application: Kalshi API Trading Data Explorer
- Python: 3.8+ required
- Dependencies: See requirements.txt
- Last Updated: December 2024

## License

This project is for educational and personal use. Please respect Kalshi's API terms of service.
