# Схема базы данных

PostgreSQL 16, подключение через SQLAlchemy (async, asyncpg).

## Таблицы

### stock_data — дневные котировки

Основная таблица с историческими ценами акций.

| Колонка | Тип | Описание |
|---|---|---|
| id | Integer, PK | Автоинкремент |
| ticker | String(10), NOT NULL | Тикер (GAZP, SIBN и т.д.) |
| date | DateTime, NOT NULL | Дата торгового дня |
| open | Float, NOT NULL | Цена открытия |
| close | Float, NOT NULL | Цена закрытия |
| high | Float, NOT NULL | Максимальная цена |
| low | Float, NOT NULL | Минимальная цена |
| volume | Float, NOT NULL | Объём торгов |
| created_at | DateTime | Дата создания записи |

Индексы:
- `idx_ticker_date` (ticker, date) — уникальный, предотвращает дубликаты

### fundamental_data — квартальная отчётность

Финансовые показатели компаний по кварталам.

| Колонка | Тип | Описание |
|---|---|---|
| id | Integer, PK | Автоинкремент |
| ticker | String(10), NOT NULL | Тикер |
| date | DateTime, NOT NULL | Конец квартала |
| revenue_bn | Float | Выручка (млрд руб.) |
| ebitda_bn | Float | EBITDA (млрд руб.) |
| net_profit_bn | Float | Чистая прибыль (млрд руб.) |
| debt_bn | Float | Долг (млрд руб.) |
| dividend | Float | Дивиденд на акцию (руб.) |
| created_at | DateTime | Дата создания записи |

Индексы:
- `idx_fundamental_ticker_date` (ticker, date) — уникальный

### macro_data — макроэкономические показатели

Ежедневные макроэкономические индикаторы.

| Колонка | Тип | Описание |
|---|---|---|
| id | Integer, PK | Автоинкремент |
| date | DateTime, NOT NULL, UNIQUE | Дата |
| oil_brent_usd | Float | Цена нефти Brent (USD) |
| usd_rub | Float | Курс доллара к рублю |
| eur_rub | Float | Курс евро к рублю |
| moex_index | Float | Индекс Московской биржи |
| cb_rate | Float | Ключевая ставка ЦБ РФ (%) |
| created_at | DateTime | Дата создания записи |

### predictions — прогнозы модели

Сохранённые результаты прогнозирования.

| Колонка | Тип | Описание |
|---|---|---|
| id | Integer, PK | Автоинкремент |
| ticker | String(10), NOT NULL | Тикер |
| prediction_date | DateTime, NOT NULL | Когда сделан прогноз |
| target_date | DateTime, NOT NULL | На какую дату прогноз |
| predicted_price | Float, NOT NULL | Прогнозируемая цена |
| confidence_low | Float | Нижняя граница интервала |
| confidence_high | Float | Верхняя граница интервала |
| model_version | String(50) | Версия модели |
| created_at | DateTime | Дата создания записи |

Индексы:
- `idx_prediction_ticker_target` (ticker, target_date)

## ER-диаграмма (упрощённая)

```
stock_data             fundamental_data         macro_data
┌──────────────┐       ┌──────────────────┐     ┌──────────────┐
│ ticker  (FK?)│       │ ticker     (FK?) │     │ date (UNIQUE)│
│ date         │       │ date             │     │ oil_brent_usd│
│ open         │       │ revenue_bn       │     │ usd_rub      │
│ close        │       │ ebitda_bn        │     │ eur_rub      │
│ high         │       │ net_profit_bn    │     │ moex_index   │
│ low          │       │ debt_bn          │     │ cb_rate      │
│ volume       │       │ dividend         │     └──────────────┘
└──────────────┘       └──────────────────┘

predictions
┌──────────────────┐
│ ticker           │
│ prediction_date  │
│ target_date      │
│ predicted_price  │
│ confidence_low   │
│ confidence_high  │
│ model_version    │
└──────────────────┘
```

Таблицы не связаны внешними ключами — связь по полю `ticker` логическая. Это упрощает импорт и позволяет добавлять данные независимо.

## Подключение

Строка подключения задаётся в переменной окружения `DATABASE_URL`:

```
postgresql+asyncpg://postgres:postgres@localhost:5432/invest_mrsu
```

Таблицы создаются автоматически при запуске приложения (`Base.metadata.create_all`).
