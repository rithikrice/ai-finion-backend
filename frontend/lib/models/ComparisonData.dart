class UserData {
  final num netWorth, monthlyIncome, investments, realEstate;
  UserData({
    required this.netWorth,
    required this.monthlyIncome,
    required this.investments,
    required this.realEstate,
  });

  factory UserData.fromJson(Map<String, dynamic> json) => UserData(
    netWorth: json['net_worth'],
    monthlyIncome: json['monthly_income'],
    investments: json['investments'],
    realEstate: json['real_estate'],
  );
}

class CelebrityData extends UserData {
  final String name;
  final List<String> primaryIncomeSources;
  final String dataSource;
  final String lastUpdated;

  CelebrityData({
    required this.name,
    required this.primaryIncomeSources,
    required this.dataSource,
    required this.lastUpdated,
    required num netWorth,
    required num monthlyIncome,
    required num investments,
    required num realEstate,
  }) : super(
         netWorth: netWorth,
         monthlyIncome: monthlyIncome,
         investments: investments,
         realEstate: realEstate,
       );

  factory CelebrityData.fromJson(Map<String, dynamic> json) => CelebrityData(
    name: json['name'],
    netWorth: json['net_worth'],
    monthlyIncome: json['monthly_income'],
    investments: json['investments'],
    realEstate: json['real_estate'],
    primaryIncomeSources: List<String>.from(json['primary_income_sources']),
    dataSource: json['data_source'],
    lastUpdated: json['last_updated'],
  );
}

class Comparison {
  final double netWorthPercentage;
  final double incomePercentage;
  final double investmentPercentage;
  final double realEstatePercentage;
  final String motivationalMessage;
  final String achievementInsight;
  final String nextMilestone;

  Comparison({
    required this.netWorthPercentage,
    required this.incomePercentage,
    required this.investmentPercentage,
    required this.realEstatePercentage,
    required this.motivationalMessage,
    required this.achievementInsight,
    required this.nextMilestone,
  });

  factory Comparison.fromJson(Map<String, dynamic> json) {
    return Comparison(
      netWorthPercentage: json['net_worth_percentage']?.toDouble() ?? 0.0,
      incomePercentage: json['income_percentage']?.toDouble() ?? 0.0,
      investmentPercentage: json['investment_percentage']?.toDouble() ?? 0.0,
      realEstatePercentage: json['real_estate_percentage']?.toDouble() ?? 0.0,
      motivationalMessage: json['motivational_message'] ?? '',
      achievementInsight: json['achievement_insight'] ?? '',
      nextMilestone: json['next_milestone'] ?? '',
    );
  }
}
