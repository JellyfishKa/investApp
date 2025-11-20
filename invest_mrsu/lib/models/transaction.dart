class Transaction {
  final String id;
  final String ticker;
  final TransactionType type;
  final int quantity;
  final double price;
  final DateTime timestamp;
  final double total;

  Transaction({
    required this.id,
    required this.ticker,
    required this.type,
    required this.quantity,
    required this.price,
    required this.timestamp,
    required this.total,
  });

  static String generateId() {
    return DateTime.now().millisecondsSinceEpoch.toString();
  }
}

enum TransactionType {
  buy,
  sell,
}

extension TransactionTypeExtension on TransactionType {
  String get displayName {
    switch (this) {
      case TransactionType.buy:
        return 'Покупка';
      case TransactionType.sell:
        return 'Продажа';
    }
  }

  String get displaySymbol {
    switch (this) {
      case TransactionType.buy:
        return '+';
      case TransactionType.sell:
        return '-';
    }
  }
}
