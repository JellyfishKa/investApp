"""
CSV Import Service
Handles uploading and importing fundamental and macro data from CSV files
"""
import pandas as pd
from io import StringIO
from typing import List
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import FundamentalData, MacroData
from datetime import datetime


class CSVImporter:
    """Service for importing data from CSV files"""
    
    @staticmethod
    async def import_fundamental_data(
        db: AsyncSession,
        ticker: str,
        csv_content: str
    ) -> int:
        """
        Import fundamental data from CSV
        
        Expected CSV format:
        Date,Revenue_bn,EBITDA_bn,Net_profit_bn,Debt_bn,Dividend
        2022-Q1,100.5,50.2,30.1,200.0,10.5
        
        Args:
            db: Database session
            ticker: Stock ticker
            csv_content: CSV file content as string
            
        Returns:
            Number of records imported
        """
        try:
            df = pd.read_csv(StringIO(csv_content))
            
            # Validate columns
            required_cols = ['Date', 'Revenue_bn', 'EBITDA_bn', 'Net_profit_bn', 'Debt_bn', 'Dividend']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"CSV must contain columns: {required_cols}")
            
            # Parse dates (handle Q1, Q2, Q3, Q4 format)
            df['date'] = df['Date'].apply(CSVImporter._parse_quarter_date)
            
            # Get existing dates
            stmt = select(FundamentalData.date).where(FundamentalData.ticker == ticker)
            result = await db.execute(stmt)
            existing_dates = {row[0] for row in result}
            
            # Filter new data
            new_data = df[~df['date'].isin(existing_dates)]
            
            if new_data.empty:
                logger.info(f"No new fundamental data for {ticker}")
                return 0
            
            # Insert records
            records = []
            for _, row in new_data.iterrows():
                record = FundamentalData(
                    ticker=ticker,
                    date=row['date'],
                    revenue_bn=float(row['Revenue_bn']),
                    ebitda_bn=float(row['EBITDA_bn']),
                    net_profit_bn=float(row['Net_profit_bn']),
                    debt_bn=float(row['Debt_bn']),
                    dividend=float(row['Dividend'])
                )
                records.append(record)
            
            db.add_all(records)
            await db.commit()
            
            logger.info(f"Imported {len(records)} fundamental records for {ticker}")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error importing fundamental data: {e}")
            raise
    
    @staticmethod
    async def import_macro_data(
        db: AsyncSession,
        csv_content: str
    ) -> int:
        """
        Import macro data from CSV
        
        Expected CSV format:
        Date,Oil_Brent_USD,USD_RUB,EUR_RUB,MOEX_Index,CB_Rate
        2024-01-01,75.5,75.2,85.1,3000.5,16.0
        
        Args:
            db: Database session
            csv_content: CSV file content as string
            
        Returns:
            Number of records imported
        """
        try:
            df = pd.read_csv(StringIO(csv_content))
            
            # Validate columns
            required_cols = ['Date', 'Oil_Brent_USD', 'USD_RUB', 'EUR_RUB', 'MOEX_Index', 'CB_Rate']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"CSV must contain columns: {required_cols}")
            
            df['date'] = pd.to_datetime(df['Date'])
            
            # Get existing dates
            stmt = select(MacroData.date)
            result = await db.execute(stmt)
            existing_dates = {row[0] for row in result}
            
            # Filter new data
            new_data = df[~df['date'].isin(existing_dates)]
            
            if new_data.empty:
                logger.info("No new macro data")
                return 0
            
            # Insert records
            records = []
            for _, row in new_data.iterrows():
                record = MacroData(
                    date=row['date'],
                    oil_brent_usd=float(row['Oil_Brent_USD']),
                    usd_rub=float(row['USD_RUB']),
                    eur_rub=float(row['EUR_RUB']),
                    moex_index=float(row['MOEX_Index']),
                    cb_rate=float(row['CB_Rate'])
                )
                records.append(record)
            
            db.add_all(records)
            await db.commit()
            
            logger.info(f"Imported {len(records)} macro records")
            return len(records)
            
        except Exception as e:
            logger.error(f"Error importing macro data: {e}")
            raise
    
    @staticmethod
    def _parse_quarter_date(quarter_str: str) -> datetime:
        """
        Parse quarter string to datetime
        Examples: 2022-Q1 -> 2022-03-31, 2022-Q2 -> 2022-06-30
        """
        year, quarter = quarter_str.split('-Q')
        year = int(year)
        quarter = int(quarter)
        
        quarter_end_months = {1: 3, 2: 6, 3: 9, 4: 12}
        month = quarter_end_months[quarter]
        
        # Last day of the quarter
        if month in [3, 6, 9]:
            day = 30
        else:
            day = 31
        
        return datetime(year, month, day)
