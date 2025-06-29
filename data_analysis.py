import pandas as pd
import numpy as np
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
            
        plt.figure(figsize=(12, 6))
        
        if chart_type == 'line':
            # Line chart of price over time
            plt.plot(self.df['timestamp'], self.df['price'], alpha=0.7)
            plt.title('Price Movement Over Time')
            plt.xlabel('Time')
            plt.ylabel('Price ($)')
            plt.xticks(rotation=45)
            
        elif chart_type == 'candlestick':
            # Simplified candlestick-like chart
            df_grouped = self.df.groupby(self.df['timestamp'].dt.date).agg({
                'price': ['min', 'max', 'first', 'last'],
                'quantity': 'sum'
            }).reset_index()
            
            for _, row in df_grouped.iterrows():
                date = row['timestamp']
                low = row[('price', 'min')]
                high = row[('price', 'max')]
                open_price = row[('price', 'first')]
                close_price = row[('price', 'last')]
                
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
            
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Volume over time
        volume_by_time = self.df.groupby(self.df['timestamp'].dt.date)['quantity'].sum()
        ax1.bar(volume_by_time.index, volume_by_time.values, alpha=0.7)
        ax1.set_title('Trading Volume by Date')
        ax1.set_ylabel('Volume')
        ax1.tick_params(axis='x', rotation=45)
        
        # Volume by hour
        volume_by_hour = self.df.groupby('hour')['quantity'].sum()
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
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Buy vs Sell count
        side_counts = self.df['side'].value_counts()
        ax1.pie(side_counts.values, labels=side_counts.index, autopct='%1.1f%%')
        ax1.set_title('Buy vs Sell Distribution')
        
        # Buy vs Sell volume
        side_volume = self.df.groupby('side')['quantity'].sum()
        ax2.bar(side_volume.index, side_volume.values, color=['green', 'red'])
        ax2.set_title('Buy vs Sell Volume')
        ax2.set_ylabel('Volume')
        
        # Price distribution by side
        buy_prices = self.df[self.df['side'] == 'buy']['price']
        sell_prices = self.df[self.df['side'] == 'sell']['price']
        
        ax3.hist(buy_prices, alpha=0.7, label='Buy', color='green', bins=20)
        ax3.hist(sell_prices, alpha=0.7, label='Sell', color='red', bins=20)
        ax3.set_title('Price Distribution by Side')
        ax3.set_xlabel('Price')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        
        # Average price by side
        avg_price_by_side = self.df.groupby('side')['price'].mean()
        ax4.bar(avg_price_by_side.index, avg_price_by_side.values, color=['green', 'red'])
        ax4.set_title('Average Price by Side')
        ax4.set_ylabel('Average Price ($)')
        
        plt.tight_layout()
        return self._save_chart()
    
    def create_heatmap(self):
        """Create trading activity heatmap"""
        if self.df.empty:
            return None
            
        # Create pivot table for heatmap
        df_copy = self.df.copy()
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        df_copy['day'] = df_copy['timestamp'].dt.day_name()
        
        heatmap_data = df_copy.groupby(['day', 'hour'])['quantity'].sum().unstack(fill_value=0)
        
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
            
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Price histogram
        ax1.hist(self.df['price'], bins=30, alpha=0.7, edgecolor='black')
        ax1.set_title('Price Distribution')
        ax1.set_xlabel('Price ($)')
        ax1.set_ylabel('Frequency')
        ax1.axvline(self.df['price'].mean(), color='red', linestyle='--', label=f'Mean: ${self.df["price"].mean():.2f}')
        ax1.axvline(self.df['price'].median(), color='green', linestyle='--', label=f'Median: ${self.df["price"].median():.2f}')
        ax1.legend()
        
        # Price box plot
        ax2.boxplot(self.df['price'])
        ax2.set_title('Price Box Plot')
        ax2.set_ylabel('Price ($)')
        
        plt.tight_layout()
        return self._save_chart()
    
    def create_time_series_analysis(self):
        """Create time series analysis"""
        if self.df.empty:
            return None
            
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Price over time with trend
        df_sorted = self.df.sort_values('timestamp')
        ax1.plot(df_sorted['timestamp'], df_sorted['price'], alpha=0.7)
        
        # Add trend line
        z = np.polyfit(range(len(df_sorted)), df_sorted['price'], 1)
        p = np.poly1d(z)
        ax1.plot(df_sorted['timestamp'], p(range(len(df_sorted))), "r--", alpha=0.8)
        ax1.set_title('Price Trend Analysis')
        ax1.set_ylabel('Price ($)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Volume over time
        volume_time = df_sorted.groupby(df_sorted['timestamp'].dt.date)['quantity'].sum()
        ax2.plot(volume_time.index, volume_time.values)
        ax2.set_title('Volume Trend')
        ax2.set_ylabel('Volume')
        ax2.tick_params(axis='x', rotation=45)
        
        # Price volatility (rolling standard deviation)
        if len(df_sorted) > 10:
            rolling_std = df_sorted['price'].rolling(window=10).std()
            ax3.plot(df_sorted['timestamp'], rolling_std)
            ax3.set_title('Price Volatility (10-period rolling std)')
            ax3.set_ylabel('Standard Deviation')
            ax3.tick_params(axis='x', rotation=45)
        
        # Trade frequency over time
        trade_freq = df_sorted.groupby(df_sorted['timestamp'].dt.date).size()
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
            
            # Time-based analysis
            if 'created_time' in self.df.columns:
                self.df['hour'] = self.df['created_time'].dt.hour
                self.df['day_of_week'] = self.df['created_time'].dt.day_name()
                
                metrics['hourly_distribution'] = self.df['hour'].value_counts().sort_index().to_dict()
                metrics['daily_distribution'] = self.df['day_of_week'].value_counts().to_dict()
            
            # Price analysis if available
            if 'yes_price' in self.df.columns and 'no_price' in self.df.columns:
                yes_prices = pd.to_numeric(self.df['yes_price'], errors='coerce')
                no_prices = pd.to_numeric(self.df['no_price'], errors='coerce')
                spread = yes_prices - no_prices
                
                # Price correlations
                metrics['price_correlation'] = yes_prices.corr(no_prices)
                
                # Volatility metrics
                metrics['yes_price_volatility'] = yes_prices.std()
                metrics['no_price_volatility'] = no_prices.std()
                metrics['spread_volatility'] = spread.std()
                
                # Price ranges
                metrics['yes_price_range'] = {
                    'min': yes_prices.min(),
                    'max': yes_prices.max(),
                    'range': yes_prices.max() - yes_prices.min()
                }
                metrics['no_price_range'] = {
                    'min': no_prices.min(),
                    'max': no_prices.max(),
                    'range': no_prices.max() - no_prices.min()
                }
                metrics['spread_range'] = {
                    'min': spread.min(),
                    'max': spread.max(),
                    'range': spread.max() - spread.min()
                }
            
            # Ticker analysis
            if 'ticker' in self.df.columns:
                ticker_counts = self.df['ticker'].value_counts()
                metrics['most_active_tickers'] = ticker_counts.head(5).to_dict()
                metrics['ticker_diversity'] = len(ticker_counts)
            
            # Taker side analysis
            if 'taker_side' in self.df.columns:
                side_counts = self.df['taker_side'].value_counts()
                metrics['taker_side_balance'] = side_counts.to_dict()
                if len(side_counts) == 2:
                    metrics['buy_sell_ratio'] = side_counts.iloc[0] / side_counts.iloc[1]
            
            # Convert NumPy types to native Python types
            return self._convert_numpy_types(metrics)
            
        except Exception as e:
            return {"error": f"Error calculating advanced metrics: {str(e)}"}
    
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