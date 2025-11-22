# ✅ Чек-лист интеграции ML модели с Flutter приложением

## 📋 Обзор

Этот документ содержит пошаговый план интеграции ML модели прогнозирования в приложение Invest MRSU.

---

## 🎯 Цели

1. Заменить mock данные на реальные прогнозы от ML модели
2. Интегрировать API endpoints в Flutter приложение
3. Обеспечить плавную работу с кешированием

---

## 📊 Этап 1: Подготовка данных

### Задачи для экономистов:

- [ ] **Собрать исторические данные** (см. [DATASET_COLLECTION_GUIDE.md](DATASET_COLLECTION_GUIDE.md))
  - [ ] GAZP (Газпром)
  - [ ] GAZP-p (Газпром привилегированные)
  - [ ] SIBN (Газпром нефть)
  - [ ] GCHE (Газпром-нефтехим Салават)
  - [ ] MRKZ (Россети Урал)

- [ ] **Собрать фундаментальные данные**
  - [ ] Квартальная отчетность Газпрома за 2 года
  - [ ] Дивиденды

- [ ] **Собрать макроэкономические показатели**
  - [ ] Цена нефти Brent
  - [ ] Курсы USD/RUB, EUR/RUB
  - [ ] Индекс MOEX

**Срок:** Дни 2-3 (параллельно с разработкой)

**Инструменты:**
```bash
# Автоматический сбор данных
python data_collector.py

# Результат: папка dataset/ с CSV файлами
```

---

## 🤖 Этап 2: Разработка ML модели

### Задачи для ML разработчика:

- [ ] **Настроить окружение**
  ```bash
  cd invest_mrsu
  python -m venv ml_env
  source ml_env/bin/activate  # Windows: ml_env\Scripts\activate
  pip install -r ml_requirements.txt
  ```

- [ ] **Подготовить данные**
  - [ ] Создать класс `DataPreprocessor`
  - [ ] Добавить технические индикаторы (MA, RSI, MACD)
  - [ ] Split на train/val/test (70/15/15)

- [ ] **Обучить модель Prophet**
  - [ ] Создать класс `StockProphetModel`
  - [ ] Обучить для каждого тикера (5 моделей)
  - [ ] Оценить метрики (MAPE < 10%)
  - [ ] Сохранить модели в `models/` папку

- [ ] **Создать FastAPI приложение**
  - [ ] Реализовать `/predict` endpoint
  - [ ] Реализовать `/predict/batch` endpoint
  - [ ] Реализовать `/model/metrics/{ticker}` endpoint
  - [ ] Добавить кеширование (Redis или DiskCache)

**Срок:** Дни 4-6

**Файлы для создания:**
```
ml_backend/
├── main.py              # FastAPI приложение
├── models.py            # ML модели
├── preprocessor.py      # Подготовка данных
├── evaluator.py         # Оценка модели
├── cache.py             # Кеширование
└── models/              # Сохраненные модели
    ├── GAZP.pkl
    ├── SIBN.pkl
    └── ...
```

---

## 🚀 Этап 3: Деплой Backend

### Вариант A: Render.com (Рекомендуется)

- [ ] **Регистрация**
  - [ ] Создать аккаунт на https://render.com
  - [ ] Подключить GitHub репозиторий

- [ ] **Настройка сервиса**
  - [ ] Создать новый Web Service
  - [ ] Выбрать ветку `main`
  - [ ] Build Command: `pip install -r ml_requirements.txt`
  - [ ] Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

- [ ] **Переменные окружения**
  ```
  PYTHON_VERSION=3.11
  ENVIRONMENT=production
  ```

- [ ] **Загрузить модели**
  - Использовать Render Disk или S3 для хранения `.pkl` файлов

**Результат:** URL типа `https://invest-mrsu-ml.onrender.com`

### Вариант B: Railway.app (Альтернатива)

- [ ] Аналогично Render, но проще интерфейс
- [ ] Бесплатный tier: 500 часов/месяц

**Срок:** День 7

---

## 📱 Этап 4: Интеграция с Flutter

### Задачи для Flutter разработчика:

- [ ] **Создать API сервис**
  ```dart
  // lib/services/ml_api_service.dart
  class MLApiService {
    static const baseUrl = 'https://invest-mrsu-ml.onrender.com';

    Future<PredictionSet> getPredictions(String ticker);
    Future<double> getCurrentPrice(String ticker);
  }
  ```

- [ ] **Обновить StocksProvider**
  ```dart
  // Заменить mock данные на реальные
  @override
  PredictionSet getPredictions(String ticker) {
    // Было: return MockData.getPredictions(...)
    // Стало: return await _mlApiService.getPredictions(ticker)
  }
  ```

- [ ] **Добавить обработку ошибок**
  - [ ] Loading states
  - [ ] Error handling
  - [ ] Retry logic

- [ ] **Добавить кеширование на клиенте**
  ```dart
  // Кешировать прогнозы на 1 день
  SharedPreferences prefs = await SharedPreferences.getInstance();
  prefs.setString('predictions_$ticker', jsonEncode(data));
  ```

**Срок:** Дни 8-9

**Файлы для изменения:**
- `lib/services/ml_api_service.dart` (создать)
- `lib/providers/stocks_provider.dart` (изменить)
- `lib/models/prediction.dart` (добавить fromJson)

---

## 🧪 Этап 5: Тестирование

### Unit тесты (Backend)

- [ ] **Тесты для модели**
  ```python
  # tests/test_model.py
  def test_model_prediction():
      model = StockProphetModel('GAZP')
      prediction = model.predict(periods=30)
      assert prediction is not None
      assert len(prediction) == 30
  ```

- [ ] **Тесты для API**
  ```python
  # tests/test_api.py
  def test_predict_endpoint():
      response = client.post('/predict', json={
          'ticker': 'GAZP',
          'period': 'month'
      })
      assert response.status_code == 200
  ```

### Integration тесты (Flutter)

- [ ] **Тест API сервиса**
  ```dart
  test('ML API returns valid predictions', () async {
    final service = MLApiService();
    final predictions = await service.getPredictions('GAZP');
    expect(predictions.monthPrediction, isNotNull);
  });
  ```

- [ ] **Тест UI**
  - [ ] Прогнозы отображаются корректно
  - [ ] Loading indicator работает
  - [ ] Error handling работает

**Срок:** День 10

---

## 📈 Этап 6: Мониторинг и оптимизация

### Мониторинг качества модели

- [ ] **Создать дашборд метрик**
  - [ ] Актуальность MAPE
  - [ ] Количество запросов
  - [ ] Время ответа API

- [ ] **Настроить алерты**
  - [ ] MAPE > 15% → переобучить модель
  - [ ] API недоступен > 5 минут

### Оптимизация производительности

- [ ] **Кеширование**
  - [ ] Redis для прогнозов (TTL = 24 часа)
  - [ ] Cache warming (предзагрузка популярных тикеров)

- [ ] **Батчинг запросов**
  ```dart
  // Запросить все прогнозы одним запросом
  final predictions = await mlApiService.getPredictionsBatch(
    ['GAZP', 'SIBN', 'GCHE']
  );
  ```

**Срок:** Дни 11-12

---

## 🔄 Этап 7: Автоматическое переобучение

### Настройка CRON задач

- [ ] **Ежедневное обновление данных**
  ```python
  # cron_jobs/update_data.py
  # Запускается каждый день в 02:00
  # 1. Скачать свежие данные с MOEX
  # 2. Добавить в датасет
  ```

- [ ] **Еженедельное переобучение**
  ```python
  # cron_jobs/retrain_models.py
  # Запускается каждое воскресенье в 03:00
  # 1. Переобучить все 5 моделей
  # 2. Оценить метрики
  # 3. Если метрики хуже - откатиться
  ```

**Инструменты:**
- GitHub Actions (бесплатно)
- Render Cron Jobs
- Railway Cron

**Срок:** Дни 13-14

---

## 📊 Метрики успеха

### Технические метрики

| Метрика | Целевое значение | Критическое значение |
|---------|------------------|----------------------|
| MAPE | < 10% | > 15% |
| API Response Time | < 500ms | > 2s |
| API Uptime | > 99% | < 95% |
| Cache Hit Rate | > 80% | < 50% |

### Бизнес метрики

- [ ] Пользователи смотрят прогнозы (> 70% пользователей)
- [ ] Прогнозы помогают принимать решения
- [ ] Точность модели приемлема для пользователей

---

## 🚨 Fallback план

### Если ML модель не работает:

1. **Временно использовать mock данные**
   ```dart
   try {
     return await mlApiService.getPredictions(ticker);
   } catch (e) {
     // Fallback на mock данные
     return MockData.getPredictions(ticker, currentPrice);
   }
   ```

2. **Уведомить пользователя**
   ```dart
   showSnackBar('Используются тестовые прогнозы');
   ```

3. **Логировать ошибки**
   ```dart
   Sentry.captureException(e);
   ```

---

## 📚 Полезные команды

### Backend (Python)

```bash
# Локальный запуск
cd ml_backend
uvicorn main:app --reload

# Тестирование
pytest tests/

# Проверка типов
mypy .

# Форматирование
black .
```

### Frontend (Flutter)

```bash
# Тестирование интеграции
flutter test test/integration/

# Build
flutter build apk --release
flutter build windows --release
```

### Docker (опционально)

```bash
# Build и запуск
docker build -t invest-mrsu-ml .
docker run -p 8000:8000 invest-mrsu-ml
```

---

## ✅ Финальный чек-лист

### Before Production:

- [ ] Все 5 моделей обучены и метрики приемлемы
- [ ] API задеплоен и доступен
- [ ] Flutter приложение интегрировано
- [ ] Все тесты проходят
- [ ] Кеширование настроено
- [ ] Мониторинг работает
- [ ] Fallback на mock данные реализован
- [ ] Документация обновлена
- [ ] Команда обучена работе с системой

### After Production:

- [ ] Мониторить метрики первую неделю
- [ ] Собрать feedback от пользователей
- [ ] Подстроить модель на основе feedback
- [ ] Настроить автоматическое переобучение

---

## 🎓 Обучение команды

### Для экономистов:
- [ ] Как собирать данные
- [ ] Как интерпретировать метрики модели
- [ ] Когда нужно переобучение

### Для разработчиков:
- [ ] Как работает ML модель
- [ ] Как деплоить изменения
- [ ] Как отлаживать проблемы

### Для тестировщиков:
- [ ] Как тестировать прогнозы
- [ ] Какие метрики важны
- [ ] Как создавать баг-репорты

---

## 📞 Контакты и поддержка

- **ML модель:** [добавить контакт]
- **Backend API:** [добавить контакт]
- **Flutter интеграция:** [добавить контакт]
- **Данные:** [добавить контакт экономиста]

---

## 🔗 Связанные документы

- [ML_MODEL_PROMPT.md](ML_MODEL_PROMPT.md) - Подробное описание модели
- [DATASET_COLLECTION_GUIDE.md](DATASET_COLLECTION_GUIDE.md) - Руководство по сбору данных
- [data_collector.py](data_collector.py) - Скрипт для автоматического сбора данных
- [MVP_STATUS.md](MVP_STATUS.md) - Текущий статус проекта

---

**Версия:** 1.0
**Дата:** Ноябрь 2025
**Проект:** Invest MRSU
