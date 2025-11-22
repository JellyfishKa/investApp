# Руководство по сборке приложения Invest MRSU
## Подготовка к демонстрации

---

## Сборка для Windows

### Вариант 1: Debug версия (для тестирования)

```bash
cd invest_mrsu
flutter run -d windows
```

**Результат:** Приложение запустится в режиме разработки

### Вариант 2: Release версия (для демонстрации)

```bash
cd invest_mrsu
flutter build windows --release
```

**Результат:** Готовое приложение в папке:
```
invest_mrsu\build\windows\x64\runner\Release\
```

**Файлы для запуска:**
- `invest_mrsu.exe` - главный исполняемый файл
- Все `.dll` файлы в той же папке (нужны для работы!)

### Создание портативной версии для Windows

```bash
# 1. Собрать release версию
flutter build windows --release

# 2. Скопировать всю папку Release в удобное место
cd build\windows\x64\runner
mkdir "C:\InvestMRSU_Demo"
xcopy Release "C:\InvestMRSU_Demo" /E /I

# 3. Теперь можно запустить из C:\InvestMRSU_Demo\invest_mrsu.exe
```

**Размер:** ~40-50 МБ

**Совет:** Можно заархивировать папку и отправить кому угодно - не требует установки!

---

## Сборка для Android

### Проверка готовности

```bash
# Проверить, что Android SDK настроен
flutter doctor -v

# Должно быть:
# ✓ Android toolchain
# ✓ Android Studio (или Android SDK)
```

### Вариант 1: APK файл (универсальный)

```bash
cd invest_mrsu
flutter build apk --release
```

**Результат:** APK файл в:
```
invest_mrsu\build\app\outputs\flutter-apk\app-release.apk
```

**Размер:** ~20-30 МБ

**Как установить на телефон:**
1. Скопировать `app-release.apk` на телефон
2. Разрешить установку из неизвестных источников
3. Открыть файл и установить

### Вариант 2: Split APK (оптимизированный)

```bash
flutter build apk --split-per-abi --release
```

**Результат:** 3 отдельных APK для разных архитектур:
- `app-armeabi-v7a-release.apk` - для старых телефонов (ARM 32-bit)
- `app-arm64-v8a-release.apk` - для современных телефонов (ARM 64-bit) ← **используйте этот**
- `app-x86_64-release.apk` - для эмуляторов

**Размер каждого:** ~10-15 МБ (меньше!)

### Вариант 3: App Bundle (для Google Play)

```bash
flutter build appbundle --release
```

**Результат:** AAB файл в:
```
invest_mrsu\build\app\outputs\bundle\release\app-release.aab
```

**Использование:** Только для загрузки в Google Play Store

---

## Тестирование на реальных устройствах

### Android телефон

```bash
# 1. Подключить телефон по USB
# 2. Включить "Режим разработчика" и "Отладка по USB"
# 3. Проверить подключение
flutter devices

# 4. Запустить на телефоне
flutter run -d <device_id>

# Или собрать и установить APK
flutter build apk --release
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Windows компьютер

```bash
# Запустить на текущем компьютере
flutter run -d windows

# Или запустить release версию
cd build\windows\x64\runner\Release
invest_mrsu.exe
```

---

## Подготовка к демонстрации

### Чек-лист перед показом

```bash
# 1. Убедиться, что все зависимости установлены
cd invest_mrsu
flutter pub get

# 2. Запустить приложение и проверить
flutter run -d windows

# 3. Проверить все экраны:
#    - Вход/Регистрация
#    - Дашборд
#    - Список акций
#    - График цен
#    - Прогнозы
#    - Дивиденды
#    - Портфель
#    - Задания

# 4. Собрать release версии
flutter build windows --release
flutter build apk --release
```

### Создать demo-пакет

```bash
# 1. Создать папку для демонстрации
mkdir InvestMRSU_Demo
cd InvestMRSU_Demo

# 2. Скопировать Windows версию
mkdir Windows
xcopy ..\invest_mrsu\build\windows\x64\runner\Release Windows\ /E /I

# 3. Скопировать Android APK
mkdir Android
copy ..\invest_mrsu\build\app\outputs\flutter-apk\app-release.apk Android\

# 4. Добавить README
echo "Invest MRSU - Demo Package" > README.txt
echo "" >> README.txt
echo "Windows: Запустить Windows\invest_mrsu.exe" >> README.txt
echo "Android: Установить Android\app-release.apk на телефон" >> README.txt

# 5. Заархивировать
# Можно использовать WinRAR, 7-Zip или встроенный архиватор Windows
```

---

## Улучшение для демонстрации

### Добавить иконку приложения

```bash
# 1. Установить flutter_launcher_icons
flutter pub add dev:flutter_launcher_icons

# 2. Добавить иконку в pubspec.yaml
# flutter_icons:
#   android: true
#   ios: true
#   image_path: "assets/icon/app_icon.png"

# 3. Сгенерировать иконки
flutter pub run flutter_launcher_icons
```

### Изменить название приложения

**Для Android:**
Отредактировать `android/app/src/main/AndroidManifest.xml`:
```xml
<application
    android:label="Invest MRSU"
    ...>
```

**Для Windows:**
Отредактировать `windows/runner/main.cpp`:
```cpp
window.Create(L"Invest MRSU", origin, size);
```

---

## Команды быстрого доступа

### Полная пересборка (если что-то сломалось)

```bash
# Очистить кеш
flutter clean

# Переустановить зависимости
flutter pub get

# Собрать заново
flutter build windows --release
flutter build apk --release
```

### Проверка производительности

```bash
# Запустить в profile режиме (для анализа)
flutter run --profile -d windows

# Измерить размер приложения
flutter build apk --analyze-size
```

### Логи для отладки

```bash
# Просмотреть логи Android
adb logcat -s flutter

# Запустить с подробными логами
flutter run -d windows --verbose
```

---

## Распространенные проблемы

### Проблема 1: "flutter: command not found"

**Решение:**
```bash
# Проверить PATH
echo $PATH  # Linux/Mac
echo %PATH%  # Windows

# Добавить Flutter в PATH (Windows)
setx PATH "%PATH%;C:\flutter\bin"
```

### Проблема 2: Android build failed

**Решение:**
```bash
# Обновить Gradle
cd android
./gradlew wrapper --gradle-version 7.6

# Очистить и пересобрать
cd ..
flutter clean
flutter build apk --release
```

### Проблема 3: Windows build очень большой

**Решение:**
- Это нормально для Flutter Windows (40-50 МБ)
- Можно сжать ZIP архивом (~20 МБ)
- Для production можно использовать MSIX installer

### Проблема 4: Приложение запускается, но вылетает

**Решение:**
```bash
# Проверить логи
flutter run -d windows --verbose

# Пересобрать в debug режиме для отладки
flutter build windows --debug
```

---

## Оптимизация размера

### Android

```bash
# Использовать split APK
flutter build apk --split-per-abi --release

# Включить обфускацию (для production)
flutter build apk --release --obfuscate --split-debug-info=build/debug-info
```

### Windows

```bash
# Использовать сжатие
# После сборки запаковать UPX (опционально)
# Или просто заархивировать ZIP

# Сборка с оптимизацией
flutter build windows --release --tree-shake-icons
```

---

## Краткая шпаргалка

```bash
# === WINDOWS ===

# Запустить (debug)
flutter run -d windows

# Собрать (release)
flutter build windows --release

# Где файл:
# build\windows\x64\runner\Release\invest_mrsu.exe


# === ANDROID ===

# Собрать APK
flutter build apk --release

# Где файл:
# build\app\outputs\flutter-apk\app-release.apk

# Установить на телефон
adb install build/app/outputs/flutter-apk/app-release.apk


# === ОЧИСТКА ===

# Очистить всё
flutter clean
flutter pub get

# Пересобрать
flutter build windows --release
flutter build apk --release
```

---

## Для презентации экспертной комиссии

### Рекомендации:

1. **Подготовить обе версии:**
   - Windows - для показа на проекторе/мониторе
   - Android - для демонстрации на телефоне

2. **Создать тестовые данные:**
   - Зарегистрируйте тестовый аккаунт
   - Купите несколько акций
   - Выполните пару заданий

3. **Подготовить сценарий демонстрации:**
   - Показать регистрацию → Дашборд
   - Открыть акцию → Графики → Прогнозы
   - Показать покупку акций → Портфель
   - Показать систему заданий

4. **План Б:**
   - Записать видео демонстрацию заранее
   - Сделать скриншоты ключевых экранов
   - Подготовить презентацию PowerPoint с функционалом

---

**Готово!** Теперь у вас есть полное руководство по сборке приложения для демонстрации.

**Быстрый старт для демо:**
```bash
cd invest_mrsu
flutter build windows --release
flutter build apk --release
```

Готовые файлы:
- Windows: `build\windows\x64\runner\Release\invest_mrsu.exe`
- Android: `build\app\outputs\flutter-apk\app-release.apk`
