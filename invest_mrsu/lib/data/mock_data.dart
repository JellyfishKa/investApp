import '../models/stock.dart';
import '../models/dividend.dart';
import '../models/prediction.dart';
import '../models/price_history.dart';
import '../models/task.dart';

class MockData {
  // Газпром и дочерние компании
  static final List<Stock> stocks = [
    Stock(
      ticker: 'GAZP',
      name: 'Газпром',
      company: 'ПАО "Газпром"',
      currentPrice: 173.50,
      previousClose: 171.20,
      change: 2.30,
      changePercent: 1.34,
      volume: 18500000,
      logo: '🏭',
      isParent: true,
    ),
    Stock(
      ticker: 'GAZP-p',
      name: 'Газпром (прив.)',
      company: 'ПАО "Газпром" (привилегированные)',
      currentPrice: 145.80,
      previousClose: 147.30,
      change: -1.50,
      changePercent: -1.02,
      volume: 3200000,
      logo: '🏭',
      isParent: false,
    ),
    Stock(
      ticker: 'SIBN',
      name: 'Газпром нефть',
      company: 'ПАО "Газпром нефть"',
      currentPrice: 548.20,
      previousClose: 542.10,
      change: 6.10,
      changePercent: 1.13,
      volume: 1850000,
      logo: '⛽',
      isParent: false,
    ),
    Stock(
      ticker: 'GCHE',
      name: 'Газпром-нефтехим Салават',
      company: 'ОАО "Газпром-нефтехим Салават"',
      currentPrice: 42.15,
      previousClose: 41.80,
      change: 0.35,
      changePercent: 0.84,
      volume: 125000,
      logo: '⚗️',
      isParent: false,
    ),
    Stock(
      ticker: 'MRKZ',
      name: 'Россети Урал',
      company: 'ПАО "Россети Урал" (партнер Газпрома)',
      currentPrice: 0.0285,
      previousClose: 0.0280,
      change: 0.0005,
      changePercent: 1.79,
      volume: 25000000,
      logo: '⚡',
      isParent: false,
    ),
  ];

  // Исторические данные (последние 365 дней для Газпрома)
  static PriceHistory generatePriceHistory(String ticker) {
    final now = DateTime.now();
    final points = <PricePoint>[];

    // Базовая цена зависит от тикера
    double basePrice;
    switch (ticker) {
      case 'GAZP':
        basePrice = 170.0;
        break;
      case 'GAZP-p':
        basePrice = 145.0;
        break;
      case 'SIBN':
        basePrice = 540.0;
        break;
      case 'GCHE':
        basePrice = 41.0;
        break;
      case 'MRKZ':
        basePrice = 0.028;
        break;
      default:
        basePrice = 100.0;
    }

    // Генерируем данные за последний год
    for (int i = 365; i >= 0; i--) {
      final date = now.subtract(Duration(days: i));

      // Создаем волатильность (синусоида + рандом)
      final trend = basePrice + (basePrice * 0.1 * (i / 365)); // общий тренд
      final seasonality = basePrice * 0.05 * (i % 30) / 30; // месячная волатильность
      final noise = (i % 7 - 3) * basePrice * 0.01; // шум

      final close = trend + seasonality + noise;
      final open = close + (i % 5 - 2) * basePrice * 0.005;
      final high = close + (basePrice * 0.01);
      final low = close - (basePrice * 0.01);

      points.add(PricePoint(
        date: date,
        price: close,
        open: open,
        high: high,
        low: low,
        close: close,
        volume: (basePrice * 100000).toInt() + (i % 10 * 10000),
      ));
    }

    return PriceHistory(ticker: ticker, points: points);
  }

  // Прогнозы для акций
  static PredictionSet getPredictions(String ticker, double currentPrice) {
    final now = DateTime.now();

    // Оптимистичные прогнозы для демонстрации
    return PredictionSet(
      ticker: ticker,
      weekPrediction: Prediction(
        ticker: ticker,
        targetDate: now.add(const Duration(days: 7)),
        predictedPrice: currentPrice * 1.02, // +2%
        confidenceLow: currentPrice * 0.99,
        confidenceHigh: currentPrice * 1.04,
        changePercent: 2.0,
        period: 'week',
      ),
      monthPrediction: Prediction(
        ticker: ticker,
        targetDate: now.add(const Duration(days: 30)),
        predictedPrice: currentPrice * 1.08, // +8%
        confidenceLow: currentPrice * 1.03,
        confidenceHigh: currentPrice * 1.12,
        changePercent: 8.0,
        period: 'month',
      ),
      yearPrediction: Prediction(
        ticker: ticker,
        targetDate: now.add(const Duration(days: 365)),
        predictedPrice: currentPrice * 1.25, // +25%
        confidenceLow: currentPrice * 1.15,
        confidenceHigh: currentPrice * 1.40,
        changePercent: 25.0,
        period: 'year',
      ),
    );
  }

  // Дивиденды (исторические и прогнозируемые)
  static List<Dividend> getDividends(String ticker, int quantity) {
    // Газпром платит дивиденды 2 раза в год
    if (ticker == 'GAZP') {
      return [
        Dividend(
          ticker: ticker,
          paymentDate: DateTime(2024, 7, 15),
          amountPerShare: 12.55,
          totalAmount: 12.55 * quantity,
          status: 'paid',
        ),
        Dividend(
          ticker: ticker,
          paymentDate: DateTime(2025, 1, 20),
          amountPerShare: 14.20,
          totalAmount: 14.20 * quantity,
          status: 'upcoming',
        ),
        Dividend(
          ticker: ticker,
          paymentDate: DateTime(2025, 7, 15),
          amountPerShare: 15.00,
          totalAmount: 15.00 * quantity,
          status: 'predicted',
        ),
      ];
    }

    // Газпром нефть
    if (ticker == 'SIBN') {
      return [
        Dividend(
          ticker: ticker,
          paymentDate: DateTime(2024, 6, 10),
          amountPerShare: 38.74,
          totalAmount: 38.74 * quantity,
          status: 'paid',
        ),
        Dividend(
          ticker: ticker,
          paymentDate: DateTime(2025, 6, 10),
          amountPerShare: 42.50,
          totalAmount: 42.50 * quantity,
          status: 'predicted',
        ),
      ];
    }

    return [];
  }

  // Прогноз дивидендов
  static List<DividendPrediction> getDividendPredictions(String ticker) {
    if (ticker == 'GAZP') {
      return [
        DividendPrediction(
          ticker: ticker,
          predictedDate: DateTime(2025, 7, 15),
          predictedAmountPerShare: 15.00,
          probability: 0.85,
          frequency: 'semi-annual',
        ),
        DividendPrediction(
          ticker: ticker,
          predictedDate: DateTime(2026, 1, 15),
          predictedAmountPerShare: 16.50,
          probability: 0.75,
          frequency: 'semi-annual',
        ),
      ];
    }

    if (ticker == 'SIBN') {
      return [
        DividendPrediction(
          ticker: ticker,
          predictedDate: DateTime(2025, 6, 10),
          predictedAmountPerShare: 42.50,
          probability: 0.80,
          frequency: 'annual',
        ),
      ];
    }

    return [];
  }

  // Игровые задания
  static List<GameTask> getInitialTasks() {
    return [
      GameTask(
        id: 'welcome',
        title: 'Добро пожаловать!',
        description: 'Зарегистрируйтесь в приложении',
        reward: 100,
        status: TaskStatus.completed,
        type: TaskType.welcome,
        progress: 1,
        target: 1,
      ),
      GameTask(
        id: 'first_buy',
        title: 'Первые шаги инвестора',
        description: 'Совершите первую покупку акций',
        reward: 500,
        status: TaskStatus.active,
        type: TaskType.firstBuy,
        progress: 0,
        target: 1,
      ),
      GameTask(
        id: 'view_predictions',
        title: 'Аналитик',
        description: 'Изучите прогноз по 3 разным компаниям',
        reward: 300,
        status: TaskStatus.active,
        type: TaskType.viewPredictions,
        progress: 0,
        target: 3,
      ),
      GameTask(
        id: 'hold_7days',
        title: 'Долгосрочный инвестор',
        description: 'Держите акции 7 дней подряд',
        reward: 1000,
        status: TaskStatus.active,
        type: TaskType.holdDays,
        progress: 0,
        target: 7,
      ),
      GameTask(
        id: 'daily_login',
        title: 'Постоянный пользователь',
        description: 'Заходите в приложение ежедневно',
        reward: 200,
        status: TaskStatus.active,
        type: TaskType.dailyLogin,
        progress: 1,
        target: 1,
      ),
    ];
  }
}
