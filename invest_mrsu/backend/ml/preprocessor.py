"""
Data Preprocessor for ML Models
Handles data cleaning, normalization, and feature engineering
"""
import pandas as pd
import numpy as np
from typing import Tuple, Optional
from sklearn.preprocessing import MinMaxScaler
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import StockData, FundamentalData, MacroData
from datetime import datetime, timedelta


class DataPreprocessor:
    """Preprocessor for stock data with technical indicators"""
    
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.feature_columns = []
    
    async def load_data(
        self, 
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load stock data from database
        
        Args:
            db: Database session
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            DataFrame with stock data
        """
        stmt = select(StockData).where(StockData.ticker == self.ticker)
        
        if start_date:
            stmt = stmt.where(StockData.date >= start_date)
        if end_date:
            stmt = stmt.where(StockData.date <= end_date)
        
        stmt = stmt.order_by(StockData.date)
        
        result = await db.execute(stmt)
        rows = result.scalars().all()
        
        if not rows:
            raise ValueError(f"No data found for {self.ticker}")
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'date': row.date,
            'open': row.open,
            'close': row.close,
            'high': row.high,
            'low': row.low,
            'volume': row.volume
        } for row in rows])
        
        logger.info(f"Loaded {len(df)} rows for {self.ticker}")
        return df
    
    def create_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create technical indicators
        
        Indicators:
        - Moving Averages (MA): 7, 30, 90 days
        - Relative Strength Index (RSI): 14 days
        - MACD (Moving Average Convergence Divergence)
        - Bollinger Bands
        - Price momentum
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicators
        """
        df = df.copy()
        
        # Moving Averages
        df['ma_7'] = df['close'].rolling(window=7, min_periods=1).mean()
        df['ma_30'] = df['close'].rolling(window=30, min_periods=1).mean()
        df['ma_90'] = df['close'].rolling(window=90, min_periods=1).mean()
        
        # RSI (Relative Strength Index)
        df['rsi'] = self._calculate_rsi(df['close'], period=14)
        
        # MACD
        df['macd'], df['macd_signal'] = self._calculate_macd(df['close'])
        
        # Bollinger Bands
        df['bb_upper'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'])
        
        # Price momentum (% change)
        df['momentum_1d'] = df['close'].pct_change(1)
        df['momentum_7d'] = df['close'].pct_change(7)
        
        # Volume change
        df['volume_change'] = df['volume'].pct_change(1)
        
        # Price range (high - low)
        df['price_range'] = (df['high'] - df['low']) / df['close']
        
        # Fill NaN values (from rolling calculations)
        df = df.fillna(method='bfill').fillna(0)
        
        logger.info(f"Created technical indicators for {self.ticker}")
        return df
    
    def prepare_sequences(
        self,
        df: pd.DataFrame,
        sequence_length: int = 60,
        target_days: int = 30
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare sequences for LSTM training
        
        Args:
            df: DataFrame with features
            sequence_length: Number of days to look back
            target_days: Number of days to predict ahead
            
        Returns:
            X (sequences), y (targets)
        """
        # Select feature columns
        feature_cols = [
            'open', 'high', 'low', 'close', 'volume',
            'ma_7', 'ma_30', 'ma_90',
            'rsi', 'macd', 'macd_signal',
            'bb_upper', 'bb_lower',
            'momentum_1d', 'momentum_7d',
            'volume_change', 'price_range'
        ]
        
        self.feature_columns = feature_cols
        
        # Extract features
        data = df[feature_cols].values
        
        # Normalize data
        scaled_data = self.scaler.fit_transform(data)
        
        X, y = [], []
        
        for i in range(sequence_length, len(scaled_data) - target_days):
            # Input sequence (past sequence_length days)
            X.append(scaled_data[i - sequence_length:i])
            
            # Target (close price after target_days)
            # We're predicting the close price, which is index 3
            target_idx = i + target_days
            if target_idx < len(scaled_data):
                y.append(scaled_data[target_idx, 3])  # close price
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Prepared {len(X)} sequences (shape: {X.shape})")
        return X, y
    
    def inverse_transform_price(self, scaled_price: float) -> float:
        """
        Convert scaled price back to actual price
        
        Args:
            scaled_price: Normalized price value
            
        Returns:
            Actual price
        """
        # Create dummy array with all features
        dummy = np.zeros((1, len(self.feature_columns)))
        dummy[0, 3] = scaled_price  # close price is at index 3
        
        # Inverse transform
        actual = self.scaler.inverse_transform(dummy)
        return actual[0, 3]
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def _calculate_macd(
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD and signal line"""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        
        return macd, signal_line
    
    @staticmethod
    def _calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = ma + (std * std_dev)
        lower_band = ma - (std * std_dev)
        
        return upper_band, lower_band
    
    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Split data into train/validation/test sets
        
        Args:
            X: Input sequences
            y: Target values
            train_ratio: Ratio for training set
            val_ratio: Ratio for validation set
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test
        """
        n_samples = len(X)
        
        train_end = int(n_samples * train_ratio)
        val_end = int(n_samples * (train_ratio + val_ratio))
        
        X_train = X[:train_end]
        y_train = y[:train_end]
        
        X_val = X[train_end:val_end]
        y_val = y[train_end:val_end]
        
        X_test = X[val_end:]
        y_test = y[val_end:]
        
        logger.info(f"Split: Train={len(X_train)}, Val={len(X_val)}, Test={len(X_test)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
