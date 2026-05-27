import 'package:flutter/foundation.dart';
import '../models/stock.dart';
import '../models/comparison.dart';

/// Provider для сравнения акций между собой
class ComparisonProvider with ChangeNotifier {
  List<Stock> _selectedStocks = [];
  Map<String, List<ComparisonMetric>> _metrics = {};
  Map<String, ComparisonRating> _ratings = {};

  List<Stock> get selectedStocks => _selectedStocks;
  Map<String, List<ComparisonMetric>> get metrics => _metrics;
  Map<String, ComparisonRating> get ratings => _ratings;

  bool get hasComparison => _selectedStocks.length >= 2;

  /// Добавить акцию в сравнение (макс 4 акции)
  void addStockToComparison(Stock stock) {
    if (_selectedStocks.length >= 4) return;
    if (_selectedStocks.any((s) => s.ticker == stock.ticker)) return;

    _selectedStocks.add(stock);
    _recalculateMetrics();
    notifyListeners();
  }

  /// Удалить акцию из сравнения
  void removeStockFromComparison(String ticker) {
    _selectedStocks.removeWhere((s) => s.ticker == ticker);
    _recalculateMetrics();
    notifyListeners();
  }

  /// Очистить всё сравнение
  void clearComparison() {
    _selectedStocks.clear();
    _metrics.clear();
    _ratings.clear();
    notifyListeners();
  }

  /// Пересчитать метрики для выбранных акций
  void _recalculateMetrics() {
    _metrics.clear();
    _ratings.clear();

    if (_selectedStocks.isEmpty) return;

    // Вычисляем метрики для каждой акции
    for (final stock in _selectedStocks) {
      final stockMetrics = _generateMetricsForStock(stock);
      _metrics[stock.ticker] = stockMetrics;

      // Вычисляем рейтинг
      final rating = _generateRatingForStock(stock, stockMetrics);
      _ratings[stock.ticker] = rating;
    }
  }

  /// Генерировать метрики для акции
  List<ComparisonMetric> _generateMetricsForStock(Stock stock) {
    final metrics = <ComparisonMetric>[];

    // 1. Цена (текущая)
    metrics.add(ComparisonMetric(
      label: 'Текущая цена',
      value: stock.currentPrice,
      unit: '₽',
      isPositiveBetter: false, // ниже цена = лучше для покупки
    ));

    // 2. Изменение за день
    metrics.add(ComparisonMetric(
      label: 'Изменение за день',
      value: stock.changePercent,
      unit: '%',
      isPositiveBetter: true,
    ));

    // 3. Объём торгов
    metrics.add(ComparisonMetric(
      label: 'Объём торгов',
      value: stock.volume.toDouble(),
      unit: 'шт.',
      isPositiveBetter: true, // больше объём = лучше ликвидность
    ));

    // 4. Волатильность (синтетическая на основе изменения)
    final volatility = (stock.changePercent.abs() * 10); // упрощённая формула
    metrics.add(ComparisonMetric(
      label: 'Волатильность',
      value: volatility,
      unit: '%',
      isPositiveBetter: false, // ниже волатильность = менее рискованная
    ));

    // 5. Пример: P/E ratio (моки данные)
    final peRatio = _getPERatio(stock.ticker);
    metrics.add(ComparisonMetric(
      label: 'P/E Ratio',
      value: peRatio,
      unit: 'x',
      isPositiveBetter: false, // ниже P/E = дешевле
    ));

    return metrics;
  }

  /// Генерировать рейтинг для акции
  ComparisonRating _generateRatingForStock(Stock stock, List<ComparisonMetric> metrics) {
    final scores = <String, double>{};
    var overallScore = 0.0;

    // Оцениваем каждый критерий
    for (final metric in metrics) {
      double score = 50; // базовая оценка

      // Логика оценки в зависимости от метрики
      switch (metric.label) {
        case 'Текущая цена':
          // Дешевле = лучше (но не слишком дешево)
          if (metric.value < 100) score = 80;
          else if (metric.value < 200) score = 70;
          else if (metric.value < 500) score = 60;
          else score = 40;
          break;

        case 'Изменение за день':
          // Положительное изменение = хорошо
          if (metric.value > 2) score = 75;
          else if (metric.value > 0) score = 65;
          else if (metric.value > -2) score = 50;
          else score = 30;
          break;

        case 'Объём торгов':
          // Больше объём = лучше
          if (metric.value > 10000000) score = 85;
          else if (metric.value > 1000000) score = 75;
          else if (metric.value > 100000) score = 60;
          else score = 40;
          break;

        case 'Волатильность':
          // Меньше волатильность = более стабильна
          if (metric.value < 2) score = 85;
          else if (metric.value < 5) score = 75;
          else if (metric.value < 10) score = 55;
          else score = 30;
          break;

        case 'P/E Ratio':
          // P/E 10-20 = нормально
          if (metric.value >= 10 && metric.value <= 20) score = 80;
          else if (metric.value > 5) score = 70;
          else score = 50;
          break;
      }

      scores[metric.label] = score;
      overallScore += score;
    }

    overallScore = overallScore / metrics.length; // средняя оценка

    return ComparisonRating(
      ticker: stock.ticker,
      name: stock.name,
      overall: overallScore,
      categoryScores: scores,
    );
  }

  /// Получить P/E ratio для акции (моки данные)
  double _getPERatio(String ticker) {
    const peRatios = {
      'GAZP': 4.5,
      'GAZP-p': 3.8,
      'SIBN': 8.2,
      'GCHE': 6.1,
      'MRKZ': 15.3,
    };
    return peRatios[ticker] ?? 10.0;
  }

  /// Получить лучшую акцию по конкретному критерию
  Stock? getBestStockByCriteria(String criteria) {
    if (_selectedStocks.isEmpty) return null;

    Stock? best;
    double? bestValue;

    for (final stock in _selectedStocks) {
      final metrics = _metrics[stock.ticker] ?? [];
      final metric = metrics.firstWhere(
        (m) => m.label == criteria,
        orElse: () => ComparisonMetric(label: '', value: 0, unit: ''),
      );

      if (metric.label.isNotEmpty) {
        final value = metric.isBetter ? metric.value : -metric.value;
        if (bestValue == null || value > bestValue) {
          bestValue = value;
          best = stock;
        }
      }
    }

    return best;
  }
}
