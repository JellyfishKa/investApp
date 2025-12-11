"""
MOEX Data Collector Service
Fetches historical and current stock data from Moscow Exchange
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import StockData, MacroData
import time


class MOEXCollector:
    """Collector for MOEX stock data"""
    
    BASE_URL = 'https://iss.moex.com/iss'
    TICKERS = ['GAZP', 'GAZP-p', 'SIBN', 'GCHE', 'MRKZ']
    
    def __init__(self):
        self.session = requests.Session()
    
    def fetch_history(
        self, 
        ticker: str, 
        start_date: str, 
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical data for a ticker
        
        Args:
            ticker: Stock ticker (e.g., 'GAZP')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            DataFrame with columns: date, open, close, high, low, volume
        """
        logger.info(f"Fetching {ticker} data from {start_date} to {end_date}")
        
        url = f"{self.BASE_URL}/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
        
        params = {
            'from': start_date,
            'till': end_date,
        }
        
        all_data = []
        start = 0
        
        while True:
            params['start'] = start
            
            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                history = data['history']['data']
                
                if not history:
                    break
                
                all_data.extend(history)
                start += len(history)
                
                # Rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {e}")
                break
        
        if not all_data:
            logger.warning(f"No data found for {ticker}")
            return pd.DataFrame()
        
        # Convert to DataFrame
        columns = data['history']['columns']
        df = pd.DataFrame(all_data, columns=columns)
        
        # Select and rename columns
        df = df[['TRADEDATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']]
        df.columns = ['date', 'open', 'close', 'high', 'low', 'volume']
        
        # Convert types
        df['date'] = pd.to_datetime(df['date'])
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Remove rows with missing prices
        df = df.dropna(subset=['close'])
        
        logger.info(f"Fetched {len(df)} records for {ticker}")
        return df
    
    async def save_to_db(
        self, 
        db: AsyncSession, 
        ticker: str, 
        df: pd.DataFrame
    ):
        """
        Save stock data to database
        
        Args:
            db: Database session
            ticker: Stock ticker
            df: DataFrame with stock data
        """
        if df.empty:
            logger.warning(f"No data to save for {ticker}")
            return
        
        # Get existing dates to avoid duplicates
        stmt = select(StockData.date).where(StockData.ticker == ticker)
        result = await db.execute(stmt)
        existing_dates = {row[0].date() for row in result}
        
        # Filter out existing dates
        new_data = df[~df['date'].dt.date.isin(existing_dates)]
        
        if new_data.empty:
            logger.info(f"No new data to save for {ticker}")
            return
        
        # Insert new records
        records = []
        for _, row in new_data.iterrows():
            record = StockData(
                ticker=ticker,
                date=row['date'],
                open=row['open'],
                close=row['close'],
                high=row['high'],
                low=row['low'],
                volume=row['volume']
            )
            records.append(record)
        
        db.add_all(records)
        await db.commit()
        
        logger.info(f"Saved {len(records)} new records for {ticker}")
    
    async def update_all_tickers(
        self, 
        db: AsyncSession,
        days_back: int = 730  # 2 years by default
    ):
        """
        Update data for all tickers
        
        Args:
            db: Database session
            days_back: Number of days to fetch from today
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        for ticker in self.TICKERS:
            try:
                df = self.fetch_history(ticker, start_str, end_str)
                await self.save_to_db(db, ticker, df)
            except Exception as e:
                logger.error(f"Failed to update {ticker}: {e}")
        
        logger.info("All tickers updated successfully")
