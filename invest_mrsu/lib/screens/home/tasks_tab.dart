import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../../providers/tasks_provider.dart';
import '../../providers/portfolio_provider.dart';
import '../../models/task.dart';

class TasksTab extends StatelessWidget {
  const TasksTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Задания'),
      ),
      body: Consumer2<TasksProvider, PortfolioProvider>(
        builder: (context, tasksProvider, portfolioProvider, _) {
          final tasks = tasksProvider.tasks;

          return ListView(
            padding: const EdgeInsets.all(16.0),
            children: [
              // Статистика
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.emoji_events, size: 40, color: Colors.amber),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Прогресс заданий',
                                  style: TextStyle(
                                    fontSize: 18,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  'Выполнено: ${tasksProvider.completedCount} из ${tasks.length}',
                                  style: TextStyle(color: Colors.grey[600]),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      LinearProgressIndicator(
                        value: tasks.isEmpty ? 0 : tasksProvider.completedCount / tasks.length,
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.green[50],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.monetization_on, color: Colors.green),
                            const SizedBox(width: 8),
                            Text(
                              'Получено наград: ${NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 0).format(tasksProvider.totalRewardsClaimed)}',
                              style: const TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // Заголовок
              const Text(
                'Все задания',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),

              // Список заданий
              ...tasks.map((task) {
                return _TaskCard(
                  task: task,
                  onClaim: () {
                    final reward = tasksProvider.claimReward(task.id);
                    if (reward > 0) {
                      portfolioProvider.addBonus(reward.toDouble());

                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(
                            'Получено ${NumberFormat.currency(locale: 'ru_RU', symbol: '₽', decimalDigits: 0).format(reward)}!',
                          ),
                          backgroundColor: Colors.green,
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    }
                  },
                );
              }),
            ],
          );
        },
      ),
    );
  }
}

class _TaskCard extends StatelessWidget {
  final GameTask task;
  final VoidCallback onClaim;

  const _TaskCard({
    required this.task,
    required this.onClaim,
  });

  @override
  Widget build(BuildContext context) {
    final isCompleted = task.status == TaskStatus.completed;
    final isClaimed = task.status == TaskStatus.claimed;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Иконка
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: isClaimed
                      ? Colors.grey[200]
                      : isCompleted
                        ? Colors.green[50]
                        : Theme.of(context).colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      task.type.icon,
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                ),
                const SizedBox(width: 12),

                // Информация
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        task.title,
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                          decoration: isClaimed ? TextDecoration.lineThrough : null,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        task.description,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),

                // Награда
                if (!isClaimed)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.amber[50],
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.amber),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.monetization_on, size: 16, color: Colors.amber),
                        const SizedBox(width: 4),
                        Text(
                          '${task.reward}₽',
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            color: Colors.amber,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 12),

            // Прогресс
            if (!isClaimed) ...[
              Row(
                children: [
                  Expanded(
                    child: LinearProgressIndicator(
                      value: task.progressPercent,
                      minHeight: 6,
                      borderRadius: BorderRadius.circular(3),
                      backgroundColor: Colors.grey[200],
                      color: isCompleted ? Colors.green : Theme.of(context).colorScheme.primary,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    '${task.progress}/${task.target}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
            ],

            // Кнопка получения награды
            if (isCompleted && !isClaimed)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: onClaim,
                  icon: const Icon(Icons.card_giftcard),
                  label: const Text('Получить награду'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),

            if (isClaimed)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.check_circle, color: Colors.green, size: 16),
                    SizedBox(width: 8),
                    Text(
                      'Выполнено',
                      style: TextStyle(
                        color: Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
