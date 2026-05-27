import 'package:flutter/material.dart';
import 'stock.dart';

/// Модель одной метрики для сравнения
class ComparisonMetric {
  final String label;
  final double value;
  final String unit;
  final double? benchmark; // значение конкурента для сравнения
  final bool isPositiveBetter; // true если больше значение = лучше инвестиция

  ComparisonMetric({
    required this.label,
    required this.value,
    required this.unit,
    this.benchmark,
    this.isPositiveBetter = true,
  });

  /// Лучше ли текущее значение бенчмарка
  bool get isBetter {
    if (benchmark == null) return false;
    if (isPositiveBetter) {
      return value > benchmark!;
    } else {
      return value < benchmark!;
    }
  }

  /// Разница от бенчмарка в процентах
  double get differencePercent {
    if (benchmark == null || benchmark == 0) return 0;
    return ((value - benchmark!) / benchmark!) * 100;
  }
}

/// Полное сравнение нескольких акций
class StockComparison {
  final List<Stock> stocks;
  final Map<String, List<ComparisonMetric>> metrics; // ticker -> список метрик

  StockComparison({
    required this.stocks,
    required this.metrics,
  });

  /// Получить метрики для конкретной акции
  List<ComparisonMetric> getMetricsForStock(String ticker) {
    return metrics[ticker] ?? [];
  }

  /// Получить все категории метрик
  List<String> get metricCategories {
    if (stocks.isEmpty) return [];
    final firstTicker = stocks.first.ticker;
    return metrics[firstTicker]?.map((m) => m.label).toList() ?? [];
  }
}

/// Рейтинг акции для сравнительного анализа
class ComparisonRating {
  final String ticker;
  final String name;
  final double overall; // от 0 до 100
  final Map<String, double> categoryScores; // категория -> оценка

  ComparisonRating({
    required this.ticker,
    required this.name,
    required this.overall,
    required this.categoryScores,
  });

  /// Получить цвет рейтинга
  Color getRatingColor() {
    if (overall >= 75) return const Color(0xFF4CAF50); // зелёный - отличная покупка
    if (overall >= 50) return const Color(0xFFFFC107); // жёлтый - нейтральная
    return const Color(0xFFF44336); // красный - плохая покупка
  }

  /// Текстовая оценка
  String getRatingText() {
    if (overall >= 75) return 'Отличная покупка';
    if (overall >= 50) return 'Нейтральна';
    return 'Не рекомендуется';
  }
}
