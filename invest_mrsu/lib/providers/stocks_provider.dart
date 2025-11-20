import 'package:flutter/foundation.dart';
import '../models/stock.dart';
import '../models/prediction.dart';
import '../models/price_history.dart';
import '../models/dividend.dart';
import '../data/mock_data.dart';

class StocksProvider with ChangeNotifier {
  List<Stock> _stocks = [];
  final Map<String, PriceHistory> _priceHistories = {};
  final Map<String, PredictionSet> _predictions = {};
  final Set<String> _viewedPredictions = {}; // для отслеживания просмотренных прогнозов

  StocksProvider() {
    _loadStocks();
  }

  List<Stock> get stocks => _stocks;
  Set<String> get viewedPredictions => _viewedPredictions;

  void _loadStocks() {
    _stocks = MockData.stocks;
    notifyListeners();
  }

  // Получить акцию по тикеру
  Stock? getStock(String ticker) {
    try {
      return _stocks.firstWhere((s) => s.ticker == ticker);
    } catch (e) {
      return null;
    }
  }

  // Получить исторические данные
  PriceHistory getPriceHistory(String ticker) {
    if (!_priceHistories.containsKey(ticker)) {
      _priceHistories[ticker] = MockData.generatePriceHistory(ticker);
    }
    return _priceHistories[ticker]!;
  }

  // Получить прогнозы
  PredictionSet getPredictions(String ticker) {
    if (!_predictions.containsKey(ticker)) {
      final stock = getStock(ticker);
      if (stock != null) {
        _predictions[ticker] = MockData.getPredictions(ticker, stock.currentPrice);
      }
    }
    return _predictions[ticker]!;
  }

  // Отметить просмотр прогноза
  void markPredictionViewed(String ticker) {
    _viewedPredictions.add(ticker);
    notifyListeners();
  }

  // Получить дивиденды
  List<Dividend> getDividends(String ticker, int quantity) {
    return MockData.getDividends(ticker, quantity);
  }

  // Получить прогноз дивидендов
  List<DividendPrediction> getDividendPredictions(String ticker) {
    return MockData.getDividendPredictions(ticker);
  }

  // Получить только акции Газпрома (головная + дочерние)
  List<Stock> get gazpromStocks => _stocks;

  // Получить головную компанию
  Stock? get parentStock => _stocks.firstWhere(
    (s) => s.isParent,
    orElse: () => _stocks.first,
  );
}
