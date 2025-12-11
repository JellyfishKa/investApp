
# Implementation Plan: Backend & AI/ML integration

This plan outlines the steps to implement a Python-based backend (FastAPI) that hosts the Machine Learning models for `Invest MRSU`.

> [!NOTE]
> **Storage Strategy**: **Option B (PostgreSQL)** selected.
> We will use PostgreSQL for structured data (stocks, fundamentals) and filesystem/S3 for large model files.

## Architecture Overview

1.  **Data Layer**:
    *   **PostgreSQL**: Primary store for Stock Prices, Fundamental Data, and Prediction History,
    *   **MOEX Parser**: Automated script to fetch historical and daily data.
    *   **CSV Ingestion**: Mechanism to load fundamental/macro data from manually uploaded CSV files.
2.  **ML Core**:
    *   **Preprocessing**: Cleaning, feature engineering (MA, RSI, MACD).
    *   **Models**: LSTM (`.keras`) models per ticker.
    *   **Training Pipeline**: Script to retrain models on new data.
3.  **API Layer (FastAPI)**:
    *   REST Endpoints for predictions and data management.
    *   Background tasks for data updates.

---

## Proposed Changes

### Phase 1: Data Infrastructure
*Est. Time: 2-3 Days*

Setting up the database and data collection services.

#### [NEW] `backend/docker-compose.yml`
*   Services: `db` (Postgres 16), `app` (FastAPI).

#### [NEW] `backend/database/`
*   `db.py`: Async connection using `SQLAlchemy` + `asyncpg`.
*   `models.py`: SQLModel/SQLAlchemy definitions for:
    *   `StockData` (date, ticker, open, close, etc.)
    *   `FundamentalData` (date, ticker, revenue, etc.)
    *   `Prediction` (date, ticker, predicted_price, model_version)

#### [MODIFY] [data_collector.py](file:///c:/Users/Sergej/Documents/GitHub/investApp/invest_mrsu/data_collector.py) -> `backend/services/moex.py`
*   Refactor to write to DB instead of CSV.
*   Implement incremental updates (fetch only missing dates).

#### [NEW] `backend/services/importer.py`
*   Logic to parse upload CSVs and upsert into DB.

### Phase 2: ML Model Implementation
*Est. Time: 3-4 Days*

Based on `ML_MODEL_PROMPT.md` but swapped for LSTM.

#### [NEW] `backend/ml/preprocessor.py`
*   `DataPreprocessor` class:
    *   Reads from DB -> Pandas DataFrame.
    *   Normalization, Technical Indicators.

#### [NEW] `backend/ml/model.py`
*   `LSTMModel` implementation (using TensorFlow/Keras).
*   methods: `train(df)`, `predict(days)`, `save(path)`, `load(path)`.

### Phase 3: Backend API (FastAPI)
*Est. Time: 2-3 Days*

#### [NEW] `backend/main.py`
*   FastAPI application entry point.
*   **Endpoints**:
    *   `POST /predict`
    *   `GET /history/{ticker}` (Reads from DB)
    *   `POST /admin/upload_csv` (Saves to DB)

#### [NEW] `backend/requirements.txt`
*   Dependencies: `fastapi`, `uvicorn[standard]`, `pandas`, `tensorflow`, `moexalgo`, `python-multipart`, `loguru`, `asyncpg`, `sqlalchemy`, `sqlmodel`, `alembic`.

### Phase 4: Integration
*Est. Time: 2 Days*

#### [MODIFY] `lib/services/ml_service.dart`
*   Implement HTTP calls to the new API endpoints.

## Verification Plan

### Automated Tests
*   **Backend**: `pytest` for API endpoints and Model logic.
    *   Spin up test DB (Docker container or sqlite memory).
    *   Test End-to-End data flow: `Upload CSV` -> `DB` -> `Train` -> `Predict`.
