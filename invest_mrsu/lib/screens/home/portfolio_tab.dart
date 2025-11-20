import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/portfolio_provider.dart';
import '../../providers/stocks_provider.dart';
import '../../models/transaction.dart';
import '../stock/stock_detail_screen.dart';

class PortfolioTab extends StatelessWidget {
  const PortfolioTab({super.key});

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2);

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Портфель'),
          bottom: const TabBar(
            tabs: [
              Tab(text: 'Активы'),
              Tab(text: 'История'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _HoldingsTab(currencyFormat: currencyFormat),
            _TransactionsTab(currencyFormat: currencyFormat),
          ],
        ),
      ),
    );
  }
}

class _HoldingsTab extends StatelessWidget {
  final NumberFormat currencyFormat;

  const _HoldingsTab({required this.currencyFormat});

  @override
  Widget build(BuildContext context) {
    return Consumer2<PortfolioProvider, StocksProvider>(
      builder: (context, portfolioProvider, stocksProvider, _) {
        final holdings = portfolioProvider.portfolio.holdings;

        if (holdings.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.account_balance_wallet_outlined,
                  size: 80,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  'Ваш портфель пуст',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Начните инвестировать прямо сейчас!',
                  style: TextStyle(color: Colors.grey[500]),
                ),
              ],
            ),
          );
        }

        return ListView(
          padding: const EdgeInsets.all(16.0),
          children: holdings.map((holding) {
            final stock = stocksProvider.getStock(holding.ticker);
            if (stock == null) return const SizedBox.shrink();

            final profitLoss = holding.profitLoss;
            final profitLossPercent = holding.profitLossPercent;
            final isProfit = profitLoss >= 0;

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              child: InkWell(
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => StockDetailScreen(ticker: stock.ticker),
                    ),
                  );
                },
                borderRadius: BorderRadius.circular(12),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            stock.logo,
                            style: const TextStyle(fontSize: 32),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  stock.name,
                                  style: const TextStyle(
                                    fontWeight: FontWeight.bold,
                                    fontSize: 16,
                                  ),
                                ),
                                Text(
                                  '${holding.quantity} шт. × ${currencyFormat.format(holding.currentPrice)}',
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 14,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                currencyFormat.format(holding.currentValue),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                ),
                              ),
                              Text(
                                '${isProfit ? '+' : ''}${currencyFormat.format(profitLoss)}',
                                style: TextStyle(
                                  color: isProfit ? Colors.green : Colors.red,
                                  fontSize: 14,
                                  fontWeight: FontWeight.w600,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: _InfoChip(
                              label: 'Средняя цена',
                              value: currencyFormat.format(holding.averagePrice),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: _InfoChip(
                              label: 'Доходность',
                              value: '${isProfit ? '+' : ''}${profitLossPercent.toStringAsFixed(2)}%',
                              color: isProfit ? Colors.green : Colors.red,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            );
          }).toList(),
        );
      },
    );
  }
}

class _TransactionsTab extends StatelessWidget {
  final NumberFormat currencyFormat;

  const _TransactionsTab({required this.currencyFormat});

  @override
  Widget build(BuildContext context) {
    return Consumer<PortfolioProvider>(
      builder: (context, portfolio, _) {
        final transactions = portfolio.transactions;

        if (transactions.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.receipt_long_outlined,
                  size: 80,
                  color: Colors.grey[400],
                ),
                const SizedBox(height: 16),
                Text(
                  'Нет транзакций',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          );
        }

        return ListView.builder(
          padding: const EdgeInsets.all(16.0),
          itemCount: transactions.length,
          itemBuilder: (context, index) {
            final transaction = transactions[index];
            final isBuy = transaction.type == TransactionType.buy;

            return Card(
              margin: const EdgeInsets.only(bottom: 8),
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: isBuy ? Colors.green[50] : Colors.red[50],
                  child: Icon(
                    isBuy ? Icons.add : Icons.remove,
                    color: isBuy ? Colors.green : Colors.red,
                  ),
                ),
                title: Text(
                  '${transaction.type.displayName} ${transaction.ticker}',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(
                  '${transaction.quantity} шт. × ${currencyFormat.format(transaction.price)}\n${DateFormat('d MMM yyyy, HH:mm', 'ru_RU').format(transaction.timestamp)}',
                ),
                isThreeLine: true,
                trailing: Text(
                  '${isBuy ? '-' : '+'}${currencyFormat.format(transaction.total)}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: isBuy ? Colors.red : Colors.green,
                    fontSize: 16,
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}

class _InfoChip extends StatelessWidget {
  final String label;
  final String value;
  final Color? color;

  const _InfoChip({
    required this.label,
    required this.value,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 2),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
