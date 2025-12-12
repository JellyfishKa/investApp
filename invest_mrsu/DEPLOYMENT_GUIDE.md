# 🚀 Руководство по развертыванию локального ML сервера

Пошаговая инструкция для развертывания backend на десктопном компьютере для демонстрации приложения в реальном времени.

---

## 📋 Что понадобится

### Требования к компьютеру-серверу:
- **OS**: Windows 10/11 (64-bit)
- **RAM**: Минимум 8 GB (рекомендуется 16 GB для обучения моделей)
- **CPU**: Многоядерный процессор (Intel Core i5/i7 или AMD Ryzen)
- **Диск**: 20+ GB свободного места (для БД и моделей)
- **Сеть**: Wi-Fi или Ethernet для локальной сети

### Программное обеспечение:
- ✅ Python 3.11+ ([скачать](https://www.python.org/downloads/))
- ✅ Docker Desktop ([скачать](https://www.docker.com/products/docker-desktop/))
- ✅ Git ([скачать](https://git-scm.com/downloads))

---

## 🔧 Часть 1: Подготовка сервера

### 1.1. Установить Docker Desktop

```powershell
# После установки проверить:
docker --version
docker-compose --version
```

### 1.2. Клонировать репозиторий

```powershell
cd C:\
git clone https://github.com/your-repo/investApp.git
cd investApp\invest_mrsu\backend
```

### 1.3. Установить Python зависимости

```powershell
# Создать виртуальное окружение
python -m venv venv
.\venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt
```

---

## 🗄️ Часть 2: Настройка базы данных

### 2.1. Запустить PostgreSQL

```powershell
# В папке backend:
docker-compose up -d db
```

Проверить, что БД запущена:
```powershell
docker ps
# Должен показать: invest_mrsu_db
```

### 2.2. Загрузить данные с MOEX

**Вариант A: Автоматическая загрузка (после запуска backend)**

После запуска backend (см. Часть 4), выполнить:
```powershell
curl -X POST http://localhost:8000/admin/update_moex
```

**Вариант B: Ручная загрузка CSV**

Если нужны дополнительные данные:
```powershell
curl -X POST http://localhost:8000/admin/upload_csv `
  -F "file=@fundamentals.csv" `
  -F "ticker=GAZP" `
  -F "data_type=fundamental"
```

---

## 🤖 Часть 3: Обучение ML моделей

### 3.1. Обучить модели (занимает 10-30 минут)

```powershell
# Убедитесь, что БД запущена и данные загружены
python ml/trainer.py
```

Это создаст модели для всех тикеров:
- `models/GAZP_model.keras`
- `models/SIBN_model.keras`
- и т.д.

### 3.2. Проверить результаты

После обучения проверьте файл:
```
models/training_summary.json
```

Там будут метрики точности (MAPE, RMSE, R²) для каждой модели.

---

## 🌐 Часть 4: Запуск Backend API

### 4.1. Узнать IP-адрес компьютера

```powershell
ipconfig
```

Найдите **IPv4-адрес** вашей локальной сети (обычно начинается с 192.168.x.x или 10.x.x.x).

> **Пример**: `192.168.1.100`

### 4.2. Настроить .env файл

```powershell
# Скопировать шаблон
cp .env.example .env

# Отредактировать .env
notepad .env
```

В `.env` убедитесь:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/invest_mrsu
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production
```

### 4.3. Запустить backend

```powershell
python main.py
```

Должно появиться:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 4.4. Проверить доступность

**С того же компьютера:**
```powershell
curl http://localhost:8000/
```

**С другого устройства в сети:**
```powershell
curl http://192.168.1.100:8000/
# Замените на ваш IP
```

---

## 📱 Часть 5: Настройка Flutter приложения

### 5.1. Обновить API URL в Flutter

Откройте файл:
```
lib/services/ml_api_service.dart
```

Измените:
```dart
// Было:
static const String baseUrl = 'http://localhost:8000';

// Стало (замените на IP вашего сервера):
static const String baseUrl = 'http://192.168.1.100:8000';
```

### 5.2. Пересобрать приложение

```bash
flutter clean
flutter pub get
flutter run -d windows
# Или для Android/iOS:
flutter run -d <device-id>
```

---

## 🔄 Часть 6: Автоматическое обновление данных

### 6.1. Создать скрипт автообновления

Создайте файл `update_data.py` в папке `backend`:

```python
"""
Скрипт для автоматического обновления данных
Запускать через Task Scheduler
"""
import asyncio
import requests
from datetime import datetime

API_URL = "http://localhost:8000"

def update_moex_data():
    """Обновить данные с MOEX"""
    try:
        print(f"[{datetime.now()}] Обновление данных с MOEX...")
        response = requests.post(f"{API_URL}/admin/update_moex", timeout=300)
        
        if response.status_code == 200:
            print(f"✓ Данные обновлены: {response.json()}")
        else:
            print(f"✗ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"✗ Ошибка: {e}")

if __name__ == "__main__":
    update_moex_data()
```

### 6.2. Настроить Task Scheduler (Windows)

1. Открыть **Task Scheduler** (Планировщик заданий)
2. Создать **Basic Task**:
   - **Name**: "Update MOEX Data"
   - **Trigger**: Daily at 19:00 (после закрытия биржи)
   - **Action**: Start a program
     - **Program**: `C:\investApp\invest_mrsu\backend\venv\Scripts\python.exe`
     - **Arguments**: `update_data.py`
     - **Start in**: `C:\investApp\invest_mrsu\backend`

### 6.3. Ручное обновление

Можно обновлять данные вручную:
```powershell
# С сервера:
curl -X POST http://localhost:8000/admin/update_moex

# С другого устройства:
curl -X POST http://192.168.1.100:8000/admin/update_moex
```

---

## 🔒 Часть 7: Настройка брандмауэра Windows

### 7.1. Разрешить подключения к порту 8000

```powershell
# Открыть PowerShell от имени администратора:
New-NetFirewallRule -DisplayName "Invest MRSU Backend" `
  -Direction Inbound `
  -Protocol TCP `
  -LocalPort 8000 `
  -Action Allow
```

### 7.2. Проверка доступности

С другого устройства в сети:
```bash
# Проверить доступность:
curl http://<IP_СЕРВЕРА>:8000/

# Получить прогноз:
curl -X POST http://<IP_СЕРВЕРА>:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"ticker":"GAZP","period":"month"}'
```

---

## 📊 Часть 8: Мониторинг и логи

### 8.1. Просмотр логов backend

Логи сохраняются в `backend/logs/`:
```powershell
# Последние логи:
Get-Content logs\training_*.log -Tail 50
```

### 8.2. Мониторинг БД

```powershell
# Подключиться к PostgreSQL:
docker exec -it invest_mrsu_db psql -U postgres -d invest_mrsu

# SQL запросы:
SELECT ticker, COUNT(*) FROM stock_data GROUP BY ticker;
SELECT * FROM predictions ORDER BY prediction_date DESC LIMIT 10;
```

### 8.3. Проверка статуса

Создайте `check_status.ps1`:
```powershell
# Проверка статуса всех компонентов
Write-Host "=== Проверка статуса Invest MRSU ===" -ForegroundColor Green

# 1. Docker
Write-Host "`n1. Docker контейнеры:" -ForegroundColor Yellow
docker ps --filter "name=invest_mrsu"

# 2. Backend API
Write-Host "`n2. Backend API:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing
    Write-Host "✓ Backend работает" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend не доступен" -ForegroundColor Red
}

# 3. Модели
Write-Host "`n3. ML Модели:" -ForegroundColor Yellow
Get-ChildItem models\*.keras | ForEach-Object {
    Write-Host "  ✓ $($_.Name)" -ForegroundColor Green
}
```

---

## ⚡ Часть 9: Оптимизация для демонстрации

### 9.1. Создать desktop ярлык для запуска

Создайте файл `start_server.bat`:
```batch
@echo off
echo ========================================
echo   Запуск Invest MRSU ML Server
echo ========================================

cd /d C:\investApp\invest_mrsu\backend

echo.
echo [1/3] Запуск базы данных...
docker-compose up -d db
timeout /t 5

echo.
echo [2/3] Активация виртуального окружения...
call venv\Scripts\activate.bat

echo.
echo [3/3] Запуск backend API...
echo.
echo Backend будет доступен по адресу:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| find "IPv4"') do echo   http://%%a:8000
echo.
echo Нажмите Ctrl+C для остановки
echo.

python main.py

pause
```

### 9.2. Автозапуск при включении компьютера

1. Создать ярлык для `start_server.bat`
2. Поместить в:
   ```
   C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
   ```

---

## 🔍 Часть 10: Решение проблем

### Проблема 1: "Connection refused" в Flutter

**Причина**: Неправильный IP или брандмауэр  
**Решение**:
```powershell
# Проверить IP:
ipconfig

# Проверить доступность с телефона:
curl http://<IP>:8000/
```

### Проблема 2: "Model not found"

**Причина**: Модели не обучены  
**Решение**:
```powershell
python ml/trainer.py
```

### Проблема 3: БД не запускается

**Причина**: Docker не запущен  
**Решение**:
```powershell
# Запустить Docker Desktop
# Затем:
docker-compose up -d db
```

### Проблема 4: Медленные предсказания

**Причина**: Нет кеширования или слабый процессор  
**Решение**:
- Кеш включен по умолчанию (TTL = 24ч)
- Первый запрос медленный, последующие быстрые

---

## 📝 Чеклист перед демонстрацией

- [ ] Docker Desktop запущен
- [ ] PostgreSQL работает (`docker ps`)
- [ ] Данные загружены (проверить через `/history/GAZP`)
- [ ] Модели обучены (проверить папку `models/`)
- [ ] Backend запущен (`http://localhost:8000/`)
- [ ] Брандмауэр настроен (порт 8000 открыт)
- [ ] Flutter приложение подключено к правильному IP
- [ ] Тесты пройдены (`python test/test_api.py`)

---

## 🎯 Краткая инструкция для демо

### Запуск сервера (разово):
```powershell
# 1. Запустить Docker Desktop

# 2. В backend папке:
docker-compose up -d db
.\venv\Scripts\activate
python main.py
```

### Запуск Flutter приложения:
```bash
flutter run -d windows
```

### Обновить данные перед демо:
```powershell
curl -X POST http://localhost:8000/admin/update_moex
```

---

## 📞 Полезные команды

```powershell
# Узнать IP сервера:
ipconfig | findstr IPv4

# Остановить все:
docker-compose down
# Ctrl+C в окне backend

# Перезапустить БД:
docker-compose restart db

# Просмотр статистики БД:
docker exec -it invest_mrsu_db psql -U postgres -d invest_mrsu -c "SELECT ticker, COUNT(*) as records FROM stock_data GROUP BY ticker;"
```

---

## 🌟 Рекомендации

1. **Стабильность сети**: Используйте Ethernet вместо Wi-Fi для сервера
2. **Резервное копирование**: Периодически копируйте папку `models/`
3. **Производительность**: Закройте ненужные программы на сервере
4. **Безопасность**: Не открывайте порт 8000 в интернет (только локальная сеть)
5. **Демонстрация**: Подготовьте несколько тикеров для показа (GAZP, SIBN, GCHE)

---

**Успешной демонстрации! 🚀**
