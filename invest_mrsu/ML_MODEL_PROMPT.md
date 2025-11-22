# Промпт для создания ML модели прогнозирования акций

## 🎯 Цель
Создать ML модель для прогнозирования цен акций российских компаний (холдинг Газпром) с возможностью предсказания на периоды: неделя, месяц, год.

---

## 📊 Требования к модели

### Входные данные
1. **Исторические данные акций:**
   - Дата (Date)
   - Цена открытия (Open)
   - Цена закрытия (Close)
   - Максимальная цена (High)
   - Минимальная цена (Low)
   - Объем торгов (Volume)
   - Тикер акции (Ticker)

2. **Фундаментальные показатели (опционально):**
   - Выручка компании
   - Прибыль (EBITDA)
   - Долг компании
   - P/E ratio (цена/прибыль)
   - Дивидендная доходность

3. **Макроэкономические показатели (опционально):**
   - Цена нефти (для Газпрома критично)
   - Курс доллара
   - Ключевая ставка ЦБ РФ
   - Индекс MOEX

### Выходные данные
1. **Прогноз цены закрытия** на указанную дату
2. **Доверительный интервал** (нижняя и верхняя граница)
3. **Вероятность роста/падения** (classification)
4. **Метрики точности** прогноза

---

## 🛠 Технический стек

### Рекомендуемые библиотеки Python:
```python
# Основные
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0

# Временные ряды
prophet>=1.1.5  # Facebook Prophet (рекомендуется для MVP)
statsmodels>=0.14.0  # ARIMA, SARIMA

# Deep Learning (опционально)
tensorflow>=2.15.0
keras>=3.0.0

# API
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.5.0

# Работа с данными
requests>=2.31.0
yfinance>=0.2.32  # для получения данных

# Визуализация (для тестирования)
matplotlib>=3.8.0
seaborn>=0.13.0
```

---

## 📝 Задание для разработки модели

### Этап 1: Подготовка данных

```python
# Задача: Создать класс DataPreprocessor
# Требования:
# 1. Загрузка данных из CSV
# 2. Проверка на пропуски и аномалии
# 3. Нормализация данных
# 4. Создание технических индикаторов:
#    - Moving Average (MA) - 7, 30, 90 дней
#    - Relative Strength Index (RSI)
#    - MACD (Moving Average Convergence Divergence)
#    - Bollinger Bands
# 5. Split на train/validation/test (70/15/15)

class DataPreprocessor:
    def __init__(self, data_path: str):
        """
        Инициализация препроцессора

        Args:
            data_path: путь к CSV файлу с данными
        """
        pass

    def load_data(self) -> pd.DataFrame:
        """Загрузить данные из CSV"""
        pass

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Проверить данные на корректность:
        - Нет пропусков в критичных колонках
        - Даты в правильном порядке
        - Цены положительные
        """
        pass

    def create_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Создать технические индикаторы"""
        pass

    def split_data(self, df: pd.DataFrame):
        """Разделить на train/val/test"""
        pass
```

---

### Этап 2: Разработка модели

#### Вариант A: Facebook Prophet (Рекомендуется для MVP)

```python
# Задача: Создать класс StockProphetModel
# Требования:
# 1. Обучение модели Prophet на исторических данных
# 2. Прогнозирование на 7, 30, 365 дней вперед
# 3. Расчет доверительного интервала
# 4. Сохранение/загрузка модели

from prophet import Prophet
import pickle

class StockProphetModel:
    def __init__(self, ticker: str):
        """
        Args:
            ticker: тикер акции (например, "GAZP")
        """
        self.ticker = ticker
        self.model = None

    def train(self, df: pd.DataFrame):
        """
        Обучить модель

        Args:
            df: DataFrame с колонками ['ds' (дата), 'y' (цена)]

        Returns:
            Метрики обучения (MAE, RMSE, MAPE)
        """
        # Создание и настройка модели
        self.model = Prophet(
            changepoint_prior_scale=0.05,  # гибкость тренда
            seasonality_prior_scale=10.0,   # сезонность
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )

        # Добавление регрессоров (если есть доп. данные)
        # self.model.add_regressor('oil_price')
        # self.model.add_regressor('usd_rub')

        # Обучение
        self.model.fit(df)

        # Валидация и расчет метрик
        return self._calculate_metrics()

    def predict(self, periods: int = 30) -> pd.DataFrame:
        """
        Сделать прогноз

        Args:
            periods: количество дней для прогноза

        Returns:
            DataFrame с колонками:
            - ds (дата)
            - yhat (прогноз)
            - yhat_lower (нижняя граница)
            - yhat_upper (верхняя граница)
        """
        future = self.model.make_future_dataframe(periods=periods)
        forecast = self.model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

    def save_model(self, path: str):
        """Сохранить модель"""
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

    def load_model(self, path: str):
        """Загрузить модель"""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

    def _calculate_metrics(self) -> dict:
        """Рассчитать метрики точности"""
        # MAE, RMSE, MAPE
        pass
```

---

#### Вариант B: LSTM (для более точных прогнозов)

```python
# Задача: Создать класс StockLSTMModel
# Требования:
# 1. Нейронная сеть LSTM для временных рядов
# 2. Использование последних N дней для прогноза
# 3. Multi-output для прогноза на разные периоды

import tensorflow as tf
from tensorflow import keras

class StockLSTMModel:
    def __init__(self, ticker: str, sequence_length: int = 60):
        """
        Args:
            ticker: тикер акции
            sequence_length: сколько предыдущих дней использовать
        """
        self.ticker = ticker
        self.sequence_length = sequence_length
        self.model = None
        self.scaler = None

    def build_model(self, input_shape):
        """
        Построить архитектуру LSTM

        Архитектура:
        - LSTM слой (128 units, return_sequences=True)
        - Dropout (0.2)
        - LSTM слой (64 units)
        - Dropout (0.2)
        - Dense (32 units, relu)
        - Dense (3 outputs) -> прогноз на 7, 30, 365 дней
        """
        model = keras.Sequential([
            keras.layers.LSTM(128, return_sequences=True,
                            input_shape=input_shape),
            keras.layers.Dropout(0.2),
            keras.layers.LSTM(64),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(3)  # 3 прогноза
        ])

        model.compile(
            optimizer='adam',
            loss='huber',  # устойчив к выбросам
            metrics=['mae', 'mse']
        )

        self.model = model
        return model

    def train(self, X_train, y_train, epochs=50, batch_size=32):
        """Обучить модель"""
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.1,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=5),
                keras.callbacks.ReduceLROnPlateau(patience=3)
            ]
        )
        return history

    def predict(self, last_sequence):
        """
        Сделать прогноз

        Args:
            last_sequence: последние N дней данных

        Returns:
            [прогноз_7дней, прогноз_30дней, прогноз_365дней]
        """
        prediction = self.model.predict(last_sequence)
        return prediction[0]  # [week, month, year]
```

---

### Этап 3: Оценка модели

```python
# Задача: Создать класс ModelEvaluator
# Требования:
# 1. Расчет метрик: MAE, RMSE, MAPE, R²
# 2. Backtesting на исторических данных
# 3. Визуализация результатов

class ModelEvaluator:
    @staticmethod
    def calculate_metrics(y_true, y_pred) -> dict:
        """
        Рассчитать метрики

        Returns:
            {
                'mae': Mean Absolute Error,
                'rmse': Root Mean Square Error,
                'mape': Mean Absolute Percentage Error,
                'r2': R² Score
            }
        """
        pass

    @staticmethod
    def backtest(model, test_data, periods=[7, 30, 365]):
        """
        Тестирование на исторических данных

        Логика:
        1. Взять данные до определенной даты
        2. Сделать прогноз
        3. Сравнить с реальными данными
        4. Повторить для разных дат
        """
        pass

    @staticmethod
    def plot_predictions(actual, predicted, ticker):
        """Визуализировать прогнозы vs реальность"""
        pass
```

---

### Этап 4: API Endpoints

```python
# Задача: Создать FastAPI приложение для ML модели
# Файл: ml_api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd

app = FastAPI(
    title="Invest MRSU ML API",
    description="API для прогнозирования цен акций",
    version="1.0.0"
)

# Модели данных
class PredictionRequest(BaseModel):
    ticker: str  # "GAZP", "SIBN", и т.д.
    period: str  # "week", "month", "year"

class PredictionResponse(BaseModel):
    ticker: str
    current_price: float
    predicted_price: float
    confidence_low: float
    confidence_high: float
    change_percent: float
    prediction_date: datetime
    model_accuracy: float  # MAPE

class HistoricalDataRequest(BaseModel):
    ticker: str
    start_date: datetime
    end_date: datetime

# Эндпоинты

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "service": "Invest MRSU ML API",
        "version": "1.0.0"
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_stock_price(request: PredictionRequest):
    """
    Прогнозирование цены акции

    Args:
        ticker: тикер акции (GAZP, SIBN, GCHE, GAZP-p, MRKZ)
        period: период прогноза (week, month, year)

    Returns:
        Прогноз с доверительным интервалом

    Пример запроса:
    ```json
    {
        "ticker": "GAZP",
        "period": "month"
    }
    ```

    Пример ответа:
    ```json
    {
        "ticker": "GAZP",
        "current_price": 173.50,
        "predicted_price": 187.38,
        "confidence_low": 180.12,
        "confidence_high": 194.64,
        "change_percent": 8.0,
        "prediction_date": "2025-12-20T00:00:00",
        "model_accuracy": 0.95
    }
    ```
    """
    try:
        # 1. Загрузить модель для тикера
        model = load_model(request.ticker)

        # 2. Получить текущую цену
        current_price = get_current_price(request.ticker)

        # 3. Сделать прогноз
        periods_map = {"week": 7, "month": 30, "year": 365}
        days = periods_map[request.period]

        forecast = model.predict(periods=days)

        # 4. Вернуть результат
        return PredictionResponse(
            ticker=request.ticker,
            current_price=current_price,
            predicted_price=forecast['yhat'].iloc[-1],
            confidence_low=forecast['yhat_lower'].iloc[-1],
            confidence_high=forecast['yhat_upper'].iloc[-1],
            change_percent=calculate_change_percent(
                current_price,
                forecast['yhat'].iloc[-1]
            ),
            prediction_date=forecast['ds'].iloc[-1],
            model_accuracy=model.get_accuracy()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/batch")
async def predict_multiple_stocks(tickers: List[str], period: str):
    """
    Прогноз для нескольких акций одновременно

    Пример:
    ```json
    {
        "tickers": ["GAZP", "SIBN", "GCHE"],
        "period": "month"
    }
    ```
    """
    results = []
    for ticker in tickers:
        try:
            prediction = await predict_stock_price(
                PredictionRequest(ticker=ticker, period=period)
            )
            results.append(prediction)
        except Exception as e:
            results.append({"ticker": ticker, "error": str(e)})

    return results

@app.get("/model/metrics/{ticker}")
async def get_model_metrics(ticker: str):
    """
    Получить метрики точности модели

    Returns:
        {
            "ticker": "GAZP",
            "mae": 2.34,
            "rmse": 3.12,
            "mape": 0.95,
            "r2": 0.87,
            "last_trained": "2025-11-20T00:00:00",
            "training_samples": 1500
        }
    """
    model = load_model(ticker)
    return model.get_metrics()

@app.post("/retrain/{ticker}")
async def retrain_model(ticker: str):
    """
    Переобучить модель на свежих данных

    Требует:
    - Admin токен для безопасности
    - Запускается как фоновая задача

    Returns:
        {
            "status": "started",
            "task_id": "uuid",
            "estimated_time": "5 minutes"
        }
    """
    # Запустить фоновую задачу переобучения
    pass

# Вспомогательные функции

def load_model(ticker: str):
    """Загрузить обученную модель"""
    # Из кеша или файла
    pass

def get_current_price(ticker: str) -> float:
    """Получить текущую цену с MOEX API"""
    pass

def calculate_change_percent(current: float, predicted: float) -> float:
    """Рассчитать процент изменения"""
    return ((predicted - current) / current) * 100

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📈 Метрики качества модели

### Целевые показатели для MVP:
- **MAPE** (Mean Absolute Percentage Error): < 10%
- **MAE** (Mean Absolute Error): < 5₽ для GAZP
- **R² Score**: > 0.75

### Как измерить успех:
1. **Backtesting**: Прогнозы на исторических данных
2. **Live testing**: Прогнозы vs реальность за последний месяц
3. **Сравнение с baseline**: Лучше ли модель, чем простое MA(30)?

---

## 🚀 Деплой модели

### Вариант 1: Render.com (Рекомендуется)
```yaml
# render.yaml
services:
  - type: web
    name: invest-mrsu-ml-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
```

### Вариант 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📝 Checklist для разработчика

- [ ] Собрать исторические данные (минимум 2 года)
- [ ] Создать DataPreprocessor класс
- [ ] Реализовать Prophet модель
- [ ] Обучить модель на каждый тикер (GAZP, SIBN, GCHE, GAZP-p, MRKZ)
- [ ] Оценить метрики (MAPE < 10%)
- [ ] Создать FastAPI приложение
- [ ] Реализовать все endpoints
- [ ] Добавить кеширование прогнозов
- [ ] Написать тесты (pytest)
- [ ] Задеплоить на Render.com
- [ ] Интегрировать с Flutter приложением

---

## 🧪 Примеры использования API

### Python
```python
import requests

# Получить прогноз
response = requests.post(
    "https://invest-mrsu-ml-api.onrender.com/predict",
    json={
        "ticker": "GAZP",
        "period": "month"
    }
)

prediction = response.json()
print(f"Прогноз на месяц: {prediction['predicted_price']}₽")
print(f"Изменение: {prediction['change_percent']}%")
```

### Dart (Flutter)
```dart
// lib/services/ml_api_service.dart
class MLApiService {
  static const baseUrl = 'https://invest-mrsu-ml-api.onrender.com';

  Future<PredictionSet> getPredictions(String ticker) async {
    // Параллельные запросы для всех периодов
    final results = await Future.wait([
      _fetchPrediction(ticker, 'week'),
      _fetchPrediction(ticker, 'month'),
      _fetchPrediction(ticker, 'year'),
    ]);

    return PredictionSet(
      ticker: ticker,
      weekPrediction: results[0],
      monthPrediction: results[1],
      yearPrediction: results[2],
    );
  }

  Future<Prediction> _fetchPrediction(String ticker, String period) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predict'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'ticker': ticker,
        'period': period,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return Prediction.fromJson(data);
    } else {
      throw Exception('Failed to get prediction');
    }
  }
}
```

---

## 📚 Дополнительные материалы

- [Facebook Prophet Documentation](https://facebook.github.io/prophet/)
- [MOEX API Documentation](https://www.moex.com/a2193)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Time Series Forecasting Best Practices](https://github.com/microsoft/forecasting)
