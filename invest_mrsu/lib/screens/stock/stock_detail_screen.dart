import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/stocks_provider.dart';
import '../../providers/portfolio_provider.dart';
import '../../providers/tasks_provider.dart';
import '../../models/stock.dart';
import '../../models/task.dart';
import '../widgets/price_chart.dart';
import '../widgets/buy_sell_dialog.dart';

class StockDetailScreen extends StatefulWidget {
  final String ticker;

  const StockDetailScreen({super.key, required this.ticker});

  @override
  State<StockDetailScreen> createState() => _StockDetailScreenState();
}

class _StockDetailScreenState extends State<StockDetailScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    // Отметить просмотр прогноза
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final stocksProvider = Provider.of<StocksProvider>(context, listen: false);
      final tasksProvider = Provider.of<TasksProvider>(context, listen: false);

      if (!stocksProvider.viewedPredictions.contains(widget.ticker)) {
        stocksProvider.markPredictionViewed(widget.ticker);
        tasksProvider.updateTaskProgress(TaskType.viewPredictions);
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2);

    return Consumer3<StocksProvider, PortfolioProvider, TasksProvider>(
      builder: (context, stocksProvider, portfolioProvider, tasksProvider, _) {
        final stock = stocksProvider.getStock(widget.ticker);
        if (stock == null) {
          return Scaffold(
            appBar: AppBar(),
            body: const Center(child: Text('Акция не найдена')),
          );
        }

        final holding = portfolioProvider.getHolding(widget.ticker);
        final priceHistory = stocksProvider.getPriceHistory(widget.ticker);
        final predictions = stocksProvider.getPredictions(widget.ticker);
        final dividends = stocksProvider.getDividends(widget.ticker, holding?.quantity ?? 1);

        return Scaffold(
          appBar: AppBar(
            title: Text(stock.name),
            actions: [
              IconButton(
                icon: const Icon(Icons.info_outline),
                onPressed: () {
                  _showInfoDialog(context, stock);
                },
              ),
            ],
          ),
          body: Column(
            children: [
              // Цена и изменение
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                color: Theme.of(context).colorScheme.primaryContainer.withValues(alpha: 0.3),
                child: Column(
                  children: [
                    Text(
                      stock.logo,
                      style: const TextStyle(fontSize: 48),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      currencyFormat.format(stock.currentPrice),
                      style: const TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(
                          stock.change >= 0 ? Icons.arrow_upward : Icons.arrow_downward,
                          color: stock.change >= 0 ? Colors.green : Colors.red,
                          size: 20,
                        ),
                        Text(
                          '${stock.change >= 0 ? '+' : ''}${currencyFormat.format(stock.change)} (${stock.changePercent.toStringAsFixed(2)}%)',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: stock.change >= 0 ? Colors.green : Colors.red,
                          ),
                        ),
                      ],
                    ),
                    if (holding != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.blue[50],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'У вас: ${holding.quantity} шт. (${currencyFormat.format(holding.currentValue)})',
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              // Вкладки
              TabBar(
                controller: _tabController,
                tabs: const [
                  Tab(text: 'График'),
                  Tab(text: 'Прогнозы'),
                  Tab(text: 'Дивиденды'),
                ],
              ),

              // Содержимое вкладок
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    // График
                    PriceChartTab(priceHistory: priceHistory),

                    // Прогнозы
                    PredictionsTab(
                      stock: stock,
                      predictions: predictions,
                      holding: holding,
                      currencyFormat: currencyFormat,
                    ),

                    // Дивиденды
                    DividendsTab(
                      ticker: widget.ticker,
                      dividends: dividends,
                      holding: holding,
                      currencyFormat: currencyFormat,
                    ),
                  ],
                ),
              ),
            ],
          ),
          bottomNavigationBar: SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _showBuyDialog(context, stock),
                      icon: const Icon(Icons.add_shopping_cart),
                      label: const Text('Купить'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),
                  if (holding != null) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () => _showSellDialog(context, stock, holding.quantity),
                        icon: const Icon(Icons.sell),
                        label: const Text('Продать'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.red,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  void _showBuyDialog(BuildContext context, Stock stock) {
    showDialog(
      context: context,
      builder: (context) => BuySellDialog(
        stock: stock,
        isBuy: true,
      ),
    );
  }

  void _showSellDialog(BuildContext context, Stock stock, int maxQuantity) {
    showDialog(
      context: context,
      builder: (context) => BuySellDialog(
        stock: stock,
        isBuy: false,
        maxQuantity: maxQuantity,
      ),
    );
  }

  void _showInfoDialog(BuildContext context, Stock stock) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(stock.name),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Тикер: ${stock.ticker}'),
            Text('Компания: ${stock.company}'),
            Text('Объем торгов: ${NumberFormat('#,###').format(stock.volume)}'),
            if (stock.isParent)
              const Text(
                '\nГоловная компания холдинга',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Закрыть'),
          ),
        ],
      ),
    );
  }
}

// Вкладка с графиком (создадим позже)
class PriceChartTab extends StatelessWidget {
  final dynamic priceHistory;

  const PriceChartTab({super.key, required this.priceHistory});

  @override
  Widget build(BuildContext context) {
    return PriceChart(priceHistory: priceHistory);
  }
}

// Вкладка с прогнозами
class PredictionsTab extends StatelessWidget {
  final Stock stock;
  final dynamic predictions;
  final dynamic holding;
  final NumberFormat currencyFormat;

  const PredictionsTab({
    super.key,
    required this.stock,
    required this.predictions,
    required this.holding,
    required this.currencyFormat,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (predictions.weekPrediction != null)
          _PredictionCard(
            title: 'Прогноз на неделю',
            prediction: predictions.weekPrediction,
            currentPrice: stock.currentPrice,
            holding: holding,
            currencyFormat: currencyFormat,
          ),
        if (predictions.monthPrediction != null)
          _PredictionCard(
            title: 'Прогноз на месяц',
            prediction: predictions.monthPrediction,
            currentPrice: stock.currentPrice,
            holding: holding,
            currencyFormat: currencyFormat,
          ),
        if (predictions.yearPrediction != null)
          _PredictionCard(
            title: 'Прогноз на год',
            prediction: predictions.yearPrediction,
            currentPrice: stock.currentPrice,
            holding: holding,
            currencyFormat: currencyFormat,
          ),
      ],
    );
  }
}

class _PredictionCard extends StatelessWidget {
  final String title;
  final dynamic prediction;
  final double currentPrice;
  final dynamic holding;
  final NumberFormat currencyFormat;

  const _PredictionCard({
    required this.title,
    required this.prediction,
    required this.currentPrice,
    required this.holding,
    required this.currencyFormat,
  });

  @override
  Widget build(BuildContext context) {
    final isPositive = prediction.predictedPrice >= currentPrice;
    final potentialProfit = holding != null
      ? (prediction.predictedPrice - currentPrice) * holding.quantity
      : 0.0;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Прогнозируемая цена:', style: TextStyle(fontSize: 14)),
                Text(
                  currencyFormat.format(prediction.predictedPrice),
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: isPositive ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text('Изменение:', style: TextStyle(fontSize: 14)),
                Text(
                  '${isPositive ? '+' : ''}${prediction.changePercent.toStringAsFixed(2)}%',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: isPositive ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
            if (holding != null) ...[
              const Divider(height: 24),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: (isPositive ? Colors.green : Colors.red).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      'Потенциальная прибыль:',
                      style: TextStyle(fontWeight: FontWeight.w600),
                    ),
                    Text(
                      '${isPositive ? '+' : ''}${currencyFormat.format(potentialProfit)}',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: isPositive ? Colors.green : Colors.red,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// Вкладка с дивидендами
class DividendsTab extends StatelessWidget {
  final String ticker;
  final List<dynamic> dividends;
  final dynamic holding;
  final NumberFormat currencyFormat;

  const DividendsTab({
    super.key,
    required this.ticker,
    required this.dividends,
    required this.holding,
    required this.currencyFormat,
  });

  @override
  Widget build(BuildContext context) {
    if (dividends.isEmpty) {
      return const Center(
        child: Text('Нет данных о дивидендах'),
      );
    }

    final totalDividends = holding != null
      ? dividends.where((d) => d.status != 'predicted').fold(0.0, (sum, d) => sum + d.totalAmount)
      : 0.0;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        if (holding != null)
          Card(
            color: Colors.green[50],
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Ваши дивиденды',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    currencyFormat.format(totalDividends),
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.green),
                  ),
                  Text('Количество акций: ${holding.quantity} шт.'),
                ],
              ),
            ),
          ),
        const SizedBox(height: 16),
        ...dividends.map((dividend) {
          final isPaid = dividend.status == 'paid';
          final isUpcoming = dividend.status == 'upcoming';

          return Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: isPaid
                  ? Colors.green[50]
                  : isUpcoming
                    ? Colors.blue[50]
                    : Colors.grey[200],
                child: Icon(
                  isPaid
                    ? Icons.check_circle
                    : isUpcoming
                      ? Icons.schedule
                      : Icons.psychology,
                  color: isPaid
                    ? Colors.green
                    : isUpcoming
                      ? Colors.blue
                      : Colors.grey,
                ),
              ),
              title: Text(
                isPaid
                  ? 'Выплачено'
                  : isUpcoming
                    ? 'Ожидается'
                    : 'Прогноз',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              subtitle: Text(
                '${DateFormat('d MMMM yyyy', 'ru_RU').format(dividend.paymentDate)}\n${currencyFormat.format(dividend.amountPerShare)} на акцию',
              ),
              isThreeLine: true,
              trailing: holding != null
                ? Text(
                    currencyFormat.format(dividend.totalAmount),
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  )
                : null,
            ),
          );
        }),
      ],
    );
  }
}
