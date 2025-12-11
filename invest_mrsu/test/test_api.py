"""
Тестовый скрипт для проверки API
Запуск: python test_api.py
"""
import requests
import json
from datetime import datetime


API_URL = "http://localhost:8000"


def test_health():
    """Проверка health endpoint"""
    print("\n" + "="*60)
    print("ТЕСТ 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✓ API доступен")
            print(f"  Сервис: {data.get('service')}")
            print(f"  Версия: {data.get('version')}")
            print(f"  Статус: {data.get('status')}")
            return True
        else:
            print(f"✗ Ошибка: status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ API недоступен (не запущен)")
        print("  Запустите: cd backend && python main.py")
        return False
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_predict():
    """Проверка predict endpoint"""
    print("\n" + "="*60)
    print("ТЕСТ 2: Predict Endpoint")
    print("="*60)
    
    try:
        payload = {
            "ticker": "GAZP",
            "period": "month"
        }
        
        print(f"Запрос: POST /predict")
        print(f"Данные: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✓ Прогноз получен")
            print(f"  Тикер: {data['ticker']}")
            print(f"  Текущая цена: {data['current_price']:.2f}₽")
            print(f"  Прогноз: {data['predicted_price']:.2f}₽")
            print(f"  Изменение: {data['change_percent']:+.2f}%")
            print(f"  Доверительный интервал: [{data['confidence_low']:.2f}, {data['confidence_high']:.2f}]")
            
            if data.get('model_accuracy'):
                print(f"  Точность модели: {data['model_accuracy']:.1f}%")
            
            return True
        elif response.status_code == 404:
            print("✗ Модель не найдена")
            print("  Необходимо обучить модель: cd backend && python ml/trainer.py")
            return False
        else:
            print(f"✗ Ошибка: status code {response.status_code}")
            print(f"  Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_history():
    """Проверка history endpoint"""
    print("\n" + "="*60)
    print("ТЕСТ 3: History Endpoint")
    print("="*60)
    
    try:
        ticker = "GAZP"
        days = 30
        
        print(f"Запрос: GET /history/{ticker}?days={days}")
        
        response = requests.get(
            f"{API_URL}/history/{ticker}",
            params={"days": days},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ История получена")
            print(f"  Тикер: {data['ticker']}")
            print(f"  Записей: {len(data['data'])}")
            
            if data['data']:
                first = data['data'][0]
                last = data['data'][-1]
                print(f"  Период: {first['date']} - {last['date']}")
                print(f"  Последняя цена: {last['close']:.2f}₽")
            
            return True
        elif response.status_code == 404:
            print("✗ Данные не найдены")
            print("  Необходимо загрузить данные: POST /admin/update_moex")
            return False
        else:
            print(f"✗ Ошибка: status code {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ Ошибка: {e}")
        return False


def test_batch_predictions():
    """Тест предсказаний для всех тикеров"""
    print("\n" + "="*60)
    print("ТЕСТ 4: Batch Predictions (все тикеры)")
    print("="*60)
    
    tickers = ['GAZP', 'SIBN', 'GCHE']
    period = 'week'
    
    results = []
    
    for ticker in tickers:
        try:
            response = requests.post(
                f"{API_URL}/predict",
                json={"ticker": ticker, "period": period},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                results.append((ticker, data['predicted_price'], data['change_percent']))
                print(f"✓ {ticker}: {data['predicted_price']:.2f}₽ ({data['change_percent']:+.2f}%)")
            else:
                print(f"✗ {ticker}: Ошибка {response.status_code}")
                results.append((ticker, None, None))
                
        except Exception as e:
            print(f"✗ {ticker}: {e}")
            results.append((ticker, None, None))
    
    successful = sum(1 for _, price, _ in results if price is not None)
    print(f"\n{successful}/{len(tickers)} прогнозов получено")
    
    return successful > 0


def main():
    """Запуск всех тестов API"""
    print("\n" + "="*60)
    print("  ТЕСТИРОВАНИЕ API")
    print("  Invest MRSU Backend")
    print("="*60)
    print(f"\nAPI URL: {API_URL}")
    print("Убедитесь, что backend запущен!")
    
    tests = [
        ("Health Check", test_health),
        ("Predict", test_predict),
        ("History", test_history),
        ("Batch Predictions", test_batch_predictions),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ ОШИБКА в тесте '{name}': {e}")
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
