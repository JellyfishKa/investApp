"""
Тестовый скрипт для проверки ML модели
Запуск: python test_ml.py
"""
import sys
import os

# Добавляем backend в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


def test_preprocessor():
    """Тест препроцессора"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Препроцессор")
    print("="*60)
    
    from ml.preprocessor import DataPreprocessor
    
    # Создаем тестовые данные
    dates = pd.date_range(end=datetime.now(), periods=200, freq='D')
    test_data = pd.DataFrame({
        'date': dates,
        'open': 170 + np.random.randn(200) * 5,
        'close': 173 + np.random.randn(200) * 5,
        'high': 175 + np.random.randn(200) * 3,
        'low': 170 + np.random.randn(200) * 3,
        'volume': 1000000 + np.random.randint(-100000, 100000, 200)
    })
    
    print(f"✓ Создано {len(test_data)} дней тестовых данных")
    
    # Создаем индикаторы
    preprocessor = DataPreprocessor('TEST')
    df_with_indicators = preprocessor.create_technical_indicators(test_data)
    
    print(f"✓ Добавлено {len(df_with_indicators.columns)} признаков")
    print(f"  Признаки: {', '.join(df_with_indicators.columns[:10])}...")
    
    # Создаем последовательности
    X, y = preprocessor.prepare_sequences(df_with_indicators, sequence_length=60, target_days=30)
    
    print(f"✓ Создано {len(X)} последовательностей")
    print(f"  Форма X: {X.shape}")
    print(f"  Форма y: {y.shape}")
    
    # Разделение данных
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.split_data(X, y)
    
    print(f"✓ Разделение данных:")
    print(f"  Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    return True


def test_lstm_model():
    """Тест LSTM модели"""
    print("\n" + "="*60)
    print("ТЕСТ 2: LSTM Модель")
    print("="*60)
    
    from ml.model import LSTMStockModel
    
    # Создаем модель
    model = LSTMStockModel(ticker='TEST', sequence_length=60, num_features=17)
    keras_model = model.build_model()
    
    print(f"✓ Модель создана")
    print(f"  Параметров: {keras_model.count_params():,}")
    print(f"  Слоев: {len(keras_model.layers)}")
    
    # Тестовые данные
    X_test = np.random.rand(10, 60, 17)
    
    # Предсказание
    predictions = model.predict(X_test)
    
    print(f"✓ Предсказание работает")
    print(f"  Входных последовательностей: {len(X_test)}")
    print(f"  Предсказаний: {len(predictions)}")
    print(f"  Пример предсказания: {predictions[0]:.4f}")
    
    return True


def test_data_collector():
    """Тест сборщика данных MOEX"""
    print("\n" + "="*60)
    print("ТЕСТ 3: MOEX Data Collector")
    print("="*60)
    
    from services.moex import MOEXCollector
    
    collector = MOEXCollector()
    
    print(f"✓ Collector инициализирован")
    print(f"  Тикеров для сбора: {len(collector.TICKERS)}")
    print(f"  Тикеры: {', '.join(collector.TICKERS)}")
    
    # Тестовый запрос (небольшой период)
    try:
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        df = collector.fetch_history(
            'GAZP',
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        
        if not df.empty:
            print(f"✓ Данные получены с MOEX")
            print(f"  Строк: {len(df)}")
            print(f"  Период: {df['date'].min()} - {df['date'].max()}")
        else:
            print("⚠️  MOEX вернул пустой ответ (возможно, выходной)")
        
    except Exception as e:
        print(f"⚠️  Ошибка MOEX API: {e}")
        print("  (Это нормально если нет интернета)")
    
    return True


def test_csv_importer():
    """Тест импортера CSV"""
    print("\n" + "="*60)
    print("ТЕСТ 4: CSV Importer")
    print("="*60)
    
    from services.importer import CSVImporter
    
    # Тестовые CSV данные
    fundamental_csv = """Date,Revenue_bn,EBITDA_bn,Net_profit_bn,Debt_bn,Dividend
2022-Q1,100.5,50.2,30.1,200.0,10.5
2022-Q2,105.0,52.0,32.0,195.0,11.0"""
    
    macro_csv = """Date,Oil_Brent_USD,USD_RUB,EUR_RUB,MOEX_Index,CB_Rate
2024-01-01,75.5,75.2,85.1,3000.5,16.0
2024-01-02,76.0,75.5,85.5,3010.0,16.0"""
    
    print("✓ CSV данные подготовлены")
    print(f"  Fundamental: {len(fundamental_csv.splitlines())} строк")
    print(f"  Macro: {len(macro_csv.splitlines())} строк")
    
    # Парсинг дат
    importer = CSVImporter()
    
    try:
        date = importer._parse_quarter_date('2022-Q1')
        print(f"✓ Парсинг квартальных дат работает")
        print(f"  2022-Q1 -> {date}")
    except Exception as e:
        print(f"✗ Ошибка парсинга: {e}")
        return False
    
    return True


def main():
    """Запуск всех тестов"""
    print("\n" + "="*60)
    print("  ТЕСТИРОВАНИЕ ML КОМПОНЕНТОВ")
    print("  Invest MRSU Backend")
    print("="*60)
    
    tests = [
        ("Препроцессор", test_preprocessor),
        ("LSTM Модель", test_lstm_model),
        ("MOEX Collector", test_data_collector),
        ("CSV Importer", test_csv_importer),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ ОШИБКА в тесте '{name}': {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Итоги
    print("\n" + "="*60)
    print("ИТОГИ")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {name}")
    
    print(f"\nВсего: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 Все тесты успешно пройдены!")
    else:
        print(f"\n⚠️  {total - passed} тест(ов) провалено")


if __name__ == "__main__":
    main()
