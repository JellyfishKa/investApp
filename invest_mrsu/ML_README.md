# 🤖 Machine Learning для Invest MRSU

## Полное руководство по созданию и интеграции ML модели

---

## 📚 Оглавление

1. [Обзор](#обзор)
2. [Быстрый старт](#быстрый-старт)
3. [Документация](#документация)
4. [Роли и ответственность](#роли-и-ответственность)
5. [Временная шкала](#временная-шкала)
6. [FAQ](#faq)

---

## 🎯 Обзор

Этот раздел содержит всю необходимую информацию для создания ML модели прогнозирования цен акций и её интеграции в Flutter приложение Invest MRSU.

### Что включено:

- ✅ Подробный промпт для разработки ML модели
- ✅ Руководство по сбору данных для экономистов
- ✅ Python скрипт для автоматического сбора данных
- ✅ Чек-лист интеграции с Flutter приложением
- ✅ Примеры кода для всех компонентов

---

## 🚀 Быстрый старт

### Для экономистов (сбор данных):

```bash
# 1. Прочитать руководство
открыть DATASET_COLLECTION_GUIDE.md

# 2. Запустить автоматический сбор данных (опционально)
pip install pandas requests
python data_collector.py

# 3. Проверить результат
ls dataset/stocks/  # Должны быть GAZP.csv, SIBN.csv, и т.д.

# 4. Заполнить фундаментальные данные вручную
открыть dataset/fundamentals/GAZP_fundamentals_TEMPLATE.csv
```

**Время:** 3-4 часа
**Результат:** Папка `dataset/` с CSV файлами

---

### Для ML разработчиков (создание модели):

```bash
# 1. Прочитать промпт
открыть ML_MODEL_PROMPT.md

# 2. Настроить окружение
python -m venv ml_env
source ml_env/bin/activate  # Windows: ml_env\Scripts\activate
pip install -r ml_requirements.txt

# 3. Обучить модель (используя промпт как руководство)
python train_model.py

# 4. Создать API
python main.py
# API доступен на http://localhost:8000

# 5. Протестировать
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GAZP","period":"month"}'
```

**Время:** 2-3 дня
**Результат:** Работающий ML API

---

### Для Flutter разработчиков (интеграция):

```bash
# 1. Прочитать чек-лист
открыть ML_INTEGRATION_CHECKLIST.md

# 2. Создать ML API сервис
создать lib/services/ml_api_service.dart

# 3. Обновить providers
изменить lib/providers/stocks_provider.dart

# 4. Протестировать
flutter test test/integration/ml_api_test.dart
```

**Время:** 1-2 дня
**Результат:** Интегрированная ML модель в приложении

---

## 📖 Документация

### Основные документы:

| Документ | Для кого | Описание |
|----------|----------|----------|
| [ML_MODEL_PROMPT.md](ML_MODEL_PROMPT.md) | ML разработчик | Полный промпт для создания модели |
| [DATASET_COLLECTION_GUIDE.md](DATASET_COLLECTION_GUIDE.md) | Экономист | Руководство по сбору данных |
| [ML_INTEGRATION_CHECKLIST.md](ML_INTEGRATION_CHECKLIST.md) | Вся команда | Чек-лист интеграции |
| [data_collector.py](data_collector.py) | Экономист/Разработчик | Скрипт для автоматизации |
| [ml_requirements.txt](ml_requirements.txt) | ML разработчик | Python зависимости |

### Вспомогательные документы:

- [MVP_STATUS.md](MVP_STATUS.md) - Текущий статус проекта
- [README.md](README.md) - Главный README приложения
- [QUICK_START.md](QUICK_START.md) - Руководство пользователя

---

## 👥 Роли и ответственность

### 1. Экономист / Аналитик данных

**Задачи:**
- Собрать исторические данные по акциям (2+ года)
- Собрать фундаментальные показатели компаний
- Собрать макроэкономические данные
- Валидировать качество данных

**Документы:**
- [DATASET_COLLECTION_GUIDE.md](DATASET_COLLECTION_GUIDE.md)

**Инструменты:**
- Excel / Google Sheets
- Python скрипт [data_collector.py](data_collector.py)
- MOEX API
- Investing.com

**Срок:** 2-3 дня (параллельно с разработкой)

---

### 2. ML разработчик / Data Scientist

**Задачи:**
- Подготовить данные (preprocessing)
- Создать и обучить модель Prophet/LSTM
- Оценить метрики модели (MAPE, RMSE)
- Создать FastAPI приложение
- Задеплоить на Render.com

**Документы:**
- [ML_MODEL_PROMPT.md](ML_MODEL_PROMPT.md)
- [ML_INTEGRATION_CHECKLIST.md](ML_INTEGRATION_CHECKLIST.md)

**Инструменты:**
- Python (pandas, prophet, scikit-learn)
- FastAPI
- Render.com / Railway.app
- Jupyter Notebook (для экспериментов)

**Срок:** 4-6 дней

---

### 3. Backend разработчик (опционально)

**Задачи:**
- Помочь с деплоем FastAPI
- Настроить кеширование (Redis)
- Настроить CI/CD
- Настроить мониторинг

**Инструменты:**
- Docker
- GitHub Actions
- Render.com
- Sentry (мониторинг ошибок)

**Срок:** 1-2 дня

---

### 4. Flutter разработчик

**Задачи:**
- Создать ML API сервис в Flutter
- Интегрировать с существующими providers
- Добавить обработку ошибок и loading states
- Добавить кеширование на клиенте
- Протестировать интеграцию

**Документы:**
- [ML_INTEGRATION_CHECKLIST.md](ML_INTEGRATION_CHECKLIST.md)

**Инструменты:**
- Flutter / Dart
- Provider (state management)
- http / dio (HTTP клиент)
- shared_preferences (кеш)

**Срок:** 2-3 дня

---

## 📅 Временная шкала (18 дней)

### Дни 1-2: Подготовка (ЗАВЕРШЕНО ✅)
- [x] Создание MVP UI
- [x] Mock данные
- [x] Подготовка документации ML

### Дни 2-3: Сбор данных
- [ ] Экономист: собрать исторические данные
- [ ] Экономист: собрать фундаментальные данные
- [ ] Экономист: собрать макроданные
- [ ] **Параллельно:** ML разработчик настраивает окружение

### Дни 4-6: Разработка ML модели
- [ ] ML: Preprocessing данных
- [ ] ML: Обучение Prophet моделей (5 тикеров)
- [ ] ML: Оценка метрик
- [ ] ML: Создание FastAPI приложения
- [ ] **Результат:** Работающий ML API локально

### День 7: Деплой Backend
- [ ] ML/Backend: Деплой на Render.com
- [ ] ML/Backend: Тестирование API в продакшене
- [ ] **Результат:** Публичный API URL

### Дни 8-9: Интеграция с Flutter
- [ ] Flutter: Создать ML API сервис
- [ ] Flutter: Обновить providers
- [ ] Flutter: Добавить обработку ошибок
- [ ] **Результат:** Приложение использует реальные прогнозы

### День 10: Тестирование
- [ ] Вся команда: Integration testing
- [ ] ML: Проверка метрик в production
- [ ] Flutter: UI тестирование
- [ ] **Результат:** Все работает стабильно

### Дни 11-14: Доработка и оптимизация
- [ ] Добавить кеширование
- [ ] Улучшить UI/UX
- [ ] Оптимизировать производительность
- [ ] Добавить дополнительные фичи

### Дни 15-17: Финальное тестирование
- [ ] Тестирование на Android
- [ ] Тестирование на Windows
- [ ] Багфиксы
- [ ] Подготовка к релизу

### День 18: Релиз и презентация
- [ ] Финальная полировка
- [ ] Создание презентации
- [ ] Демонстрация экспертной комиссии

---

## ❓ FAQ

### Q: Нужны ли платные сервисы?
**A:** Нет! Все сервисы бесплатные:
- Render.com: 750 часов/месяц бесплатно
- MOEX API: полностью бесплатный
- GitHub: бесплатно для публичных репозиториев

### Q: Какая точность модели ожидается?
**A:** Целевая MAPE < 10%. Для финансовых данных это хороший результат.

### Q: Что делать, если модель показывает плохие результаты?
**A:**
1. Проверить качество данных
2. Добавить больше исторических данных
3. Добавить дополнительные фичи (макропоказатели)
4. Попробовать другую модель (LSTM вместо Prophet)
5. В крайнем случае - использовать fallback на mock данные

### Q: Как часто переобучать модель?
**A:** Рекомендуется раз в неделю. Настроить автоматическое переобучение через GitHub Actions или Render Cron.

### Q: Сколько данных нужно минимум?
**A:** Минимум 2 года ежедневных данных. Чем больше - тем лучше.

### Q: Можно ли использовать другие ML фреймворки?
**A:** Да! Промпт предлагает Prophet как самый простой, но можно использовать:
- LSTM (TensorFlow/PyTorch) - более точный
- ARIMA - классический подход
- XGBoost - для табличных данных
- Ансамбль моделей - комбинация нескольких

### Q: Нужен ли опыт в ML?
**A:** Базовый опыт желателен. Промпт содержит все необходимые инструкции, но понимание основ ML поможет.

### Q: Как тестировать модель локально?
**A:**
```bash
# Запустить API
python main.py

# В другом терминале
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GAZP","period":"month"}'
```

### Q: Что делать если API недоступен в приложении?
**A:** Приложение автоматически переключится на mock данные (fallback). Нужно проверить логи Render.com.

### Q: Как добавить новую акцию?
**A:**
1. Собрать данные по новому тикеру
2. Обучить модель
3. Добавить тикер в список `TICKERS` в коде
4. Передеплоить API

---

## 🎓 Обучающие материалы

### Для начинающих в ML:
- [Time Series Forecasting with Prophet](https://facebook.github.io/prophet/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Python for Data Analysis (книга)](https://wesmckinney.com/book/)

### Для продвинутых:
- [Deep Learning for Time Series](https://arxiv.org/abs/2004.13408)
- [Forecasting: Principles and Practice (книга)](https://otexts.com/fpp3/)
- [Microsoft Forecasting Best Practices](https://github.com/microsoft/forecasting)

### Видео курсы:
- Coursera: Machine Learning Specialization
- YouTube: StatQuest (объяснения ML концепций)
- YouTube: Sentdex (Python для финансов)

---

## 🔗 Полезные ссылки

### API и данные:
- [MOEX API Documentation](https://www.moex.com/a2193)
- [Finam Export](https://www.finam.ru/profile/moex-akcii/gazprom/export/)
- [Investing.com](https://ru.investing.com/)
- [ЦБ РФ API](https://www.cbr.ru/development/sxml/)

### ML библиотеки:
- [Prophet Documentation](https://facebook.github.io/prophet/)
- [scikit-learn](https://scikit-learn.org/)
- [TensorFlow](https://www.tensorflow.org/)
- [PyTorch](https://pytorch.org/)

### Деплой:
- [Render.com](https://render.com/)
- [Railway.app](https://railway.app/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)

---

## 📞 Поддержка

### Нашли баг или есть вопрос?
1. Проверьте [FAQ](#faq)
2. Посмотрите в соответствующий документ
3. Создайте Issue в GitHub
4. Свяжитесь с командой

### Хотите улучшить документацию?
1. Fork репозиторий
2. Внесите изменения
3. Создайте Pull Request

---

## ✅ Чек-лист готовности

### Перед началом работы убедитесь:

**Для экономиста:**
- [ ] Прочитан [DATASET_COLLECTION_GUIDE.md](DATASET_COLLECTION_GUIDE.md)
- [ ] Есть доступ к источникам данных
- [ ] Установлен Python (опционально)

**Для ML разработчика:**
- [ ] Прочитан [ML_MODEL_PROMPT.md](ML_MODEL_PROMPT.md)
- [ ] Python 3.11+ установлен
- [ ] Есть аккаунт на Render.com
- [ ] Есть базовые знания ML

**Для Flutter разработчика:**
- [ ] Прочитан [ML_INTEGRATION_CHECKLIST.md](ML_INTEGRATION_CHECKLIST.md)
- [ ] Flutter SDK установлен
- [ ] Понимание Provider state management
- [ ] Опыт работы с HTTP API

---

## 🎉 Итоги

С помощью этой документации вы сможете:

✅ Собрать качественный датасет
✅ Создать и обучить ML модель
✅ Развернуть ML API в продакшене
✅ Интегрировать модель с Flutter приложением
✅ Получить работающее приложение с реальными прогнозами

**Удачи в разработке! 🚀**

---

**Версия:** 1.0
**Дата:** Ноябрь 2025
**Проект:** Invest MRSU
**Команда:** AI Assistant + Разработчики MRSU
