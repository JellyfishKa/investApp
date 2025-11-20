class GameTask {
  final String id;
  final String title;
  final String description;
  final int reward; // бонусные рубли
  final TaskStatus status;
  final TaskType type;
  final int progress;
  final int target;

  GameTask({
    required this.id,
    required this.title,
    required this.description,
    required this.reward,
    required this.status,
    required this.type,
    this.progress = 0,
    this.target = 1,
  });

  double get progressPercent => target > 0 ? (progress / target) : 0;

  bool get isCompleted => status == TaskStatus.completed;

  GameTask copyWith({
    String? id,
    String? title,
    String? description,
    int? reward,
    TaskStatus? status,
    TaskType? type,
    int? progress,
    int? target,
  }) {
    return GameTask(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      reward: reward ?? this.reward,
      status: status ?? this.status,
      type: type ?? this.type,
      progress: progress ?? this.progress,
      target: target ?? this.target,
    );
  }
}

enum TaskStatus {
  active,
  completed,
  claimed,
}

enum TaskType {
  welcome,
  firstBuy,
  viewPredictions,
  holdDays,
  dailyLogin,
}

extension TaskTypeExtension on TaskType {
  String get icon {
    switch (this) {
      case TaskType.welcome:
        return '👋';
      case TaskType.firstBuy:
        return '💰';
      case TaskType.viewPredictions:
        return '📊';
      case TaskType.holdDays:
        return '⏳';
      case TaskType.dailyLogin:
        return '📅';
    }
  }
}
