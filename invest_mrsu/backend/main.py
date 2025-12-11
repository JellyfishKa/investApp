"""
FastAPI Backend Application
Main entry point for the Invest MRSU ML API
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import numpy as np
import joblib
from pathlib import Path

from database.db import get_db, init_db, close_db
from database.models import StockData, Prediction
from services.moex import MOEXCollector
from services.importer import CSVImporter
from ml.model import LSTMStockModel
from ml.preprocessor import DataPreprocessor

# Initialize app
app = FastAPI(
    title="Invest MRSU ML API",
    description="Machine Learning API for stock price prediction",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class PredictionRequest(BaseModel):
    ticker: str
    period: str  # 'week', 'month', 'year'

class PredictionResponse(BaseModel):
    ticker: str
    current_price: float
    predicted_price: float
    confidence_low: Optional[float] = None
    confidence_high: Optional[float] = None
    change_percent: float
    prediction_date: datetime
    model_accuracy: Optional[float] = None

class HistoryResponse(BaseModel):
    ticker: str
    data: List[dict]

class UploadResponse(BaseModel):
    message: str
    records_imported: int


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Starting Invest MRSU ML API...")
    await init_db()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    await close_db()


# Endpoints
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Invest MRSU ML API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock_price(
    request: PredictionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Predict stock price
    
    Args:
        request: Prediction request with ticker and period
        
    Returns:
        Prediction with confidence intervals
    """
    try:
        ticker = request.ticker.upper()
        period = request.period.lower()
        
        # Check cache first
        from services.cache import get_cache
        cache = get_cache()
        cached_prediction = cache.get_prediction(ticker, period)
        
        if cached_prediction:
            return PredictionResponse(**cached_prediction)
        
        # Validate period
        period_days = {
            'week': 7,
            'month': 30,
            'year': 365
        }
        
        if period not in period_days:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid period. Must be one of: {list(period_days.keys())}"
            )
        
        target_days = period_days[period]
        
        # Load model
        model_path = Path("models") / f"{ticker}_model.keras"
        if not model_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Model not found for ticker {ticker}"
            )
        
        model = LSTMStockModel(ticker=ticker)
        model.load()
        
        # Load preprocessor
        preprocessor_path = Path("models") / f"{ticker}_preprocessor.pkl"
        if not preprocessor_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Preprocessor not found for ticker {ticker}"
            )
        
        preprocessor = joblib.load(preprocessor_path)
        
        # Load recent data
        df = await preprocessor.load_data(db)
        
        # Get current price (last close)
        current_price = float(df['close'].iloc[-1])
        
        # Prepare data for prediction
        df = preprocessor.create_technical_indicators(df)
        
        # Get last sequence
        feature_cols = preprocessor.feature_columns
        data = df[feature_cols].values
        scaled_data = preprocessor.scaler.transform(data)
        
        # Take last 60 days
        last_sequence = scaled_data[-60:]
        
        # Make prediction
        scaled_prediction = model.predict_single(last_sequence)
        
        # Convert back to actual price
        predicted_price = preprocessor.inverse_transform_price(scaled_prediction)
        
        # Calculate change percent
        change_percent = ((predicted_price - current_price) / current_price) * 100
        
        # Estimate confidence intervals (simplified - use ±10% for now)
        # In a real system, you'd calculate this from prediction uncertainty
        confidence_range = predicted_price * 0.1
        confidence_low = predicted_price - confidence_range
        confidence_high = predicted_price + confidence_range
        
        # Get model accuracy from training summary
        summary_path = Path("models") / "training_summary.json"
        model_accuracy = None
        if summary_path.exists():
            import json
            with open(summary_path) as f:
                summary = json.load(f)
                if ticker in summary and 'metrics' in summary[ticker]:
                    mape = summary[ticker]['metrics'].get('mape', 0)
                    model_accuracy = 100 - mape  # Convert MAPE to accuracy
        
        # Save prediction to database
        prediction_record = Prediction(
            ticker=ticker,
            prediction_date=datetime.now(),
            target_date=datetime.now() + timedelta(days=target_days),
            predicted_price=predicted_price,
            confidence_low=confidence_low,
            confidence_high=confidence_high,
            model_version="1.0"
        )
        db.add(prediction_record)
        await db.commit()
        
        # Prepare response
        response_data = {
            'ticker': ticker,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'confidence_low': confidence_low,
            'confidence_high': confidence_high,
            'change_percent': change_percent,
            'prediction_date': datetime.now() + timedelta(days=target_days),
            'model_accuracy': model_accuracy
        }
        
        # Cache the prediction
        cache.set_prediction(ticker, period, response_data)
        
        return PredictionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history/{ticker}", response_model=HistoryResponse)
async def get_stock_history(
    ticker: str,
    days: int = 365,
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical stock data
    
    Args:
        ticker: Stock ticker
        days: Number of days to retrieve
        
    Returns:
        Historical OHLCV data
    """
    try:
        ticker = ticker.upper()
        
        # Query data
        from sqlalchemy import select
        start_date = datetime.now() - timedelta(days=days)
        
        stmt = select(StockData).where(
            StockData.ticker == ticker,
            StockData.date >= start_date
        ).order_by(StockData.date)
        
        result = await db.execute(stmt)
        rows = result.scalars().all()
        
        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker {ticker}"
            )
        
        data = [{
            'date': row.date.isoformat(),
            'open': row.open,
            'close': row.close,
            'high': row.high,
            'low': row.low,
            'volume': row.volume
        } for row in rows]
        
        return HistoryResponse(ticker=ticker, data=data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"History error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/upload_csv", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    ticker: Optional[str] = None,
    data_type: str = "fundamental",
    db: AsyncSession = Depends(get_db)
):
    """
    Upload CSV file with fundamental or macro data
    
    Args:
        file: CSV file
        ticker: Stock ticker (required for fundamental data)
        data_type: 'fundamental' or 'macro'
        
    Returns:
        Upload confirmation
    """
    try:
        # Read file content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        importer = CSVImporter()
        
        if data_type == "fundamental":
            if not ticker:
                raise HTTPException(
                    status_code=400,
                    detail="Ticker required for fundamental data"
                )
            
            count = await importer.import_fundamental_data(
                db, ticker.upper(), csv_content
            )
        
        elif data_type == "macro":
            count = await importer.import_macro_data(db, csv_content)
        
        else:
            raise HTTPException(
                status_code=400,
                detail="data_type must be 'fundamental' or 'macro'"
            )
        
        return UploadResponse(
            message=f"Successfully imported {count} records",
            records_imported=count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/admin/update_moex")
async def update_moex_data(db: AsyncSession = Depends(get_db)):
    """
    Trigger MOEX data update for all tickers
    
    Returns:
        Update status
    """
    try:
        collector = MOEXCollector()
        await collector.update_all_tickers(db)
        
        return {
            "message": "MOEX data updated successfully",
            "tickers": collector.TICKERS,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"MOEX update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
