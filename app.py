from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from kalshi_api_client import get_all_trades
from markets_api import get_all_markets, organize_markets_by_event, get_unique_event_tickers, get_markets_for_event_ticker
from data_analysis import TradingDataAnalyzer
from series_api import get_all_categories, get_series_by_category

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store current data
current_trades_data = []
current_markets_data = []
organized_markets_data = {}

# Serve static files (HTML, CSS, JS)
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# API endpoint to fetch trades data
@app.route('/api/trades', methods=['POST'])
def fetch_trades():
    global current_trades_data
    try:
        data = request.get_json()
        
        # Extract parameters from request
        ticker = data.get('ticker')
        limit = int(data.get('limit', 100))
        min_ts = data.get('min_ts')
        max_ts = data.get('max_ts')
        fetch_all = data.get('fetchAll', False)
        
        # Set limit to maximum if fetch_all is True
        if fetch_all:
            limit = 1000
            # Don't use date filters when fetching all data
            min_ts = None
            max_ts = None
        else:
            # Convert min_ts and max_ts to integers if they exist
            if min_ts:
                min_ts = int(min_ts)
            if max_ts:
                max_ts = int(max_ts)
        
        print(f"Fetching trades with params: ticker={ticker}, limit={limit}, min_ts={min_ts}, max_ts={max_ts}, fetch_all={fetch_all}")
        
        # Call the Kalshi API client
        trades = get_all_trades(
            ticker=ticker,
            limit=limit,
            min_ts=min_ts,
            max_ts=max_ts
        )
        
        # Store data globally for analysis
        current_trades_data = trades
        
        return jsonify({
            'success': True,
            'data': trades,
            'count': len(trades)
        })
        
    except Exception as e:
        print(f"Error fetching trades: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to fetch all markets data
@app.route('/api/markets', methods=['GET', 'POST'])
def fetch_markets():
    global current_markets_data, organized_markets_data
    try:
        print("Fetching markets from Kalshi API...")
        
        # Get filter parameters from request
        filters = {}
        if request.method == 'POST':
            filters = request.get_json() or {}
            print(f"Using filters: {filters}")
        
        # Call the markets API client with filters
        markets = get_all_markets(**filters)
        
        # Store data globally
        current_markets_data = markets
        organized_markets_data = organize_markets_by_event(markets)
        
        # Get unique event tickers
        event_tickers = get_unique_event_tickers(markets)
        
        return jsonify({
            'success': True,
            'data': {
                'markets': markets,
                'event_tickers': event_tickers,
                'organized_markets': organized_markets_data,
                'total_markets': len(markets),
                'total_events': len(event_tickers)
            }
        })
        
    except Exception as e:
        print(f"Error fetching markets: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get event tickers
@app.route('/api/markets/events', methods=['GET'])
def get_events():
    global current_markets_data
    try:
        if not current_markets_data:
            return jsonify({
                'success': False,
                'error': 'No markets data available. Please fetch markets first.'
            }), 400
        
        event_tickers = get_unique_event_tickers(current_markets_data)
        
        return jsonify({
            'success': True,
            'data': event_tickers
        })
        
    except Exception as e:
        print(f"Error getting events: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get tickers for a specific event
@app.route('/api/markets/events/<event_ticker>/tickers', methods=['GET'])
def get_tickers_for_event(event_ticker):
    global current_markets_data, organized_markets_data
    try:
        if not current_markets_data:
            return jsonify({
                'success': False,
                'error': 'No markets data available. Please fetch markets first.'
            }), 400
        
        if event_ticker in organized_markets_data:
            markets_for_event = organized_markets_data[event_ticker]
            tickers = [market.get('ticker') for market in markets_for_event]
            
            return jsonify({
                'success': True,
                'data': {
                    'event_ticker': event_ticker,
                    'tickers': tickers,
                    'markets': markets_for_event,
                    'count': len(tickers)
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Event ticker "{event_ticker}" not found'
            }), 404
        
    except Exception as e:
        print(f"Error getting tickers for event {event_ticker}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get basic statistics
@app.route('/api/analysis/stats', methods=['GET'])
def get_stats():
    global current_trades_data
    try:
        if not current_trades_data:
            return jsonify({
                'success': False,
                'error': 'No data available. Please fetch trades first.'
            }), 400
        
        analyzer = TradingDataAnalyzer(current_trades_data)
        stats = analyzer.get_statistics()
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        print(f"Error getting stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get advanced metrics
@app.route('/api/analysis/metrics', methods=['GET'])
def get_metrics():
    global current_trades_data
    try:
        if not current_trades_data:
            return jsonify({
                'success': False,
                'error': 'No data available. Please fetch trades first.'
            }), 400
        
        analyzer = TradingDataAnalyzer(current_trades_data)
        metrics = analyzer.get_advanced_metrics()
        
        return jsonify({
            'success': True,
            'data': metrics
        })
        
    except Exception as e:
        print(f"Error getting metrics: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get specific chart
@app.route('/api/analysis/chart/<chart_type>', methods=['GET'])
def get_chart(chart_type):
    global current_trades_data
    try:
        if not current_trades_data:
            return jsonify({
                'success': False,
                'error': 'No data available. Please fetch trades first.'
            }), 400
        
        analyzer = TradingDataAnalyzer(current_trades_data)
        
        chart_methods = {
            'price': lambda: analyzer.create_price_chart('line'),
            'volume': analyzer.create_volume_chart,
            'side_analysis': analyzer.create_side_analysis,
            'heatmap': analyzer.create_heatmap,
            'price_distribution': analyzer.create_price_distribution,
            'time_series': analyzer.create_time_series_analysis
        }
        
        if chart_type not in chart_methods:
            return jsonify({
                'success': False,
                'error': f'Unknown chart type: {chart_type}'
            }), 400
        
        chart_data = chart_methods[chart_type]()
        
        if chart_data is None:
            return jsonify({
                'success': False,
                'error': 'Failed to generate chart'
            }), 500
        
        return jsonify({
            'success': True,
            'data': {
                'chart_type': chart_type,
                'image_data': chart_data
            }
        })
        
    except Exception as e:
        print(f"Error generating chart {chart_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get all analyses at once
@app.route('/api/analysis/all', methods=['GET'])
def get_all_analyses():
    global current_trades_data
    try:
        if not current_trades_data:
            return jsonify({
                'success': False,
                'error': 'No data available. Please fetch trades first.'
            }), 400
        
        analyzer = TradingDataAnalyzer(current_trades_data)
        analyses = analyzer.generate_all_analyses()
        
        return jsonify({
            'success': True,
            'data': analyses
        })
        
    except Exception as e:
        print(f"Error generating all analyses: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API endpoint to get all series categories
@app.route('/api/series/categories', methods=['GET'])
def api_get_series_categories():
    try:
        categories = get_all_categories()
        return jsonify({'success': True, 'data': categories})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint to get all series for a given category
@app.route('/api/series/category/<category>', methods=['GET'])
def api_get_series_by_category(category):
    try:
        series = get_series_by_category(category)
        return jsonify({'success': True, 'data': series})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API endpoint to get markets/tickers for a specific series
@app.route('/api/series/<series_ticker>/tickers', methods=['GET'])
def api_get_tickers_for_series(series_ticker):
    try:
        print(f"Fetching tickers for series: {series_ticker}")
        
        # Use the markets API to get markets filtered by series_ticker
        # Don't filter by status so we get all markets (active, finalized, etc.)
        markets = get_all_markets(series_ticker=series_ticker, status=None)
        
        print(f"Found {len(markets)} markets for series {series_ticker}")
        
        # Log the first market to see its structure
        if markets:
            print(f"First market structure: {markets[0]}")
            print(f"Available fields: {list(markets[0].keys())}")
        
        # Extract tickers from markets
        tickers = [market.get('ticker') for market in markets if market.get('ticker')]
        
        print(f"Extracted {len(tickers)} tickers: {tickers[:5]}...")  # Show first 5
        
        return jsonify({
            'success': True, 
            'data': {
                'series_ticker': series_ticker,
                'tickers': tickers,
                'markets': markets,
                'count': len(tickers)
            }
        })
    except Exception as e:
        print(f"Error in api_get_tickers_for_series: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Kalshi API Web Server...")
    print("Open http://localhost:5015 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5015) 