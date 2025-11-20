class Prediction {
  final String ticker;
  final DateTime targetDate;
  final double predictedPrice;
  final double confidenceLow; // нижняя граница доверительного интервала
  final double confidenceHigh; // верхняя граница
  final double changePercent;
  final String period; // 'week', 'month', 'year'

  Prediction({
    required this.ticker,
    required this.targetDate,
    required this.predictedPrice,
    required this.confidenceLow,
    required this.confidenceHigh,
    required this.changePercent,
    required this.period,
  });

  // Расчет потенциальной прибыли
  double calculatePotentialProfit(double currentPrice, int quantity) {
    return (predictedPrice - currentPrice) * quantity;
  }

  // Расчет процента изменения
  static double calculateChangePercent(double current, double predicted) {
    return ((predicted - current) / current) * 100;
  }
}

class PredictionSet {
  final String ticker;
  final Prediction? weekPrediction;
  final Prediction? monthPrediction;
  final Prediction? yearPrediction;

  PredictionSet({
    required this.ticker,
    this.weekPrediction,
    this.monthPrediction,
    this.yearPrediction,
  });
}
