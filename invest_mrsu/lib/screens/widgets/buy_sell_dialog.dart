import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/portfolio_provider.dart';
import '../../providers/tasks_provider.dart';
import '../../models/stock.dart';
import '../../models/task.dart';

class BuySellDialog extends StatefulWidget {
  final Stock stock;
  final bool isBuy;
  final int? maxQuantity;

  const BuySellDialog({
    super.key,
    required this.stock,
    required this.isBuy,
    this.maxQuantity,
  });

  @override
  State<BuySellDialog> createState() => _BuySellDialogState();
}

class _BuySellDialogState extends State<BuySellDialog> {
  final _quantityController = TextEditingController(text: '1');
  int _quantity = 1;

  @override
  void dispose() {
    _quantityController.dispose();
    super.dispose();
  }

  double get _totalCost => widget.stock.currentPrice * _quantity;

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2);

    return Consumer2<PortfolioProvider, TasksProvider>(
      builder: (context, portfolio, tasks, _) {
        final canAfford = widget.isBuy
          ? portfolio.portfolio.balance >= _totalCost
          : true;
        final hasEnoughShares = !widget.isBuy
          ? (widget.maxQuantity != null && _quantity <= widget.maxQuantity!)
          : true;

        return AlertDialog(
          title: Text(widget.isBuy ? 'Купить акции' : 'Продать акции'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Информация об акции
                Row(
                  children: [
                    Text(
                      widget.stock.logo,
                      style: const TextStyle(fontSize: 32),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            widget.stock.name,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                          Text(
                            currencyFormat.format(widget.stock.currentPrice),
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),

                // Количество
                TextField(
                  controller: _quantityController,
                  keyboardType: TextInputType.number,
                  inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                  decoration: InputDecoration(
                    labelText: 'Количество',
                    border: const OutlineInputBorder(),
                    suffixText: 'шт.',
                    helperText: widget.isBuy
                      ? 'Доступно: ${currencyFormat.format(portfolio.portfolio.balance)}'
                      : 'У вас: ${widget.maxQuantity} шт.',
                  ),
                  onChanged: (value) {
                    setState(() {
                      _quantity = int.tryParse(value) ?? 1;
                      if (_quantity < 1) {
                        _quantity = 1;
                        _quantityController.text = '1';
                      }
                    });
                  },
                ),
                const SizedBox(height: 20),

                // Итого
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Цена за 1 акцию:'),
                          Text(
                            currencyFormat.format(widget.stock.currentPrice),
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Количество:'),
                          Text(
                            '$_quantity шт.',
                            style: const TextStyle(fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                      const Divider(height: 20),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Итого:',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            currencyFormat.format(_totalCost),
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: widget.isBuy ? Colors.red : Colors.green,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),

                // Предупреждения
                if (widget.isBuy && !canAfford) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.error_outline, color: Colors.red),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Недостаточно средств',
                            style: TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],

                if (!widget.isBuy && !hasEnoughShares) ...[
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.error_outline, color: Colors.red),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Недостаточно акций',
                            style: TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Отмена'),
            ),
            ElevatedButton(
              onPressed: (canAfford && hasEnoughShares)
                ? () {
                    bool success;
                    if (widget.isBuy) {
                      success = portfolio.buyStock(widget.stock, _quantity);
                      if (success) {
                        // Обновляем прогресс задания "первая покупка"
                        tasks.updateTaskProgress(TaskType.firstBuy);
                      }
                    } else {
                      success = portfolio.sellStock(widget.stock, _quantity);
                    }

                    if (success) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            widget.isBuy
                              ? 'Куплено $_quantity шт. ${widget.stock.ticker}'
                              : 'Продано $_quantity шт. ${widget.stock.ticker}',
                          ),
                          backgroundColor: widget.isBuy ? Colors.green : Colors.orange,
                        ),
                      );
                    }
                  }
                : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: widget.isBuy ? Colors.green : Colors.red,
                foregroundColor: Colors.white,
              ),
              child: Text(widget.isBuy ? 'Купить' : 'Продать'),
            ),
          ],
        );
      },
    );
  }
}
