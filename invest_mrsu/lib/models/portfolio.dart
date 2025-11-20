class Holding {
  final String ticker;
  final int quantity;
  final double averagePrice;
  final double currentPrice;

  Holding({
    required this.ticker,
    required this.quantity,
    required this.averagePrice,
    required this.currentPrice,
  });

  // Расчет текущей стоимости
  double get currentValue => quantity * currentPrice;

  // Расчет стоимости покупки
  double get costBasis => quantity * averagePrice;

  // Прибыль/убыток в рублях
  double get profitLoss => currentValue - costBasis;

  // Прибыль/убыток в процентах
  double get profitLossPercent => ((currentPrice - averagePrice) / averagePrice) * 100;

  Holding copyWith({
    String? ticker,
    int? quantity,
    double? averagePrice,
    double? currentPrice,
  }) {
    return Holding(
      ticker: ticker ?? this.ticker,
      quantity: quantity ?? this.quantity,
      averagePrice: averagePrice ?? this.averagePrice,
      currentPrice: currentPrice ?? this.currentPrice,
    );
  }
}

class Portfolio {
  final double balance;
  final List<Holding> holdings;

  Portfolio({
    required this.balance,
    required this.holdings,
  });

  // Общая стоимость портфеля
  double get totalValue {
    double holdingsValue = holdings.fold(0, (sum, h) => sum + h.currentValue);
    return balance + holdingsValue;
  }

  // Стоимость всех акций
  double get holdingsValue {
    return holdings.fold(0, (sum, h) => sum + h.currentValue);
  }

  // Общая прибыль/убыток
  double get totalProfitLoss {
    return holdings.fold(0, (sum, h) => sum + h.profitLoss);
  }

  Portfolio copyWith({
    double? balance,
    List<Holding>? holdings,
  }) {
    return Portfolio(
      balance: balance ?? this.balance,
      holdings: holdings ?? this.holdings,
    );
  }
}
