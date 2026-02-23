# Развёртывание

## Требования

- Python 3.11+
- Flutter SDK 3.x (Dart ^3.9.2)
- Docker и Docker Compose (для PostgreSQL)
- Git

## Flutter-приложение

### Разработка

```bash
cd invest_mrsu
flutter pub get
flutter run
```

Работает на мок-данных, backend не нужен.

### Сборка APK (Android)

```bash
cd invest_mrsu
flutter build apk --release
```

Готовый APK: `build/app/outputs/flutter-apk/app-release.apk`.

### Сборка для Windows

```bash
cd invest_mrsu
flutter build windows --release
```

## Backend

### Вариант 1: Тестовый режим (без БД)

Самый простой способ запустить API для разработки:

```bash
cd invest_mrsu/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main_simple.py
```

API на `http://localhost:8000`, Swagger на `http://localhost:8000/docs`.

### Вариант 2: С PostgreSQL через Docker

```bash
cd invest_mrsu/backend

# 1. Настроить окружение
cp .env.example .env

# 2. Запустить БД
docker-compose up -d db

# 3. Установить зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Запустить приложение
python main.py
```

### Вариант 3: Полностью в Docker

```bash
cd invest_mrsu/backend
docker-compose up -d
```

Запустит PostgreSQL и backend в контейнерах. API на порту 8000.

## Первоначальная загрузка данных

После запуска backend с PostgreSQL нужно загрузить котировки:

```bash
# Автоматический сбор с Московской биржи (последние 2 года)
curl -X POST http://localhost:8000/admin/update_moex
```

Для загрузки фундаментальных данных из CSV:
```bash
curl -X POST -F "file=@fundamentals.csv" -F "ticker=GAZP" -F "data_type=fundamental" \
  http://localhost:8000/admin/upload_csv
```

## Обучение моделей

После загрузки данных (минимум 100 дней):

```bash
cd invest_mrsu/backend
python ml/trainer.py
```

Обучение занимает 10-30 минут. Модели сохраняются в `models/`.

## Тестирование

### Backend (unit-тесты)

```bash
cd invest_mrsu/backend
pytest test_backend.py -v
```

### ML-компоненты (без БД)

```bash
cd invest_mrsu/test
python test_ml.py
```

### API (нужен запущенный backend)

```bash
cd invest_mrsu/test
python test_api.py
```

## Структура Docker

```yaml
# docker-compose.yml
services:
  db:        # PostgreSQL 16 (порт 5432)
  app:       # FastAPI backend (порт 8000)
```

Тома:
- `postgres_data` — данные PostgreSQL
- `./models` — обученные модели (монтируется в контейнер)
- `./logs` — логи обучения

## Переменные окружения

См. файл `.env.example`. Основные:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/invest_mrsu
ENVIRONMENT=development
API_PORT=8000
SEQUENCE_LENGTH=60
TARGET_DAYS=30
EPOCHS=100
```
