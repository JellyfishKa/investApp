class PricePoint {
  final DateTime date;
  final double price;
  final double open;
  final double high;
  final double low;
  final double close;
  final int volume;

  PricePoint({
    required this.date,
    required this.price,
    required this.open,
    required this.high,
    required this.low,
    required this.close,
    required this.volume,
  });
}

class PriceHistory {
  final String ticker;
  final List<PricePoint> points;

  PriceHistory({
    required this.ticker,
    required this.points,
  });

  // Получить точки за последние N дней
  List<PricePoint> getLastNDays(int days) {
    if (points.length <= days) return points;
    return points.sublist(points.length - days);
  }

  // Получить точки за период
  List<PricePoint> getRange(DateTime start, DateTime end) {
    return points.where((p) =>
      p.date.isAfter(start) && p.date.isBefore(end)
    ).toList();
  }
}
