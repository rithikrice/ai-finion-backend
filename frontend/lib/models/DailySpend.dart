class DailySpend {
  final DateTime date;
  final double amount;

  DailySpend({required this.date, required this.amount});

  factory DailySpend.fromJson(Map<String, dynamic> json) {
    return DailySpend(
      date: DateTime.parse(json['date']),
      amount: json['amount']?.toDouble() ?? 0,
    );
  }
}
