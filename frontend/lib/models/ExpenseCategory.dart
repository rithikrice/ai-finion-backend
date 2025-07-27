class ExpenseCategory {
  final String category;
  final double amount;
  final double percentage;

  ExpenseCategory({
    required this.category,
    required this.amount,
    required this.percentage,
  });

  factory ExpenseCategory.fromJson(Map<String, dynamic> json) {
    return ExpenseCategory(
      category: json['category'],
      amount: json['amount'].toDouble(),
      percentage: json['percentage'].toDouble(),
    );
  }
}
