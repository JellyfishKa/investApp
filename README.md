# НейроПульс (рабочий репозиторий)

Мобильный тренажёр инвестиционных решений для новичков: короткое обучение, практические сценарии и ML-подсказки без обещаний доходности.

## Текущий статус

- Flutter-клиент уже работает как demo/MVP.
- Backend на FastAPI и ML-контур (LSTM) готовы к интеграции.
- Основной фокус: сквозной пользовательский поток, retention и ранняя монетизация.

## Быстрый запуск

### Клиент (Flutter)

```bash
cd invest_mrsu
flutter pub get
flutter run
```

### Backend (локально, тестовый режим)

```bash
cd invest_mrsu/backend
pip install -r requirements.txt
python main_simple.py
```

### Backend (полный режим, PostgreSQL)

```bash
cd invest_mrsu/backend
cp .env.example .env
docker-compose up -d db
pip install -r requirements.txt
python main.py
```

## Карта документации

Актуальный индекс документации находится в `docs/README.md`.

Ключевые документы:
- `docs/market-analysis-2026-neuropulse.md` — глубокий рынок 2026 + unit-экономика.
- `docs/brand-folder-neuropulse.md` — бренд-папка (позиционирование, голос, визуал).
- `docs/design-system-style-code.md` — дизайн-система и дизайн-код.
- `docs/improvements.md` — технические приоритеты и дорожка реализации.

## Лицензия

Apache License 2.0 — `LICENSE`.
