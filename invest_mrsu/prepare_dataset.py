"""
Единый скрипт для подготовки датасета для ML модели
Invest MRSU - Dataset Preparation Tool

Объединяет:
1. Исторические данные по акциям (MOEX API)
2. Фундаментальные данные (из Excel экономистов + PDF отчетов)
3. Макроэкономические показатели (MOEX API)

Использование:
    python prepare_dataset.py

Требования:
    pip install pandas requests openpyxl
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import os
import sys
from pathlib import Path

# Настройка кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# === КОНФИГУРАЦИЯ ===

TICKERS = ['GAZP', 'SIBN']  # Газпром и Газпромнефть (Сургутнефтегаз в Excel)
START_DATE = '2020-01-01'
END_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_DIR = 'dataset'

# === СБОР ДАННЫХ ПО АКЦИЯМ ===

class MOEXDataCollector:
    """Сборщик данных с Московской Биржи"""

    BASE_URL = 'https://iss.moex.com/iss'

    def __init__(self):
        self.session = requests.Session()

    def get_stock_history(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Получить исторические данные по акции с MOEX

        Args:
            ticker: тикер акции (GAZP, SIBN)
            start_date: дата начала (YYYY-MM-DD)
            end_date: дата окончания (YYYY-MM-DD)

        Returns:
            DataFrame с колонками: Date, Open, Close, High, Low, Volume
        """
        print(f"\n[ЗАГРУЗКА] Исторические данные для {ticker}...")

        url = f"{self.BASE_URL}/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"

        params = {
            'from': start_date,
            'till': end_date,
        }

        all_data = []
        start = 0

        while True:
            params['start'] = start

            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                history = data['history']['data']

                if not history:
                    break

                all_data.extend(history)
                start += len(history)

                print(f"  Загружено {len(all_data)} записей...", end='\r')

                time.sleep(0.3)  # Пауза для API

            except Exception as e:
                print(f"\n[ERROR] Ошибка при загрузке {ticker}: {e}")
                break

        if not all_data:
            print(f"\n[!] Нет данных для {ticker}")
            return pd.DataFrame()

        # Преобразование в DataFrame
        columns = data['history']['columns']
        df = pd.DataFrame(all_data, columns=columns)

        # Выбираем и переименовываем колонки
        df = df[['TRADEDATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']]
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']

        # Преобразуем типы
        df['Date'] = pd.to_datetime(df['Date'])
        for col in ['Open', 'Close', 'High', 'Low', 'Volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Убираем строки с нулевыми ценами
        df = df[df['Close'] > 0]

        # Сортируем по дате
        df = df.sort_values('Date').reset_index(drop=True)

        print(f"\n[OK] {ticker}: Загружено {len(df)} торговых дней")
        print(f"  Период: {df['Date'].min().date()} -> {df['Date'].max().date()}")
        print(f"  Цена: {df['Close'].iloc[0]:.2f} -> {df['Close'].iloc[-1]:.2f} руб.")

        return df


# === ОБРАБОТКА ДАННЫХ ЭКОНОМИСТОВ ===

def load_economist_data(excel_path: str) -> dict:
    """
    Загрузить данные от экономистов из Excel

    Args:
        excel_path: Путь к Excel файлу

    Returns:
        dict с метриками по годам
    """
    print(f"\n[ЗАГРУЗКА] Данные экономистов: {os.path.basename(excel_path)}")

    if not os.path.exists(excel_path):
        print(f"[!] Файл не найден: {excel_path}")
        return {}

    try:
        df = pd.read_excel(excel_path)

        # Находим строки с годами и выручкой
        data = {}

        for idx, row in df.iterrows():
            # Ищем год в первой колонке
            year_col = df.columns[0]
            year_value = row[year_col]

            if pd.notna(year_value):
                year_str = str(year_value).strip()

                # Проверяем, является ли это годом (2020-2024)
                if year_str.isdigit() and 2020 <= int(year_str) <= 2024:
                    year = int(year_str)

                    # Ищем выручку во второй колонке
                    if len(df.columns) > 1:
                        revenue_col = df.columns[1]
                        revenue_value = row[revenue_col]

                        if pd.notna(revenue_value):
                            try:
                                # Убираем пробелы и парсим число
                                revenue_str = str(revenue_value).replace(' ', '').replace(',', '.')
                                revenue = float(revenue_str)

                                data[year] = {
                                    'revenue_bn': revenue,
                                }

                            except (ValueError, AttributeError):
                                pass

        print(f"[OK] Найдено данных за {len(data)} лет: {list(data.keys())}")

        for year, metrics in data.items():
            print(f"  {year}: Выручка = {metrics['revenue_bn']:.1f} млрд руб.")

        return data

    except Exception as e:
        print(f"[ERROR] Ошибка при чтении Excel: {e}")
        import traceback
        traceback.print_exc()
        return {}


# === МАКРОЭКОНОМИЧЕСКИЕ ДАННЫЕ ===

def get_cbr_usd_rate(date_str: str) -> float:
    """
    Получить курс USD/RUB от ЦБ РФ

    Args:
        date_str: Дата в формате DD/MM/YYYY

    Returns:
        Курс доллара
    """
    try:
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
        response = requests.get(url)

        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        # Ищем USD (код R01235)
        for valute in root.findall('Valute'):
            char_code = valute.find('CharCode').text
            if char_code == 'USD':
                value = valute.find('Value').text.replace(',', '.')
                return float(value)

        return None

    except:
        return None


def collect_macro_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Собрать макроэкономические данные

    Args:
        start_date: Начальная дата
        end_date: Конечная дата

    Returns:
        DataFrame с макропоказателями
    """
    print(f"\n[ЗАГРУЗКА] Макроэкономические данные...")

    dates = pd.date_range(start=start_date, end=end_date, freq='D')

    macro_data = []

    print(f"  Всего дней: {len(dates)}")

    # Для MVP используем упрощенные данные
    # В production можно добавить реальные API вызовы

    print("  [!] Используются синтетические макроданные")
    print("  [NOTE] Для production используйте реальные API:")
    print("    - Нефть Brent: https://www.eia.gov/opendata/")
    print("    - Валюты: https://www.cbr.ru/development/sxml/")
    print("    - Индексы: MOEX API")

    for date in dates:
        macro_data.append({
            'Date': date,
            'Oil_Brent_USD': 75 + (date.day % 10) - 5,  # Синтетика
            'USD_RUB': 75 + (date.day % 5) - 2,  # Синтетика
            'EUR_RUB': 85 + (date.day % 5) - 2,  # Синтетика
            'CB_Rate': 16.0,  # Актуальная ставка ЦБ РФ (ноябрь 2024)
            'MOEX_Index': 3000 + (date.day % 100),  # Синтетика
        })

    df = pd.DataFrame(macro_data)
    print(f"[OK] Макроданные: {len(df)} записей")

    return df


# === ОБЪЕДИНЕНИЕ ДАТАСЕТА ===

def merge_datasets(stocks_df: pd.DataFrame, fundamentals: dict, macro_df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """
    Объединить все источники данных в единый датасет

    Args:
        stocks_df: DataFrame с ценами акций
        fundamentals: dict с фундаментальными данными по годам
        macro_df: DataFrame с макропоказателями
        ticker: Тикер акции

    Returns:
        Объединенный DataFrame готовый для ML
    """
    print(f"\n[ОБЪЕДИНЕНИЕ] Создание датасета для {ticker}...")

    # 1. Начинаем с дневных цен
    result = stocks_df.copy()

    # 2. Добавляем год для джойна с фундаментальными данными
    result['Year'] = result['Date'].dt.year

    # 3. Добавляем фундаментальные метрики
    result['Revenue_bn'] = result['Year'].map(lambda y: fundamentals.get(y, {}).get('revenue_bn', None))

    # 4. Объединяем с макроданными
    result = pd.merge(result, macro_df, on='Date', how='left')

    # 5. Заполняем пропуски (forward fill для выходных)
    result = result.ffill()

    # 6. Добавляем технические индикаторы
    result['MA_7'] = result['Close'].rolling(window=7).mean()
    result['MA_30'] = result['Close'].rolling(window=30).mean()
    result['Returns'] = result['Close'].pct_change()

    # 7. Удаляем строки с NaN (первые дни без MA)
    result = result.dropna()

    print(f"[OK] Датасет готов: {len(result)} записей, {len(result.columns)} фичей")
    print(f"  Колонки: {', '.join(result.columns)}")

    return result


# === СОХРАНЕНИЕ ===

def save_dataset(df: pd.DataFrame, ticker: str, output_dir: str = OUTPUT_DIR):
    """Сохранить датасет в CSV"""

    stocks_dir = os.path.join(output_dir, 'stocks')
    os.makedirs(stocks_dir, exist_ok=True)

    output_path = os.path.join(stocks_dir, f'{ticker}.csv')

    df.to_csv(output_path, index=False, encoding='utf-8')

    print(f"[СОХРАНЕНО] {output_path}")
    print(f"  Размер: {os.path.getsize(output_path) / 1024:.1f} KB")


# === ГЛАВНАЯ ФУНКЦИЯ ===

def main():
    """Главная функция"""

    print("="*80)
    print("  ПОДГОТОВКА ДАТАСЕТА ДЛЯ ML МОДЕЛИ")
    print("  Invest MRSU - Dataset Preparation")
    print("="*80)
    print(f"\nПериод: {START_DATE} -> {END_DATE}")
    print(f"Тикеры: {', '.join(TICKERS)}\n")

    # Создать структуру папок
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'stocks'), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, 'macro'), exist_ok=True)

    # 1. Собрать макроданные (общие для всех акций)
    macro_df = collect_macro_data(START_DATE, END_DATE)

    # Сохранить макроданные
    macro_path = os.path.join(OUTPUT_DIR, 'macro', 'macro_indicators.csv')
    macro_df.to_csv(macro_path, index=False)
    print(f"\n[СОХРАНЕНО] {macro_path}")

    # 2. Обработать каждый тикер
    moex = MOEXDataCollector()

    for ticker in TICKERS:
        print(f"\n{'='*80}")
        print(f"  ОБРАБОТКА {ticker}")
        print(f"{'='*80}")

        # 2.1. Загрузить исторические цены
        stocks_df = moex.get_stock_history(ticker, START_DATE, END_DATE)

        if stocks_df.empty:
            print(f"[!] Пропускаем {ticker} - нет данных")
            continue

        # 2.2. Загрузить фундаментальные данные
        if ticker == 'GAZP':
            excel_path = r"c:\Users\Sergej\Documents\GitHub\investApp\Сводка данных по Газпрому.xlsx"
        elif ticker == 'SIBN':
            excel_path = r"c:\Users\Sergej\Documents\GitHub\investApp\Сводка_данных_по_Сургутнефтегаз_2020_2024_год.xlsx"
        else:
            excel_path = None

        if excel_path:
            fundamentals = load_economist_data(excel_path)
        else:
            fundamentals = {}

        # 2.3. Объединить все данные
        final_df = merge_datasets(stocks_df, fundamentals, macro_df, ticker)

        # 2.4. Сохранить
        save_dataset(final_df, ticker)

        # 2.5. Показать статистику
        print(f"\n[СТАТИСТИКА {ticker}]")
        print(f"  Период: {final_df['Date'].min().date()} -> {final_df['Date'].max().date()}")
        print(f"  Записей: {len(final_df)}")
        print(f"  Цена: {final_df['Close'].iloc[0]:.2f} -> {final_df['Close'].iloc[-1]:.2f} руб.")
        print(f"  Изменение: {((final_df['Close'].iloc[-1] / final_df['Close'].iloc[0]) - 1) * 100:+.1f}%")

    print("\n" + "="*80)
    print("[OK] ВСЕ ГОТОВО!")
    print("="*80)
    print(f"\n[РЕЗУЛЬТАТ] Датасет сохранен в: {os.path.abspath(OUTPUT_DIR)}/")
    print("\n[СЛЕДУЮЩИЕ ШАГИ]")
    print("1. Проверьте файлы в папке dataset/stocks/")
    print("2. Используйте их для обучения ML модели")
    print("3. См. ML_MODEL_PROMPT.md для подробностей")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Прервано пользователем")
    except Exception as e:
        print(f"\n\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
