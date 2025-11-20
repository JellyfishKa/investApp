import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../models/price_history.dart';

class PriceChart extends StatefulWidget {
  final PriceHistory priceHistory;

  const PriceChart({super.key, required this.priceHistory});

  @override
  State<PriceChart> createState() => _PriceChartState();
}

class _PriceChartState extends State<PriceChart> {
  String _selectedPeriod = '1M'; // 1W, 1M, 3M, 1Y, ALL

  List<PricePoint> get _filteredPoints {
    switch (_selectedPeriod) {
      case '1W':
        return widget.priceHistory.getLastNDays(7);
      case '1M':
        return widget.priceHistory.getLastNDays(30);
      case '3M':
        return widget.priceHistory.getLastNDays(90);
      case '1Y':
        return widget.priceHistory.getLastNDays(365);
      case 'ALL':
      default:
        return widget.priceHistory.points;
    }
  }

  @override
  Widget build(BuildContext context) {
    final points = _filteredPoints;
    if (points.isEmpty) {
      return const Center(child: Text('Нет данных'));
    }

    final minPrice = points.map((p) => p.low).reduce((a, b) => a < b ? a : b);
    final maxPrice = points.map((p) => p.high).reduce((a, b) => a > b ? a : b);
    final priceRange = maxPrice - minPrice;

    return Column(
      children: [
        // Кнопки выбора периода
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: ['1W', '1M', '3M', '1Y', 'ALL'].map((period) {
              final isSelected = _selectedPeriod == period;
              return ChoiceChip(
                label: Text(period),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() {
                    _selectedPeriod = period;
                  });
                },
              );
            }).toList(),
          ),
        ),

        // График
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(right: 16, left: 8, bottom: 16),
            child: LineChart(
              LineChartData(
                minY: minPrice - (priceRange * 0.1),
                maxY: maxPrice + (priceRange * 0.1),
                lineBarsData: [
                  LineChartBarData(
                    spots: points.asMap().entries.map((entry) {
                      return FlSpot(
                        entry.key.toDouble(),
                        entry.value.close,
                      );
                    }).toList(),
                    isCurved: true,
                    color: Theme.of(context).colorScheme.primary,
                    barWidth: 2,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Theme.of(context).colorScheme.primary.withValues(alpha: 0.3),
                          Theme.of(context).colorScheme.primary.withValues(alpha: 0.0),
                        ],
                      ),
                    ),
                  ),
                ],
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 45,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          '${value.toStringAsFixed(1)}₽',
                          style: const TextStyle(fontSize: 10),
                        );
                      },
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 30,
                      getTitlesWidget: (value, meta) {
                        final index = value.toInt();
                        if (index < 0 || index >= points.length) {
                          return const Text('');
                        }

                        // Показываем только некоторые даты
                        final showEvery = points.length > 30 ? points.length ~/ 6 : 5;
                        if (index % showEvery != 0 && index != points.length - 1) {
                          return const Text('');
                        }

                        final date = points[index].date;
                        return Text(
                          DateFormat('d MMM').format(date),
                          style: const TextStyle(fontSize: 10),
                        );
                      },
                    ),
                  ),
                  rightTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                  topTitles: const AxisTitles(
                    sideTitles: SideTitles(showTitles: false),
                  ),
                ),
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: priceRange / 5,
                  getDrawingHorizontalLine: (value) {
                    return FlLine(
                      color: Colors.grey[300],
                      strokeWidth: 1,
                    );
                  },
                ),
                borderData: FlBorderData(show: false),
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipItems: (touchedSpots) {
                      return touchedSpots.map((spot) {
                        final index = spot.x.toInt();
                        if (index < 0 || index >= points.length) {
                          return null;
                        }

                        final point = points[index];
                        final currencyFormat = NumberFormat.currency(
                          locale: 'ru_RU',
                          symbol: '₽',
                          decimalDigits: 2,
                        );

                        return LineTooltipItem(
                          '${DateFormat('d MMM yyyy').format(point.date)}\n${currencyFormat.format(point.close)}',
                          const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                        );
                      }).toList();
                    },
                  ),
                ),
              ),
            ),
          ),
        ),

        // Статистика
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _StatItem(
                label: 'Мин',
                value: NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2).format(minPrice),
                color: Colors.red,
              ),
              _StatItem(
                label: 'Макс',
                value: NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2).format(maxPrice),
                color: Colors.green,
              ),
              _StatItem(
                label: 'Средн',
                value: NumberFormat.currency(
                  locale: 'ru_RU',
                  symbol: '₽',
                  decimalDigits: 2,
                ).format(
                  points.map((p) => p.close).reduce((a, b) => a + b) / points.length,
                ),
                color: Colors.blue,
              ),
            ],
          ),
        ),
      ],
    );
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatItem({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
