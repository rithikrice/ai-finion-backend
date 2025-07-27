class PaymentNudge {
  final String category;
  final double amount;
  final DateTime due;

  PaymentNudge({
    required this.category,
    required this.amount,
    required this.due,
  });

  factory PaymentNudge.fromJson(Map<String, dynamic> json) {
    return PaymentNudge(
      category: json['category'],
      amount: json['amount'].toDouble(),
      due: DateTime.parse(json['due']),
    );
  }
}
