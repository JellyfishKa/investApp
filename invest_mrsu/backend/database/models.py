"""
Database models for Invest MRSU Backend
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from database.db import Base


class StockData(Base):
    """Historical stock price data"""
    __tablename__ = "stock_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ticker_date', 'ticker', 'date', unique=True),
    )


class FundamentalData(Base):
    """Fundamental company data (quarterly)"""
    __tablename__ = "fundamental_data"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # Quarter end date
    revenue_bn = Column(Float)
    ebitda_bn = Column(Float)
    net_profit_bn = Column(Float)
    debt_bn = Column(Float)
    dividend = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_fundamental_ticker_date', 'ticker', 'date', unique=True),
    )


class MacroData(Base):
    """Macroeconomic indicators"""
    __tablename__ = "macro_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, unique=True, index=True)
    oil_brent_usd = Column(Float)
    usd_rub = Column(Float)
    eur_rub = Column(Float)
    moex_index = Column(Float)
    cb_rate = Column(Float)  # Central Bank key rate
    created_at = Column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    """ML model predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), nullable=False, index=True)
    prediction_date = Column(DateTime, nullable=False)  # Date of prediction
    target_date = Column(DateTime, nullable=False)  # Date being predicted
    predicted_price = Column(Float, nullable=False)
    confidence_low = Column(Float)
    confidence_high = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_prediction_ticker_target', 'ticker', 'target_date'),
    )
