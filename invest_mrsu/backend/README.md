# Invest MRSU Backend

Backend API для приложения Invest MRSU с поддержкой машинного обучения (LSTM).

## 🚀 Быстрый старт

### Требования
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 16 (через Docker)

### Установка

1. **Клонировать репозиторий**:
```bash
cd invest_mrsu/backend
```

2. **Создать виртуальное окружение**:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Установить зависимости**:
```bash
pip install -r requirements.txt
```

4. **Настроить переменные окружения**:
```bash
cp .env.example .env
# Отредактируйте .env при необходимости
```

5. **Запустить базу данных**:
```bash
docker-compose up -d db
```

6. **Запустить приложение**:
```bash
python main.py
```

API будет доступен по адресу: `http://localhost:8000`

## 📊 Сбор данных

### Автоматический сбор с MOEX:
```bash
curl -X POST http://localhost:8000/admin/update_moex
```

### Загрузка CSV файлов:
```bash
# Фундаментальные данные
curl -X POST -F "file=@fundamentals.csv" -F "ticker=GAZP" -F "data_type=fundamental" \
  http://localhost:8000/admin/upload_csv

# Макроэкономические данные
curl -X POST -F "file=@macro.csv" -F "data_type=macro" \
  http://localhost:8000/admin/upload_csv
```

## 🤖 Обучение моделей

```bash
python ml/trainer.py
```

Модели будут сохранены в папке `models/`.

## 🧪 Тестирование

```bash
# Запустить все тесты
pytest test_backend.py -v

# Запустить с покрытием
pytest test_backend.py --cov=. --cov-report=html
```

## 📡 API Endpoints

### Основные

- `GET /` - Health check
- `POST /predict` - Получить прогноз цены
- `GET /history/{ticker}` - Получить исторические данные

### Администрирование

- `POST /admin/upload_csv` - Загрузить CSV
- `POST /admin/update_moex` - Обновить данные с MOEX

### Примеры запросов

**Прогноз на месяц:**
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GAZP","period":"month"}'
```

**История за год:**
```bash
curl http://localhost:8000/history/GAZP?days=365
```

## 🏗 Структура проекта

```
backend/
├── database/
│   ├── db.py           # Подключение к БД
│   └── models.py       # SQLAlchemy модели
├── ml/
│   ├── preprocessor.py # Препроцессинг данных
│   ├── model.py        # LSTM модель
│   └── trainer.py      # Обучение моделей
├── services/
│   ├── moex.py         # MOEX API клиент
│   └── importer.py     # CSV импорт
├── main.py             # FastAPI приложение
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## 🔧 Конфигурация

Все настройки в `.env` файле:
- `DATABASE_URL` - URL базы данных
- `SEQUENCE_LENGTH` - Длина последовательности для LSTM (по умолчанию: 60)
- `TARGET_DAYS` - Дней для прогноза (по умолчанию: 30)
- `EPOCHS` - Эпохи обучения (по умолчанию: 100)

## 📈 Модель

**Архитектура LSTM:**
- Input: (60 дней, 17 признаков)
- LSTM(128) + Dropout(0.2)
- LSTM(64) + Dropout(0.2)
- Dense(32) + Dropout(0.1)
- Output: 1 (цена)

**Признаки:**
- OHLCV (Open, High, Low, Close, Volume)
- Moving Averages (MA7, MA30, MA90)
- RSI, MACD, Bollinger Bands
- Momentum, Volume change

## 🐳 Docker

**Запустить весь стек:**
```bash
docker-compose up -d
```

**Пересобрать после изменений:**
```bash
docker-compose up -d --build
```

## 📝 Логи

Логи сохраняются в `logs/`:
- `training_{date}.log` - Логи обучения
- Остальные логи в stderr/stdout

## ⚠️ Важно

1. Убедитесь, что база данных запущена перед стартом приложения
2. Для обучения нужно минимум 100 дней данных
3. Первый запуск обучения может занять 10-30 минут
4. Модели весят ~10-50 МБ каждая

## 🔗 Интеграция с Flutter

См. `implementation_plan.md` раздел "Phase 4: Integration"
