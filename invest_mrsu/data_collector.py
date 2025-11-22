"""
Скрипт для автоматического сбора данных для ML модели
Invest MRSU - Data Collector

Использование:
    python data_collector.py --start 2022-01-01 --end 2024-11-20
"""

import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import os
from pathlib import Path

# Конфигурация
TICKERS = ['GAZP', 'GAZP-p', 'SIBN', 'GCHE', 'MRKZ']
OUTPUT_DIR = 'dataset'

class MOEXDataCollector:
    """Сборщик данных с Московской Биржи"""

    BASE_URL = 'https://iss.moex.com/iss'

    def __init__(self):
        self.session = requests.Session()

    def get_stock_history(self, ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Получить исторические данные по акции

        Args:
            ticker: тикер акции (GAZP, SIBN, и т.д.)
            start_date: дата начала (YYYY-MM-DD)
            end_date: дата окончания (YYYY-MM-DD)

        Returns:
            DataFrame с колонками: Date, Open, Close, High, Low, Volume
        """
        print(f"📊 Скачивание данных для {ticker}...")

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

                # Пауза, чтобы не нагружать API
                time.sleep(0.5)

            except Exception as e:
                print(f"❌ Ошибка при скачивании {ticker}: {e}")
                break

        # Преобразование в DataFrame
        if not all_data:
            print(f"⚠️  Нет данных для {ticker}")
            return pd.DataFrame()

        columns = data['history']['columns']
        df = pd.DataFrame(all_data, columns=columns)

        # Выбираем нужные колонки и переименовываем
        df = df[['TRADEDATE', 'OPEN', 'CLOSE', 'HIGH', 'LOW', 'VOLUME']]
        df.columns = ['Date', 'Open', 'Close', 'High', 'Low', 'Volume']

        # Преобразуем типы
        df['Date'] = pd.to_datetime(df['Date'])
        df['Open'] = pd.to_numeric(df['Open'])
        df['Close'] = pd.to_numeric(df['Close'])
        df['High'] = pd.to_numeric(df['High'])
        df['Low'] = pd.to_numeric(df['Low'])
        df['Volume'] = pd.to_numeric(df['Volume'])

        # Сортируем по дате
        df = df.sort_values('Date').reset_index(drop=True)

        print(f"✅ Скачано {len(df)} записей для {ticker}")
        return df


class MacroDataCollector:
    """Сборщик макроэкономических данных"""

    def get_oil_prices(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Получить цены на нефть Brent

        Примечание: Здесь используется заглушка.
        Для реальных данных используйте API от:
        - Alpha Vantage (бесплатно, но нужен API ключ)
        - Quandl
        - Yahoo Finance
        """
        print("📊 Скачивание данных по нефти Brent...")

        # Заглушка - генерация синтетических данных
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        # В реальности здесь должен быть API запрос
        prices = pd.DataFrame({
            'Date': dates,
            'Oil_Brent_USD': 75 + (dates.day % 10) - 5  # заглушка
        })

        print("⚠️  Используются синтетические данные. Замените на реальные!")
        return prices

    def get_currency_rates(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Получить курсы валют с ЦБ РФ

        API ЦБ РФ: https://www.cbr.ru/development/sxml/
        """
        print("📊 Скачивание курсов валют...")

        # Заглушка
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        rates = pd.DataFrame({
            'Date': dates,
            'USD_RUB': 75 + (dates.day % 5) - 2,  # заглушка
            'EUR_RUB': 85 + (dates.day % 5) - 2,  # заглушка
        })

        print("⚠️  Используются синтетические данные. Замените на реальные!")
        return rates

    def get_moex_index(self, start_date: str, end_date: str) -> pd.DataFrame:
        """Получить индекс MOEX"""
        print("📊 Скачивание индекса MOEX...")

        # В реальности используйте MOEX API
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        index = pd.DataFrame({
            'Date': dates,
            'MOEX_Index': 3000 + (dates.day % 100),  # заглушка
        })

        print("⚠️  Используются синтетические данные. Замените на реальные!")
        return index


def create_directory_structure():
    """Создать структуру папок для датасета"""
    dirs = [
        f'{OUTPUT_DIR}/stocks',
        f'{OUTPUT_DIR}/fundamentals',
        f'{OUTPUT_DIR}/macro'
    ]

    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📁 Создана папка: {dir_path}")


def collect_stock_data(start_date: str, end_date: str):
    """Собрать данные по всем акциям"""
    collector = MOEXDataCollector()

    for ticker in TICKERS:
        try:
            df = collector.get_stock_history(ticker, start_date, end_date)

            if not df.empty:
                output_path = f'{OUTPUT_DIR}/stocks/{ticker}.csv'
                df.to_csv(output_path, index=False)
                print(f"💾 Сохранено: {output_path}\n")
            else:
                print(f"⚠️  Пропускаем {ticker} - нет данных\n")

        except Exception as e:
            print(f"❌ Ошибка для {ticker}: {e}\n")

        time.sleep(1)  # Пауза между запросами


def collect_macro_data(start_date: str, end_date: str):
    """Собрать макроэкономические данные"""
    collector = MacroDataCollector()

    # Нефть
    oil = collector.get_oil_prices(start_date, end_date)

    # Валюты
    currency = collector.get_currency_rates(start_date, end_date)

    # Индекс MOEX
    moex = collector.get_moex_index(start_date, end_date)

    # Объединяем все
    macro = oil.merge(currency, on='Date', how='outer')
    macro = macro.merge(moex, on='Date', how='outer')

    # Добавляем ключевую ставку (меняется редко, поэтому константа)
    macro['CB_Rate'] = 16.0  # актуальная ставка на ноябрь 2024

    # Сортируем и заполняем пропуски
    macro = macro.sort_values('Date')
    macro = macro.fillna(method='ffill')  # заполняем выходные предыдущим значением

    # Сохраняем
    output_path = f'{OUTPUT_DIR}/macro/macro_indicators.csv'
    macro.to_csv(output_path, index=False)
    print(f"💾 Сохранено: {output_path}\n")


def validate_data():
    """Проверить качество собранных данных"""
    print("\n" + "="*50)
    print("🔍 ПРОВЕРКА КАЧЕСТВА ДАННЫХ")
    print("="*50 + "\n")

    stocks_dir = f'{OUTPUT_DIR}/stocks'

    for ticker in TICKERS:
        file_path = f'{stocks_dir}/{ticker}.csv'

        if not os.path.exists(file_path):
            print(f"❌ {ticker}: Файл не найден")
            continue

        df = pd.read_csv(file_path)

        print(f"📊 {ticker}:")
        print(f"   Строк: {len(df)}")
        print(f"   Период: {df['Date'].min()} - {df['Date'].max()}")
        print(f"   Пропуски: {df.isnull().sum().sum()}")

        # Проверка на аномалии
        if (df['Close'] <= 0).any():
            print(f"   ⚠️  ВНИМАНИЕ: Есть нулевые/отрицательные цены!")

        if (df['Volume'] < 0).any():
            print(f"   ⚠️  ВНИМАНИЕ: Есть отрицательные объемы!")

        print()


def create_fundamentals_template():
    """Создать шаблон для фундаментальных данных"""
    template = pd.DataFrame({
        'Date': ['2022-Q1', '2022-Q2', '2022-Q3', '2022-Q4'],
        'Revenue_bn': [0.0, 0.0, 0.0, 0.0],
        'EBITDA_bn': [0.0, 0.0, 0.0, 0.0],
        'Net_profit_bn': [0.0, 0.0, 0.0, 0.0],
        'Debt_bn': [0.0, 0.0, 0.0, 0.0],
        'Dividend': [0.0, 0.0, 0.0, 0.0],
    })

    output_path = f'{OUTPUT_DIR}/fundamentals/GAZP_fundamentals_TEMPLATE.csv'
    template.to_csv(output_path, index=False)
    print(f"📝 Создан шаблон: {output_path}")
    print("   Заполните его вручную данными из отчетности!\n")


def main():
    """Главная функция"""
    print("="*60)
    print("  INVEST MRSU - DATA COLLECTOR")
    print("  Автоматический сбор данных для ML модели")
    print("="*60 + "\n")

    # Параметры
    START_DATE = '2022-01-01'
    END_DATE = datetime.now().strftime('%Y-%m-%d')

    print(f"📅 Период: {START_DATE} - {END_DATE}\n")

    # Шаг 1: Создать структуру
    print("Шаг 1/5: Создание структуры папок...")
    create_directory_structure()
    print()

    # Шаг 2: Собрать данные по акциям
    print("Шаг 2/5: Сбор данных по акциям...")
    collect_stock_data(START_DATE, END_DATE)

    # Шаг 3: Собрать макроданные
    print("Шаг 3/5: Сбор макроэкономических данных...")
    collect_macro_data(START_DATE, END_DATE)

    # Шаг 4: Создать шаблон для фундаментальных данных
    print("Шаг 4/5: Создание шаблона для фундаментальных данных...")
    create_fundamentals_template()

    # Шаг 5: Валидация
    print("Шаг 5/5: Проверка качества данных...")
    validate_data()

    print("="*60)
    print("✅ ГОТОВО!")
    print("="*60)
    print(f"\nДанные сохранены в папке: {OUTPUT_DIR}/")
    print("\n📝 Следующие шаги:")
    print("1. Заполните шаблон фундаментальных данных")
    print("2. Проверьте макроданные (они синтетические!)")
    print("3. Передайте данные разработчику ML модели")
    print("\n📚 См. DATASET_COLLECTION_GUIDE.md для подробностей")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем")
    except Exception as e:
        print(f"\n\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
