from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from kalshi_api_client import get_all_trades
from data_analysis import TradingDataAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variable to store current data
current_trades_data = []

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
        
        # Convert min_ts and max_ts to integers if they exist
        if min_ts:
            min_ts = int(min_ts)
        if max_ts:
            max_ts = int(max_ts)
        
        # Set limit to maximum if fetch_all is True
        if fetch_all:
            limit = 1000
        
        print(f"Fetching trades with params: ticker={ticker}, limit={limit}, min_ts={min_ts}, max_ts={max_ts}")
        
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

if __name__ == '__main__':
    print("Starting Kalshi API Web Server...")
    print("Open http://localhost:5015 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5015) 