# Быстрый запуск тестов

## Тест 1: ML компоненты (без БД)
```bash
cd test
python test_ml.py
```

## Тест 2: API endpoints (нужен backend)
```bash
# Терминал 1 - запуск backend:
cd backend
python main.py

# Терминал 2 - запуск тестов:
cd test
python test_api.py
```
