class Dividend {
  final String ticker;
  final DateTime paymentDate;
  final double amountPerShare;
  final double totalAmount; // для портфеля
  final String status; // 'paid', 'upcoming', 'predicted'

  Dividend({
    required this.ticker,
    required this.paymentDate,
    required this.amountPerShare,
    required this.totalAmount,
    required this.status,
  });

  // Расчет общей суммы дивидендов для количества акций
  static double calculateTotal(double amountPerShare, int quantity) {
    return amountPerShare * quantity;
  }
}

class DividendPrediction {
  final String ticker;
  final DateTime predictedDate;
  final double predictedAmountPerShare;
  final double probability; // вероятность выплаты (0-1)
  final String frequency; // 'quarterly', 'annual', 'semi-annual'

  DividendPrediction({
    required this.ticker,
    required this.predictedDate,
    required this.predictedAmountPerShare,
    required this.probability,
    required this.frequency,
  });
}
