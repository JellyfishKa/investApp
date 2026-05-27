import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/comparison_provider.dart';
import '../../providers/stocks_provider.dart';
import '../../models/comparison.dart';

class ComparisonTab extends StatelessWidget {
  const ComparisonTab({super.key});

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Сравнение акций'),
      ),
      body: Consumer2<ComparisonProvider, StocksProvider>(
        builder: (context, comparisonProvider, stocksProvider, _) {
          if (!comparisonProvider.hasComparison) {
            return _EmptyComparisonState(stocksProvider: stocksProvider);
          }

          return ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              // Выбранные акции
              _SelectedStocksWidget(
                stocks: comparisonProvider.selectedStocks,
                onRemove: (ticker) {
                  comparisonProvider.removeStockFromComparison(ticker);
                },
              ),
              const SizedBox(height: 20),

              // Таблица метрик
              _ComparisonTableWidget(
                selectedStocks: comparisonProvider.selectedStocks,
                metrics: comparisonProvider.metrics,
                currencyFormat: currencyFormat,
              ),
              const SizedBox(height: 20),

              // Рейтинги
              Text(
                'Оценки',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              ..._buildRatingCards(comparisonProvider),
              const SizedBox(height: 20),

              // Кнопка очистить
              ElevatedButton.icon(
                onPressed: () => comparisonProvider.clearComparison(),
                icon: const Icon(Icons.delete_outline),
                label: const Text('Очистить сравнение'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red[400],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  List<Widget> _buildRatingCards(ComparisonProvider provider) {
    return provider.selectedStocks.map((stock) {
      final rating = provider.ratings[stock.ticker];
      if (rating == null) return const SizedBox.shrink();

      return Card(
        margin: const EdgeInsets.only(bottom: 12),
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
                          stock.ticker,
                          style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: rating.getRatingColor(),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      children: [
                        Text(
                          '${rating.overall.toStringAsFixed(0)}/100',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                        Text(
                          rating.getRatingText(),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }).toList();
  }
}

class _EmptyComparisonState extends StatelessWidget {
  final StocksProvider stocksProvider;

  const _EmptyComparisonState({required this.stocksProvider});

  @override
  Widget build(BuildContext context) {
    return Consumer<ComparisonProvider>(
      builder: (context, comparisonProvider, _) {
        return Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.compare_arrows,
                size: 80,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                'Выберите 2+ акции для сравнения',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 24),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: stocksProvider.stocks.map((stock) {
                    return ElevatedButton.icon(
                      onPressed: () {
                        comparisonProvider.addStockToComparison(stock);
                      },
                      icon: const Icon(Icons.add),
                      label: Text('${stock.ticker}'),
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _SelectedStocksWidget extends StatelessWidget {
  final List stocks;
  final Function(String) onRemove;

  const _SelectedStocksWidget({
    required this.stocks,
    required this.onRemove,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Выбранные акции',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: stocks.map((stock) {
                return Chip(
                  label: Text(stock.ticker),
                  onDeleted: () => onRemove(stock.ticker),
                  deleteIcon: const Icon(Icons.close, size: 18),
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _ComparisonTableWidget extends StatelessWidget {
  final List selectedStocks;
  final Map<String, List<ComparisonMetric>> metrics;
  final NumberFormat currencyFormat;

  const _ComparisonTableWidget({
    required this.selectedStocks,
    required this.metrics,
    required this.currencyFormat,
  });

  @override
  Widget build(BuildContext context) {
    if (selectedStocks.isEmpty) return const SizedBox.shrink();

    final firstTicker = (selectedStocks.first as dynamic).ticker;
    final metricList = metrics[firstTicker] ?? [];

    return Card(
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: DataTable(
          columns: [
            const DataColumn(label: Text('Метрика')),
            ...selectedStocks.map((stock) {
              return DataColumn(
                label: Text(
                  (stock as dynamic).ticker,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              );
            }),
          ],
          rows: metricList.map((metric) {
            return DataRow(
              cells: [
                DataCell(Text(metric.label)),
                ...selectedStocks.map((stock) {
                  final stockMetric = metrics[(stock as dynamic).ticker]
                          ?.firstWhere(
                        (m) => m.label == metric.label,
                        orElse: () => ComparisonMetric(
                          label: '',
                          value: 0,
                          unit: '',
                        ),
                      ) ??
                      ComparisonMetric(label: '', value: 0, unit: '');

                  return DataCell(
                    Text(
                      '${stockMetric.value.toStringAsFixed(2)} ${stockMetric.unit}',
                      style: TextStyle(
                        color: stockMetric.isBetter ? Colors.green : Colors.grey,
                        fontWeight: stockMetric.isBetter ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  );
                }),
              ],
            );
          }).toList(),
        ),
      ),
    );
  }
}
