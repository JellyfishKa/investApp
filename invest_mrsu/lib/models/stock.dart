class Stock {
  final String ticker;
  final String name;
  final String company;
  final double currentPrice;
  final double previousClose;
  final double change;
  final double changePercent;
  final int volume;
  final String logo;
  final bool isParent; // true если это головная компания

  Stock({
    required this.ticker,
    required this.name,
    required this.company,
    required this.currentPrice,
    required this.previousClose,
    required this.change,
    required this.changePercent,
    required this.volume,
    required this.logo,
    this.isParent = false,
  });

  // Для копирования с изменениями
  Stock copyWith({
    String? ticker,
    String? name,
    String? company,
    double? currentPrice,
    double? previousClose,
    double? change,
    double? changePercent,
    int? volume,
    String? logo,
    bool? isParent,
  }) {
    return Stock(
      ticker: ticker ?? this.ticker,
      name: name ?? this.name,
      company: company ?? this.company,
      currentPrice: currentPrice ?? this.currentPrice,
      previousClose: previousClose ?? this.previousClose,
      change: change ?? this.change,
      changePercent: changePercent ?? this.changePercent,
      volume: volume ?? this.volume,
      logo: logo ?? this.logo,
      isParent: isParent ?? this.isParent,
    );
  }
}
