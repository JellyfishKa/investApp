import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/auth_provider.dart';
import '../../providers/portfolio_provider.dart';
import '../../providers/stocks_provider.dart';
import '../../providers/tasks_provider.dart';
import '../../models/task.dart';

class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    final currencyFormat = NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 2);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Invest MRSU'),
        actions: [
          // Иконка профиля
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              _showProfileDialog(context);
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          // Обновление данных (в будущем)
          await Future.delayed(const Duration(seconds: 1));
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Приветствие
              Consumer<AuthProvider>(
                builder: (context, auth, _) {
                  return Text(
                    'Привет, ${auth.userEmail?.split('@').first ?? 'Инвестор'}!',
                    style: Theme.of(context).textTheme.headlineSmall,
                  );
                },
              ),
              const SizedBox(height: 8),
              Text(
                'Сегодня ${DateFormat('d MMMM yyyy', 'ru_RU').format(DateTime.now())}',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 24),

              // Баланс портфеля
              Consumer<PortfolioProvider>(
                builder: (context, portfolio, _) {
                  return Card(
                    child: Padding(
                      padding: const EdgeInsets.all(20.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.account_balance_wallet, size: 32),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text(
                                      'Общий баланс',
                                      style: TextStyle(
                                        fontSize: 14,
                                        color: Colors.grey,
                                      ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      currencyFormat.format(portfolio.portfolio.totalValue),
                                      style: const TextStyle(
                                        fontSize: 28,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const Divider(height: 24),
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Свободные средства', style: TextStyle(fontSize: 12, color: Colors.grey)),
                                    const SizedBox(height: 4),
                                    Text(
                                      currencyFormat.format(portfolio.portfolio.balance),
                                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                                    ),
                                  ],
                                ),
                              ),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('В акциях', style: TextStyle(fontSize: 12, color: Colors.grey)),
                                    const SizedBox(height: 4),
                                    Text(
                                      currencyFormat.format(portfolio.portfolio.holdingsValue),
                                      style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          if (portfolio.portfolio.holdings.isNotEmpty) ...[
                            const SizedBox(height: 12),
                            Row(
                              children: [
                                Icon(
                                  portfolio.portfolio.totalProfitLoss >= 0
                                    ? Icons.trending_up
                                    : Icons.trending_down,
                                  color: portfolio.portfolio.totalProfitLoss >= 0
                                    ? Colors.green
                                    : Colors.red,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  '${portfolio.portfolio.totalProfitLoss >= 0 ? '+' : ''}${currencyFormat.format(portfolio.portfolio.totalProfitLoss)}',
                                  style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                    color: portfolio.portfolio.totalProfitLoss >= 0
                                      ? Colors.green
                                      : Colors.red,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 24),

              // Быстрые действия
              Text(
                'Быстрые действия',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _QuickActionCard(
                      icon: Icons.trending_up,
                      title: 'Купить',
                      color: Colors.green,
                      onTap: () {
                        // Переключиться на вкладку акций
                        DefaultTabController.of(context).animateTo(1);
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _QuickActionCard(
                      icon: Icons.trending_down,
                      title: 'Продать',
                      color: Colors.red,
                      onTap: () {
                        // Переключиться на портфель
                        DefaultTabController.of(context).animateTo(2);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Активные задания
              Consumer<TasksProvider>(
                builder: (context, tasks, _) {
                  final activeTasks = tasks.activeTasks.take(3).toList();
                  if (activeTasks.isEmpty) return const SizedBox.shrink();

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Активные задания',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          if (tasks.hasUnclaimedRewards)
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.orange,
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: const Text(
                                'Награда!',
                                style: TextStyle(color: Colors.white, fontSize: 12),
                              ),
                            ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      ...activeTasks.map((task) => Padding(
                        padding: const EdgeInsets.only(bottom: 8.0),
                        child: Card(
                          child: ListTile(
                            leading: Text(task.type.icon, style: const TextStyle(fontSize: 24)),
                            title: Text(task.title),
                            subtitle: LinearProgressIndicator(
                              value: task.progressPercent,
                              backgroundColor: Colors.grey[200],
                            ),
                            trailing: task.status == TaskStatus.completed
                              ? const Icon(Icons.check_circle, color: Colors.green)
                              : Text('${task.progress}/${task.target}'),
                          ),
                        ),
                      )),
                    ],
                  );
                },
              ),
              const SizedBox(height: 24),

              // Популярные акции
              Text(
                'Акции Газпрома',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 12),
              Consumer<StocksProvider>(
                builder: (context, stocks, _) {
                  return Column(
                    children: stocks.stocks.take(3).map((stock) {
                      return Card(
                        margin: const EdgeInsets.only(bottom: 8),
                        child: ListTile(
                          leading: CircleAvatar(
                            child: Text(stock.logo, style: const TextStyle(fontSize: 24)),
                          ),
                          title: Text(stock.name),
                          subtitle: Text(stock.ticker),
                          trailing: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                currencyFormat.format(stock.currentPrice),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                ),
                              ),
                              Text(
                                '${stock.change >= 0 ? '+' : ''}${stock.changePercent.toStringAsFixed(2)}%',
                                style: TextStyle(
                                  color: stock.change >= 0 ? Colors.green : Colors.red,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                          onTap: () {
                            // Перейти к деталям акции (позже)
                          },
                        ),
                      );
                    }).toList(),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showProfileDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Профиль'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Consumer<AuthProvider>(
              builder: (context, auth, _) {
                return Text('Email: ${auth.userEmail}');
              },
            ),
            const SizedBox(height: 8),
            Consumer<TasksProvider>(
              builder: (context, tasks, _) {
                return Text('Выполнено заданий: ${tasks.completedCount}');
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              Provider.of<AuthProvider>(context, listen: false).logout();
            },
            child: const Text('Выйти'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Закрыть'),
          ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.title,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            children: [
              Icon(icon, size: 32, color: color),
              const SizedBox(height: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
