import 'package:flutter/foundation.dart';
import '../models/task.dart';
import '../data/mock_data.dart';

class TasksProvider with ChangeNotifier {
  List<GameTask> _tasks = [];
  int _totalRewardsClaimed = 0;

  TasksProvider() {
    _loadTasks();
  }

  List<GameTask> get tasks => _tasks;
  int get totalRewardsClaimed => _totalRewardsClaimed;

  List<GameTask> get activeTasks => _tasks.where((t) =>
    t.status == TaskStatus.active || t.status == TaskStatus.completed
  ).toList();

  List<GameTask> get completedTasks => _tasks.where((t) =>
    t.status == TaskStatus.completed
  ).toList();

  void _loadTasks() {
    _tasks = MockData.getInitialTasks();
    notifyListeners();
  }

  // Обновить прогресс задания
  void updateTaskProgress(TaskType type, {int increment = 1}) {
    final taskIndex = _tasks.indexWhere((t) => t.type == type);
    if (taskIndex < 0) return;

    final task = _tasks[taskIndex];
    if (task.status == TaskStatus.completed || task.status == TaskStatus.claimed) {
      return; // уже завершено
    }

    final newProgress = task.progress + increment;
    final isCompleted = newProgress >= task.target;

    _tasks[taskIndex] = task.copyWith(
      progress: newProgress,
      status: isCompleted ? TaskStatus.completed : TaskStatus.active,
    );

    notifyListeners();
  }

  // Забрать награду за задание
  int claimReward(String taskId) {
    final taskIndex = _tasks.indexWhere((t) => t.id == taskId);
    if (taskIndex < 0) return 0;

    final task = _tasks[taskIndex];
    if (task.status != TaskStatus.completed) {
      return 0; // нельзя забрать награду
    }

    _tasks[taskIndex] = task.copyWith(status: TaskStatus.claimed);
    _totalRewardsClaimed += task.reward;

    notifyListeners();
    return task.reward;
  }

  // Проверить, есть ли незабранные награды
  bool get hasUnclaimedRewards => _tasks.any((t) =>
    t.status == TaskStatus.completed
  );

  // Количество завершенных заданий
  int get completedCount => _tasks.where((t) =>
    t.status == TaskStatus.completed || t.status == TaskStatus.claimed
  ).length;
}
