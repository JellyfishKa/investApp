import 'package:flutter/foundation.dart';
import '../models/portfolio.dart';
import '../models/transaction.dart';
import '../models/stock.dart';

class PortfolioProvider with ChangeNotifier {
  Portfolio _portfolio = Portfolio(
    balance: 100000.0, // начальный виртуальный баланс
    holdings: [],
  );

  final List<Transaction> _transactions = [];

  Portfolio get portfolio => _portfolio;
  List<Transaction> get transactions => List.unmodifiable(_transactions);

  // Покупка акций
  bool buyStock(Stock stock, int quantity) {
    final totalCost = stock.currentPrice * quantity;

    if (_portfolio.balance < totalCost) {
      return false; // недостаточно средств
    }

    // Обновляем баланс
    _portfolio = _portfolio.copyWith(
      balance: _portfolio.balance - totalCost,
    );

    // Обновляем holdings
    final existingHoldingIndex = _portfolio.holdings.indexWhere(
      (h) => h.ticker == stock.ticker,
    );

    List<Holding> updatedHoldings = List.from(_portfolio.holdings);

    if (existingHoldingIndex >= 0) {
      // Уже есть такие акции - обновляем среднюю цену
      final existingHolding = _portfolio.holdings[existingHoldingIndex];
      final totalQuantity = existingHolding.quantity + quantity;
      final newAveragePrice =
        ((existingHolding.averagePrice * existingHolding.quantity) +
         (stock.currentPrice * quantity)) / totalQuantity;

      updatedHoldings[existingHoldingIndex] = existingHolding.copyWith(
        quantity: totalQuantity,
        averagePrice: newAveragePrice,
        currentPrice: stock.currentPrice,
      );
    } else {
      // Новые акции
      updatedHoldings.add(Holding(
        ticker: stock.ticker,
        quantity: quantity,
        averagePrice: stock.currentPrice,
        currentPrice: stock.currentPrice,
      ));
    }

    _portfolio = _portfolio.copyWith(holdings: updatedHoldings);

    // Добавляем транзакцию
    _transactions.insert(0, Transaction(
      id: Transaction.generateId(),
      ticker: stock.ticker,
      type: TransactionType.buy,
      quantity: quantity,
      price: stock.currentPrice,
      timestamp: DateTime.now(),
      total: totalCost,
    ));

    notifyListeners();
    return true;
  }

  // Продажа акций
  bool sellStock(Stock stock, int quantity) {
    final holdingIndex = _portfolio.holdings.indexWhere(
      (h) => h.ticker == stock.ticker,
    );

    if (holdingIndex < 0) {
      return false; // нет таких акций
    }

    final holding = _portfolio.holdings[holdingIndex];
    if (holding.quantity < quantity) {
      return false; // недостаточно акций
    }

    final totalRevenue = stock.currentPrice * quantity;

    // Обновляем баланс
    _portfolio = _portfolio.copyWith(
      balance: _portfolio.balance + totalRevenue,
    );

    // Обновляем holdings
    List<Holding> updatedHoldings = List.from(_portfolio.holdings);

    if (holding.quantity == quantity) {
      // Продаем все акции - удаляем из holdings
      updatedHoldings.removeAt(holdingIndex);
    } else {
      // Продаем часть
      updatedHoldings[holdingIndex] = holding.copyWith(
        quantity: holding.quantity - quantity,
        currentPrice: stock.currentPrice,
      );
    }

    _portfolio = _portfolio.copyWith(holdings: updatedHoldings);

    // Добавляем транзакцию
    _transactions.insert(0, Transaction(
      id: Transaction.generateId(),
      ticker: stock.ticker,
      type: TransactionType.sell,
      quantity: quantity,
      price: stock.currentPrice,
      timestamp: DateTime.now(),
      total: totalRevenue,
    ));

    notifyListeners();
    return true;
  }

  // Обновить текущие цены акций в портфеле
  void updatePrices(List<Stock> stocks) {
    List<Holding> updatedHoldings = _portfolio.holdings.map((holding) {
      final stock = stocks.firstWhere(
        (s) => s.ticker == holding.ticker,
        orElse: () => stocks.first,
      );
      return holding.copyWith(currentPrice: stock.currentPrice);
    }).toList();

    _portfolio = _portfolio.copyWith(holdings: updatedHoldings);
    notifyListeners();
  }

  // Получить holding по тикеру
  Holding? getHolding(String ticker) {
    try {
      return _portfolio.holdings.firstWhere((h) => h.ticker == ticker);
    } catch (e) {
      return null;
    }
  }

  // Добавить бонусные средства (награды за задания)
  void addBonus(double amount) {
    _portfolio = _portfolio.copyWith(
      balance: _portfolio.balance + amount,
    );
    notifyListeners();
  }
}
