import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import base64
from io import BytesIO
import json

class TradingDataAnalyzer:
    def __init__(self, trades_data):
        """
        Initialize analyzer with trades data
        
        Args:
            trades_data: List of trade dictionaries from Kalshi API
        """
        self.trades_data = trades_data
        self.df = self._prepare_dataframe()
        
    def _convert_numpy_types(self, obj):
        """Convert NumPy types to native Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj
        
    def _prepare_dataframe(self):
        """Convert trades data to pandas DataFrame with proper data types"""
        if not self.trades_data:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(self.trades_data)
            
            # Convert timestamp column
            if 'created_time' in df.columns:
                df['created_time'] = pd.to_datetime(df['created_time'], errors='coerce')
            
            # Convert price columns to numeric
            if 'yes_price' in df.columns:
                df['yes_price'] = pd.to_numeric(df['yes_price'], errors='coerce')
                
            if 'no_price' in df.columns:
                df['no_price'] = pd.to_numeric(df['no_price'], errors='coerce')
            
            # Convert count to numeric if it exists
            if 'count' in df.columns:
                df['count'] = pd.to_numeric(df['count'], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error in _prepare_dataframe: {e}")
            return pd.DataFrame()
    
    def get_statistics(self):
        """Get basic statistics about the trading data"""
        if self.df.empty:
            return {"error": "No data available"}
        
        try:
            # Basic statistics
            stats = {
                "total_trades": len(self.df),
                "unique_tickers": self.df['ticker'].nunique() if 'ticker' in self.df.columns else 0,
            }
            
            # Date range if created_time exists
            if 'created_time' in self.df.columns:
                min_time = self.df['created_time'].min()
                max_time = self.df['created_time'].max()
                stats["date_range"] = {
                    "start": min_time.isoformat() if pd.notna(min_time) else None,
                    "end": max_time.isoformat() if pd.notna(max_time) else None
                }
            else:
                stats["date_range"] = {"start": None, "end": None}
            
            # Taker side distribution
            if 'taker_side' in self.df.columns:
                stats["taker_side_distribution"] = self.df['taker_side'].value_counts().to_dict()
            else:
                stats["taker_side_distribution"] = {}
            
            # Ticker distribution
            if 'ticker' in self.df.columns:
                stats["ticker_distribution"] = self.df['ticker'].value_counts().head(10).to_dict()
            else:
                stats["ticker_distribution"] = {}
            
            # Price statistics if available
            if 'yes_price' in self.df.columns and 'no_price' in self.df.columns:
                # Convert to float explicitly
                yes_prices = self.df['yes_price'].astype(float)
                no_prices = self.df['no_price'].astype(float)
                
                # Calculate spread
                spread = yes_prices - no_prices
                
                stats.update({
                    "yes_price_stats": {
                        "mean": float(yes_prices.mean()),
                        "median": float(yes_prices.median()),
                        "min": float(yes_prices.min()),
                        "max": float(yes_prices.max()),
                        "std": float(yes_prices.std())
                    },
                    "no_price_stats": {
                        "mean": float(no_prices.mean()),
                        "median": float(no_prices.median()),
                        "min": float(no_prices.min()),
                        "max": float(no_prices.max()),
                        "std": float(no_prices.std())
                    },
                    "spread_stats": {
                        "mean": float(spread.mean()),
                        "median": float(spread.median()),
                        "min": float(spread.min()),
                        "max": float(spread.max()),
                        "std": float(spread.std())
                    }
                })
            else:
                stats.update({
                    "yes_price_stats": {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0},
                    "no_price_stats": {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0},
                    "spread_stats": {"mean": 0, "median": 0, "min": 0, "max": 0, "std": 0}
                })
            
            # Convert NumPy types to native Python types
            return self._convert_numpy_types(stats)
            
        except Exception as e:
            return {"error": f"Error calculating statistics: {str(e)}"}
    
    def create_price_chart(self, chart_type='line'):
        """Create price movement chart"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'created_time' not in self.df.columns or 'yes_price' not in self.df.columns:
            return None
            
        plt.figure(figsize=(12, 6))
        
        if chart_type == 'line':
            # Line chart of price over time
            plt.plot(self.df['created_time'], self.df['yes_price'], alpha=0.7)
            plt.title('Yes Price Movement Over Time')
            plt.xlabel('Time')
            plt.ylabel('Yes Price ($)')
            plt.xticks(rotation=45)
            
        elif chart_type == 'candlestick':
            # Simplified candlestick-like chart
            df_grouped = self.df.groupby(self.df['created_time'].dt.date).agg({
                'yes_price': ['min', 'max', 'first', 'last'],
                'count': 'sum'
            }).reset_index()
            
            for _, row in df_grouped.iterrows():
                date = row['created_time']
                low = row[('yes_price', 'min')]
                high = row[('yes_price', 'max')]
                open_price = row[('yes_price', 'first')]
                close_price = row[('yes_price', 'last')]
                
                # Draw candlestick
                color = 'green' if close_price >= open_price else 'red'
                plt.plot([date, date], [low, high], color='black', linewidth=1)
                plt.plot([date, date], [open_price, close_price], color=color, linewidth=3)
        
        plt.grid(True, alpha=0.3)
        return self._save_chart()
    
    def create_volume_chart(self):
        """Create volume analysis chart"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'created_time' not in self.df.columns or 'count' not in self.df.columns:
            return None
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Volume over time
        volume_by_time = self.df.groupby(self.df['created_time'].dt.date)['count'].sum()
        ax1.bar(volume_by_time.index, volume_by_time.values, alpha=0.7)
        ax1.set_title('Trading Volume by Date')
        ax1.set_ylabel('Volume')
        ax1.tick_params(axis='x', rotation=45)
        
        # Volume by hour
        if 'created_time' in self.df.columns:
            self.df['hour'] = self.df['created_time'].dt.hour
            volume_by_hour = self.df.groupby('hour')['count'].sum()
            ax2.bar(volume_by_hour.index, volume_by_hour.values, alpha=0.7)
            ax2.set_title('Trading Volume by Hour of Day')
            ax2.set_xlabel('Hour')
            ax2.set_ylabel('Volume')
        
        plt.tight_layout()
        return self._save_chart()
    
    def create_side_analysis(self):
        """Create buy/sell side analysis"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'taker_side' not in self.df.columns or 'yes_price' not in self.df.columns or 'count' not in self.df.columns:
            return None
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Buy vs Sell count
        side_counts = self.df['taker_side'].value_counts()
        ax1.pie(side_counts.values, labels=side_counts.index, autopct='%1.1f%%')
        ax1.set_title('Buy vs Sell Distribution')
        
        # Buy vs Sell volume
        side_volume = self.df.groupby('taker_side')['count'].sum()
        ax2.bar(side_volume.index, side_volume.values, color=['green', 'red'])
        ax2.set_title('Buy vs Sell Volume')
        ax2.set_ylabel('Volume')
        
        # Price distribution by side
        buy_prices = self.df[self.df['taker_side'] == 'buy']['yes_price']
        sell_prices = self.df[self.df['taker_side'] == 'sell']['yes_price']
        
        ax3.hist(buy_prices, alpha=0.7, label='Buy', color='green', bins=20)
        ax3.hist(sell_prices, alpha=0.7, label='Sell', color='red', bins=20)
        ax3.set_title('Price Distribution by Side')
        ax3.set_xlabel('Price')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        
        # Average price by side
        avg_price_by_side = self.df.groupby('taker_side')['yes_price'].mean()
        ax4.bar(avg_price_by_side.index, avg_price_by_side.values, color=['green', 'red'])
        ax4.set_title('Average Price by Side')
        ax4.set_ylabel('Average Price ($)')
        
        plt.tight_layout()
        return self._save_chart()
    
    def create_heatmap(self):
        """Create trading activity heatmap"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'created_time' not in self.df.columns or 'count' not in self.df.columns:
            return None
            
        # Create pivot table for heatmap
        df_copy = self.df.copy()
        df_copy['hour'] = df_copy['created_time'].dt.hour
        df_copy['day'] = df_copy['created_time'].dt.day_name()
        
        heatmap_data = df_copy.groupby(['day', 'hour'])['count'].sum().unstack(fill_value=0)
        
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd')
        plt.title('Trading Activity Heatmap (Volume by Day/Hour)')
        plt.xlabel('Hour of Day')
        plt.ylabel('Day of Week')
        
        return self._save_chart()
    
    def create_price_distribution(self):
        """Create price distribution analysis"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'yes_price' not in self.df.columns:
            return None
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Price histogram
        ax1.hist(self.df['yes_price'], bins=30, alpha=0.7, edgecolor='black')
        ax1.set_title('Yes Price Distribution')
        ax1.set_xlabel('Yes Price ($)')
        ax1.set_ylabel('Frequency')
        ax1.axvline(self.df['yes_price'].mean(), color='red', linestyle='--', label=f'Mean: ${self.df["yes_price"].mean():.2f}')
        ax1.axvline(self.df['yes_price'].median(), color='green', linestyle='--', label=f'Median: ${self.df["yes_price"].median():.2f}')
        ax1.legend()
        
        # Price box plot
        ax2.boxplot(self.df['yes_price'])
        ax2.set_title('Yes Price Box Plot')
        ax2.set_ylabel('Yes Price ($)')
        
        plt.tight_layout()
        return self._save_chart()
    
    def create_time_series_analysis(self):
        """Create time series analysis"""
        if self.df.empty:
            return None
            
        # Check if required columns exist
        if 'created_time' not in self.df.columns or 'yes_price' not in self.df.columns or 'count' not in self.df.columns:
            return None
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Price over time with trend
        df_sorted = self.df.sort_values('created_time')
        ax1.plot(df_sorted['created_time'], df_sorted['yes_price'], alpha=0.7)
        
        # Add trend line
        z = np.polyfit(range(len(df_sorted)), df_sorted['yes_price'], 1)
        p = np.poly1d(z)
        ax1.plot(df_sorted['created_time'], p(range(len(df_sorted))), "r--", alpha=0.8)
        ax1.set_title('Yes Price Trend Analysis')
        ax1.set_ylabel('Yes Price ($)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Volume over time
        volume_time = df_sorted.groupby(df_sorted['created_time'].dt.date)['count'].sum()
        ax2.plot(volume_time.index, volume_time.values)
        ax2.set_title('Volume Trend')
        ax2.set_ylabel('Volume')
        ax2.tick_params(axis='x', rotation=45)
        
        # Price volatility (rolling standard deviation)
        if len(df_sorted) > 10:
            rolling_std = df_sorted['yes_price'].rolling(window=10).std()
            ax3.plot(df_sorted['created_time'], rolling_std)
            ax3.set_title('Yes Price Volatility (10-period rolling std)')
            ax3.set_ylabel('Standard Deviation')
            ax3.tick_params(axis='x', rotation=45)
        
        # Trade frequency over time
        trade_freq = df_sorted.groupby(df_sorted['created_time'].dt.date).size()
        ax4.plot(trade_freq.index, trade_freq.values)
        ax4.set_title('Trade Frequency')
        ax4.set_ylabel('Number of Trades')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return self._save_chart()
    
    def get_advanced_metrics(self):
        """Get advanced trading metrics and analysis"""
        if self.df.empty:
            return {"error": "No data available"}
        
        try:
            metrics = {}
            
            # Price analysis if available
            if 'yes_price' in self.df.columns and 'no_price' in self.df.columns:
                yes_prices = pd.to_numeric(self.df['yes_price'], errors='coerce')
                no_prices = pd.to_numeric(self.df['no_price'], errors='coerce')
                
                # Remove NaN values for calculations
                yes_prices_clean = yes_prices.dropna()
                no_prices_clean = no_prices.dropna()
                
                if len(yes_prices_clean) > 0:
                    # Price volatility (standard deviation)
                    metrics['price_volatility'] = float(yes_prices_clean.std())
                    
                    # Price skewness
                    metrics['price_skewness'] = float(yes_prices_clean.skew())
                    
                    # Price kurtosis
                    metrics['price_kurtosis'] = float(yes_prices_clean.kurtosis())
                    
                    # Price spread (difference between yes and no prices)
                    if len(no_prices_clean) > 0:
                        spread = yes_prices_clean - no_prices_clean
                        metrics['price_spread'] = float(spread.mean())
                
                # Volume weighted average price (VWAP)
                if 'count' in self.df.columns:
                    count = pd.to_numeric(self.df['count'], errors='coerce')
                    vwap_numerator = (yes_prices * count).sum()
                    vwap_denominator = count.sum()
                    if vwap_denominator > 0:
                        metrics['volume_weighted_avg_price'] = float(vwap_numerator / vwap_denominator)
                    else:
                        metrics['volume_weighted_avg_price'] = 0.0
                else:
                    metrics['volume_weighted_avg_price'] = 0.0
            
            # Trade size analysis
            if 'count' in self.df.columns:
                count = pd.to_numeric(self.df['count'], errors='coerce')
                count_clean = count.dropna()
                
                if len(count_clean) > 0:
                    metrics['avg_trade_size'] = float(count_clean.mean())
                    metrics['largest_trade'] = float(count_clean.max())
                else:
                    metrics['avg_trade_size'] = 0.0
                    metrics['largest_trade'] = 0.0
            else:
                metrics['avg_trade_size'] = 0.0
                metrics['largest_trade'] = 0.0
            
            # Trading intensity (trades per hour)
            if 'created_time' in self.df.columns:
                # Calculate total hours in the dataset
                time_range = self.df['created_time'].max() - self.df['created_time'].min()
                total_hours = time_range.total_seconds() / 3600
                
                if total_hours > 0:
                    metrics['trading_intensity'] = float(len(self.df) / total_hours)
                else:
                    metrics['trading_intensity'] = 0.0
            else:
                metrics['trading_intensity'] = 0.0
            
            # Taker side analysis for buy/sell ratio
            if 'taker_side' in self.df.columns:
                side_counts = self.df['taker_side'].value_counts()
                if len(side_counts) >= 2:
                    # Calculate ratio of first side to second side
                    metrics['buy_sell_ratio'] = float(side_counts.iloc[0] / side_counts.iloc[1])
                else:
                    metrics['buy_sell_ratio'] = 1.0  # Default to 1 if only one side
            else:
                metrics['buy_sell_ratio'] = 1.0
            
            # Set default values for any missing metrics
            default_metrics = {
                'price_volatility': 0.0,
                'price_skewness': 0.0,
                'price_kurtosis': 0.0,
                'avg_trade_size': 0.0,
                'largest_trade': 0.0,
                'volume_weighted_avg_price': 0.0,
                'buy_sell_ratio': 1.0,
                'price_spread': 0.0,
                'trading_intensity': 0.0
            }
            
            # Ensure all expected metrics are present
            for key, default_value in default_metrics.items():
                if key not in metrics:
                    metrics[key] = default_value
            
            # Convert NumPy types to native Python types
            return self._convert_numpy_types(metrics)
            
        except Exception as e:
            print(f"Error in get_advanced_metrics: {e}")
            # Return default values on error
            return {
                'price_volatility': 0.0,
                'price_skewness': 0.0,
                'price_kurtosis': 0.0,
                'avg_trade_size': 0.0,
                'largest_trade': 0.0,
                'volume_weighted_avg_price': 0.0,
                'buy_sell_ratio': 1.0,
                'price_spread': 0.0,
                'trading_intensity': 0.0,
                'error': f"Error calculating advanced metrics: {str(e)}"
            }
    
    def _save_chart(self):
        """Save matplotlib chart to base64 string"""
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        
        return base64.b64encode(image_png).decode()
    
    def generate_all_analyses(self):
        """Generate all analyses and return as JSON"""
        analyses = {
            'basic_stats': self.get_statistics(),
            'advanced_metrics': self.get_advanced_metrics(),
            'charts': {
                'price_chart': self.create_price_chart('line'),
                'volume_chart': self.create_volume_chart(),
                'side_analysis': self.create_side_analysis(),
                'heatmap': self.create_heatmap(),
                'price_distribution': self.create_price_distribution(),
                'time_series': self.create_time_series_analysis()
            }
        }
        
        return analyses 