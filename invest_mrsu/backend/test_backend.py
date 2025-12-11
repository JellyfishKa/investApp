"""
Unit and Integration Tests for Backend
"""
import pytest
import asyncio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.db import Base
from database.models import StockData, FundamentalData, MacroData, Prediction
from services.moex import MOEXCollector
from services.importer import CSVImporter
from ml.preprocessor import DataPreprocessor
from ml.model import LSTMStockModel


# Test database URL (in-memory SQLite)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_db():
    """Create test database"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=NullPool
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture
async def sample_stock_data(test_db: AsyncSession):
    """Create sample stock data for testing"""
    # Generate 100 days of sample data
    dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
    base_price = 173.50
    
    for i, date in enumerate(dates):
        # Simulate price movement
        price = base_price + np.random.randn() * 5 + i * 0.1
        
        record = StockData(
            ticker='GAZP',
            date=date,
            open=price + np.random.randn() * 2,
            close=price,
            high=price + abs(np.random.randn() * 3),
            low=price - abs(np.random.randn() * 3),
            volume=1000000 + np.random.randint(-100000, 100000)
        )
        test_db.add(record)
    
    await test_db.commit()
    return True


# Tests for Database Models
@pytest.mark.asyncio
async def test_stock_data_creation(test_db: AsyncSession):
    """Test creating stock data record"""
    record = StockData(
        ticker='GAZP',
        date=datetime.now(),
        open=173.0,
        close=173.5,
        high=174.0,
        low=172.5,
        volume=1000000
    )
    
    test_db.add(record)
    await test_db.commit()
    
    from sqlalchemy import select
    stmt = select(StockData).where(StockData.ticker == 'GAZP')
    result = await test_db.execute(stmt)
    saved_record = result.scalars().first()
    
    assert saved_record is not None
    assert saved_record.ticker == 'GAZP'
    assert saved_record.close == 173.5


@pytest.mark.asyncio
async def test_fundamental_data_creation(test_db: AsyncSession):
    """Test creating fundamental data record"""
    record = FundamentalData(
        ticker='GAZP',
        date=datetime(2024, 3, 31),
        revenue_bn=100.5,
        ebitda_bn=50.2,
        net_profit_bn=30.1,
        debt_bn=200.0,
        dividend=10.5
    )
    
    test_db.add(record)
    await test_db.commit()
    
    from sqlalchemy import select
    stmt = select(FundamentalData).where(FundamentalData.ticker == 'GAZP')
    result = await test_db.execute(stmt)
    saved_record = result.scalars().first()
    
    assert saved_record is not None
    assert saved_record.revenue_bn == 100.5


# Tests for CSV Importer
@pytest.mark.asyncio
async def test_csv_import_fundamental(test_db: AsyncSession):
    """Test importing fundamental data from CSV"""
    csv_content = """Date,Revenue_bn,EBITDA_bn,Net_profit_bn,Debt_bn,Dividend
2022-Q1,100.5,50.2,30.1,200.0,10.5
2022-Q2,105.0,52.0,32.0,195.0,11.0
"""
    
    importer = CSVImporter()
    count = await importer.import_fundamental_data(test_db, 'GAZP', csv_content)
    
    assert count == 2


@pytest.mark.asyncio
async def test_csv_import_macro(test_db: AsyncSession):
    """Test importing macro data from CSV"""
    csv_content = """Date,Oil_Brent_USD,USD_RUB,EUR_RUB,MOEX_Index,CB_Rate
2024-01-01,75.5,75.2,85.1,3000.5,16.0
2024-01-02,76.0,75.5,85.5,3010.0,16.0
"""
    
    importer = CSVImporter()
    count = await importer.import_macro_data(test_db, csv_content)
    
    assert count == 2


# Tests for Data Preprocessor
@pytest.mark.asyncio
async def test_preprocessor_load_data(test_db: AsyncSession, sample_stock_data):
    """Test loading data from database"""
    preprocessor = DataPreprocessor('GAZP')
    df = await preprocessor.load_data(test_db)
    
    assert len(df) == 100
    assert 'close' in df.columns
    assert df['close'].notna().all()


@pytest.mark.asyncio
async def test_preprocessor_technical_indicators(test_db: AsyncSession, sample_stock_data):
    """Test creating technical indicators"""
    preprocessor = DataPreprocessor('GAZP')
    df = await preprocessor.load_data(test_db)
    df = preprocessor.create_technical_indicators(df)
    
    # Check that indicators are created
    assert 'ma_7' in df.columns
    assert 'ma_30' in df.columns
    assert 'rsi' in df.columns
    assert 'macd' in df.columns
    assert 'bb_upper' in df.columns
    
    # Check no NaN values after filling
    assert df['ma_7'].notna().all()


@pytest.mark.asyncio
async def test_preprocessor_prepare_sequences(test_db: AsyncSession, sample_stock_data):
    """Test preparing sequences for LSTM"""
    preprocessor = DataPreprocessor('GAZP')
    df = await preprocessor.load_data(test_db)
    df = preprocessor.create_technical_indicators(df)
    
    X, y = preprocessor.prepare_sequences(df, sequence_length=10, target_days=5)
    
    # Check shapes
    assert len(X) > 0
    assert X.shape[1] == 10  # sequence_length
    assert X.shape[2] == 17  # num_features
    assert len(y) == len(X)


# Tests for LSTM Model
def test_model_build():
    """Test building LSTM model"""
    model = LSTMStockModel(ticker='GAZP', sequence_length=60, num_features=17)
    keras_model = model.build_model()
    
    assert keras_model is not None
    assert len(keras_model.layers) > 0
    
    # Check input shape
    assert keras_model.input_shape == (None, 60, 17)


def test_model_predict_single():
    """Test single prediction"""
    model = LSTMStockModel(ticker='GAZP', sequence_length=60, num_features=17)
    model.build_model()
    
    # Create random input
    sequence = np.random.rand(60, 17)
    
    # Should not raise error
    prediction = model.predict_single(sequence)
    assert isinstance(prediction, float)


# Integration Tests
@pytest.mark.asyncio
async def test_end_to_end_training(test_db: AsyncSession, sample_stock_data):
    """Test complete training pipeline (with small data)"""
    preprocessor = DataPreprocessor('GAZP')
    df = await preprocessor.load_data(test_db)
    df = preprocessor.create_technical_indicators(df)
    
    X, y = preprocessor.prepare_sequences(df, sequence_length=10, target_days=1)
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split_data(X, y)
    
    # Build and train model (just 1 epoch for testing)
    model = LSTMStockModel(ticker='GAZP', sequence_length=10, num_features=X.shape[2])
    model.build_model()
    
    # Quick training
    history = model.train(
        X_train, y_train,
        X_val, y_val,
        epochs=1,
        batch_size=8
    )
    
    assert history is not None
    
    # Test prediction
    predictions = model.predict(X_test)
    assert len(predictions) == len(X_test)


# Mock data for testing without actual MOEX API calls
@pytest.fixture
def mock_moex_response():
    """Mock MOEX API response"""
    return {
        'history': {
            'columns': ['TRADEDATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME'],
            'data': [
                ['2024-01-01', 173.0, 173.5, 174.0, 172.5, 1000000],
                ['2024-01-02', 173.5, 174.0, 174.5, 173.0, 1100000],
            ]
        }
    }


def test_moex_collector_init():
    """Test MOEX collector initialization"""
    collector = MOEXCollector()
    assert collector is not None
    assert len(collector.TICKERS) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
