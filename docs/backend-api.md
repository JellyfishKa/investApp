# Backend API

REST API на FastAPI для работы с котировками и ML-прогнозами.

## Запуск

### Тестовый режим (без PostgreSQL)

```bash
cd invest_mrsu/backend
pip install -r requirements.txt
python main_simple.py
```

Работает на мок-данных, не требует базы данных. Подходит для разработки Flutter-клиента.

### Полный режим

```bash
cd invest_mrsu/backend
cp .env.example .env
docker-compose up -d db
python main.py
```

Требует PostgreSQL (через Docker).

## Эндпоинты

### GET / — Health Check

Проверка работоспособности сервера.

**Ответ:**
```json
{
  "status": "ok",
  "service": "Invest MRSU ML API",
  "version": "1.0.0",
  "timestamp": "2025-02-20T12:00:00"
}
```

### POST /predict — Прогноз цены

Возвращает прогноз цены акции на указанный период.

**Тело запроса:**
```json
{
  "ticker": "GAZP",
  "period": "month"
}
```

Допустимые значения `period`: `week`, `month`, `year`.

**Ответ (200):**
```json
{
  "ticker": "GAZP",
  "current_price": 173.50,
  "predicted_price": 187.38,
  "confidence_low": 168.64,
  "confidence_high": 206.12,
  "change_percent": 8.0,
  "prediction_date": "2025-03-20T12:00:00",
  "model_accuracy": 85.5
}
```

**Ошибки:**
- `400` — неверный период
- `404` — модель для тикера не найдена (нужно обучить)
- `500` — внутренняя ошибка

### GET /history/{ticker} — Исторические данные

Возвращает дневные котировки OHLCV.

**Параметры:**
- `ticker` (path) — тикер акции, например `GAZP`
- `days` (query, по умолчанию 365) — количество дней

**Пример:** `GET /history/GAZP?days=30`

**Ответ (200):**
```json
{
  "ticker": "GAZP",
  "data": [
    {
      "date": "2025-01-20T00:00:00",
      "open": 172.0,
      "close": 173.5,
      "high": 174.0,
      "low": 171.5,
      "volume": 1050000
    }
  ]
}
```

### POST /admin/upload_csv — Загрузка CSV

Загрузка файла с фундаментальными или макроэкономическими данными.

**Параметры (form-data):**
- `file` — CSV-файл
- `ticker` (опционально) — тикер (обязателен для фундаментальных данных)
- `data_type` — `fundamental` или `macro`

**Формат CSV для фундаментальных данных:**
```csv
Date,Revenue_bn,EBITDA_bn,Net_profit_bn,Debt_bn,Dividend
2022-Q1,100.5,50.2,30.1,200.0,10.5
```

**Формат CSV для макроданных:**
```csv
Date,Oil_Brent_USD,USD_RUB,EUR_RUB,MOEX_Index,CB_Rate
2024-01-01,75.5,75.2,85.1,3000.5,16.0
```

**Ответ (200):**
```json
{
  "message": "Successfully imported 2 records",
  "records_imported": 2
}
```

### POST /admin/update_moex — Обновление данных с биржи

Запускает сбор котировок по всем тикерам с MOEX ISS API за последние 2 года.

**Ответ (200):**
```json
{
  "message": "MOEX data updated successfully",
  "tickers": ["GAZP", "GAZP-p", "SIBN", "GCHE", "MRKZ"],
  "timestamp": "2025-02-20T12:00:00"
}
```

## Переменные окружения

Настраиваются в файле `.env` (шаблон — `.env.example`):

| Переменная | Описание | По умолчанию |
|---|---|---|
| DATABASE_URL | Строка подключения к PostgreSQL | postgresql+asyncpg://postgres:postgres@localhost:5432/invest_mrsu |
| ENVIRONMENT | Окружение (development/production) | development |
| API_HOST | Хост для запуска | 0.0.0.0 |
| API_PORT | Порт | 8000 |
| SEQUENCE_LENGTH | Длина входной последовательности LSTM | 60 |
| TARGET_DAYS | Горизонт прогноза (дни) | 30 |
| EPOCHS | Количество эпох обучения | 100 |
| BATCH_SIZE | Размер батча | 32 |
| LOG_LEVEL | Уровень логирования | INFO |

## Зависимости

Основные пакеты (полный список — в `requirements.txt`):

- **FastAPI** — веб-фреймворк
- **SQLAlchemy** (async) — ORM для PostgreSQL
- **TensorFlow** — LSTM-модель
- **pandas, numpy, scikit-learn** — обработка данных
- **moexalgo, aiohttp** — получение данных с биржи
- **diskcache** — кэширование прогнозов
- **loguru** — логирование
- **pytest, httpx** — тестирование

## Кэширование

Прогнозы кэшируются на диск (папка `cache/`) с TTL 24 часа. При повторном запросе того же тикера и периода в течение суток модель не запускается — возвращается кэшированный результат.

Кэш сбрасывается при обновлении данных с MOEX.
