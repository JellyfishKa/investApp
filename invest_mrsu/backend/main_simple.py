"""
Simple main.py для тестирования БЕЗ PostgreSQL
Использует SQLite вместо PostgreSQL
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import numpy as np

# Initialize app
app = FastAPI(
    title="Invest MRSU ML API (SQLite)",
    description="ML API для тестирования с SQLite",
    version="1.0.0-sqlite"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionRequest(BaseModel):
    ticker: str
    period: str

class PredictionResponse(BaseModel):
    ticker: str
    current_price: float
    predicted_price: float
    confidence_low: float
    confidence_high: float
    change_percent: float
    prediction_date: datetime
    model_accuracy: float = None

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "Invest MRSU ML API (SQLite Test Mode)",
        "version": "1.0.0-sqlite",
        "timestamp": datetime.now().isoformat(),
        "note": "Using mock predictions - no database required"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock_price(request: PredictionRequest):
    """
    Mock predictions для тестирования
    """
    ticker = request.ticker.upper()
    period = request.period.lower()
    
    # Validate period
    period_days = {
        'week': 7,
        'month': 30,
        'year': 365
    }
    
    if period not in period_days:
        return {"error": f"Invalid period. Must be one of: {list(period_days.keys())}"}
    
    target_days = period_days[period]
    
    # Mock current price
    base_prices = {
        'GAZP': 173.50,
        'GAZP-P': 155.20,
        'SIBN': 450.30,
        'GCHE': 1250.00,
        'MRKZ': 0.85
    }
    
    current_price = base_prices.get(ticker, 100.0)
    
    # Generate mock prediction (random walk with slight upward bias)
    days_factor = target_days / 30.0
    change = np.random.randn() * 5 * days_factor + 2 * days_factor
    predicted_price = current_price * (1 + change / 100)
    
    # Confidence interval
    confidence_range = predicted_price * 0.1
    confidence_low = predicted_price - confidence_range
    confidence_high = predicted_price + confidence_range
    
    # Change percent
    change_percent = ((predicted_price - current_price) / current_price) * 100
    
    return PredictionResponse(
        ticker=ticker,
        current_price=current_price,
        predicted_price=predicted_price,
        confidence_low=confidence_low,
        confidence_high=confidence_high,
        change_percent=change_percent,
        prediction_date=datetime.now() + timedelta(days=target_days),
        model_accuracy=85.5  # Mock accuracy
    )

@app.get("/history/{ticker}")
async def get_history(ticker: str, days: int = 365):
    """
    Mock historical data
    """
    # Generate mock history
    base_prices = {
        'GAZP': 173.50,
        'SIBN': 450.30,
        'GCHE': 1250.00,
    }
    
    base_price = base_prices.get(ticker.upper(), 100.0)
    
    data = []
    for i in range(days):
        date = datetime.now() - timedelta(days=days - i - 1)
        # Random walk
        price = base_price + np.random.randn() * 5
        data.append({
            'date': date.isoformat(),
            'open': price + np.random.randn(),
            'close': price,
            'high': price + abs(np.random.randn() * 2),
            'low': price - abs(np.random.randn() * 2),
            'volume': 1000000 + int(np.random.randn() * 100000)
        })
    
    return {
        'ticker': ticker.upper(),
        'data': data
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Запуск тестового сервера (БЕЗ PostgreSQL)")
    print("=" * 60)
    print("API будет доступен по адресу: http://localhost:8000")
    print("Документация: http://localhost:8000/docs")
    print("=" * 60)
    print("\n💡 Это тестовая версия с mock данными")
    print("   Для полной версии нужен PostgreSQL\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
