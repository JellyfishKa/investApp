# Invest MRSU

Мобильное приложение для обучения инвестированию, разработанное в рамках учебного проекта МГУ им. Н.П. Огарёва.

Приложение позволяет изучать рынок акций, отслеживать котировки компаний Газпром-группы и получать прогнозы цен на основе машинного обучения (LSTM-нейросеть).

## Что сейчас реализовано

### Flutter-клиент (мобильное приложение)
- Экран авторизации (логин/пароль, демо-режим)
- Главный экран с четырьмя вкладками:
  - **Дашборд** — сводка по портфелю, быстрый доступ к акциям
  - **Акции** — список тикеров с ценами и изменениями за день
  - **Портфель** — виртуальный портфель с историей сделок
  - **Задачи** — учебные задания для пользователя
- Детальная страница акции с графиком цен и кнопками покупки/продажи
- Диалог покупки/продажи с расчётом суммы
- График цен на виджете fl_chart

Приложение работает на мок-данных. Тикеры: GAZP, GAZP-p, SIBN, GCHE, MRKZ.

### Python Backend (FastAPI)
- REST API с пятью эндпоинтами:
  - `GET /` — проверка состояния сервера
  - `POST /predict` — прогноз цены акции (тикер + период)
  - `GET /history/{ticker}` — исторические данные OHLCV
  - `POST /admin/upload_csv` — загрузка CSV с фундаментальными/макро данными
  - `POST /admin/update_moex` — обновление котировок с Московской биржи
- Сбор данных с MOEX ISS API (автоматический)
- Импорт CSV-файлов (фундаментальные и макроэкономические показатели)
- Кэширование прогнозов (diskcache, TTL 24 часа)
- Тестовый режим без PostgreSQL (`main_simple.py` с мок-данными)

### ML-модель (LSTM)
- Архитектура: два слоя LSTM (128 и 64 юнита) + Dense(32) + выход
- 17 признаков: OHLCV, скользящие средние (MA7/30/90), RSI, MACD, полосы Боллинджера, моментум, изменение объёма
- Препроцессинг с нормализацией MinMaxScaler
- Обучение с EarlyStopping и ReduceLROnPlateau
- Оценка: MAE, RMSE, MAPE, R²

### Инфраструктура
- Docker Compose: PostgreSQL 16 + Python-приложение
- Dockerfile для backend
- Тесты: pytest-asyncio (backend), ручные скрипты (ML, API)

### Вспомогательные инструменты
- `analyze_excel.py` — анализ Excel-файлов с финансовой отчётностью
- `gr.py`, `gr2.py` — визуализации (распределение компетенций, бюджет, unit-экономика)
- Данные: PDF-отчёты Газпрома (2020–2025), сводки по Газпрому и Сургутнефтегазу

## Технологический стек

| Компонент | Технология |
|---|---|
| Мобильный клиент | Flutter 3.x, Dart, Provider |
| Backend API | Python 3.11+, FastAPI, Uvicorn |
| База данных | PostgreSQL 16 (async SQLAlchemy) |
| ML-модель | TensorFlow/Keras (LSTM) |
| Данные | MOEX ISS API, CSV, Excel |
| Контейнеризация | Docker, Docker Compose |
| Графики | fl_chart (Flutter), Matplotlib (Python) |

## Быстрый старт

### Flutter-приложение

```bash
cd invest_mrsu
flutter pub get
flutter run
```

Приложение запустится на мок-данных без необходимости backend.

### Backend (тестовый режим, без PostgreSQL)

```bash
cd invest_mrsu/backend
pip install -r requirements.txt
python main_simple.py
```

API будет доступен по адресу `http://localhost:8000`. Документация Swagger: `http://localhost:8000/docs`.

### Backend (полный режим, с PostgreSQL)

```bash
cd invest_mrsu/backend
cp .env.example .env
docker-compose up -d db
pip install -r requirements.txt
python main.py
```

Подробнее — в [документации по развёртыванию](docs/deployment.md).

## Структура репозитория

```
investApp/
├── invest_mrsu/                 # Flutter-приложение
│   ├── lib/
│   │   ├── models/              # Модели данных (Stock, Portfolio, Prediction и др.)
│   │   ├── providers/           # State management (Provider)
│   │   ├── screens/             # Экраны приложения
│   │   ├── services/            # Сервис связи с backend API
│   │   ├── data/                # Мок-данные
│   │   └── main.dart            # Точка входа
│   ├── backend/                 # Python Backend
│   │   ├── database/            # Подключение к БД и модели таблиц
│   │   ├── ml/                  # LSTM модель, препроцессор, тренировка
│   │   ├── services/            # MOEX API, CSV импорт, кэш
│   │   ├── main.py              # FastAPI приложение (полная версия)
│   │   ├── main_simple.py       # Тестовая версия без PostgreSQL
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   └── test/                    # Тесты
├── docs/                        # Документация проекта
│   ├── plans/                   # Теоретические планы развития
│   └── ...
├── analyze_excel.py             # Анализ Excel-файлов
├── gr.py, gr2.py                # Визуализации для презентаций
└── LICENSE                      # Apache 2.0
```

## Документация

- [Архитектура проекта](docs/architecture.md)
- [Backend API](docs/backend-api.md)
- [Flutter-клиент](docs/flutter-client.md)
- [ML-модель](docs/ml-model.md)
- [Схема базы данных](docs/database-schema.md)
- [Развёртывание](docs/deployment.md)
- [Возможные улучшения](docs/improvements.md)
- [Теоретические планы развития](docs/plans/)

## Лицензия

Apache License 2.0 — см. файл [LICENSE](LICENSE).
