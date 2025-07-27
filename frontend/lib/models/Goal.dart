// lib/models/Goal.dart

import 'dart:convert';

class Goal {
  final String id;
  final String userId;
  final String name;
  final double targetAmount;
  final double currentAmount;
  final String targetDate;
  final String category;
  final String? description;
  final bool? aiEstimated;
  final String? estimationReasoning;
  final DetailedReasoning? detailedReasoning;
  final FinionInsights? finionInsights;
  final double progressPercentage;
  final double monthlyNeeded;
  final int remainingMonths;
  final double remainingAmount;
  final bool onTrack;

  Goal({
    required this.id,
    required this.userId,
    required this.name,
    required this.targetAmount,
    required this.currentAmount,
    required this.targetDate,
    required this.category,
    this.description,
    this.aiEstimated,
    this.estimationReasoning,
    this.detailedReasoning,
    this.finionInsights,
    required this.progressPercentage,
    required this.monthlyNeeded,
    required this.remainingMonths,
    required this.remainingAmount,
    required this.onTrack,
  });

  factory Goal.fromJson(Map<String, dynamic> json) {
    return Goal(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      name: json['name'] as String,
      targetAmount: (json['target_amount'] as num).toDouble(),
      currentAmount: (json['current_amount'] as num).toDouble(),
      targetDate: json['target_date'] as String,
      category: json['category'] as String,
      description: json['description'] as String?,
      aiEstimated: json['ai_estimated'] as bool?,
      estimationReasoning: json['estimation_reasoning'] as String?,
      detailedReasoning:
          json['detailed_reasoning'] != null
              ? DetailedReasoning.fromJson(json['detailed_reasoning'])
              : null,
      finionInsights:
          json['finion_insights'] != null
              ? FinionInsights.fromJson(json['finion_insights'])
              : null,
      progressPercentage: (json['progress_percentage'] as num).toDouble(),
      monthlyNeeded: (json['monthly_needed'] as num).toDouble(),
      remainingMonths: json['remaining_months'] as int,
      remainingAmount: (json['remaining_amount'] as num).toDouble(),
      onTrack: json['on_track'] as bool,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'user_id': userId,
    'name': name,
    'target_amount': targetAmount,
    'current_amount': currentAmount,
    'target_date': targetDate,
    'category': category,
    'description': description,
    'ai_estimated': aiEstimated,
    'estimation_reasoning': estimationReasoning,
    'detailed_reasoning': detailedReasoning?.toJson(),
    'finion_insights': finionInsights?.toJson(),
    'progress_percentage': progressPercentage,
    'monthly_needed': monthlyNeeded,
    'remaining_months': remainingMonths,
    'remaining_amount': remainingAmount,
    'on_track': onTrack,
  };

  @override
  String toString() => jsonEncode(toJson());
}

class DetailedReasoning {
  final String? categoryBasis;
  final String? financialAnalysis;
  final double? monthlySavingsNeeded;
  final String? achievementDifficulty;

  DetailedReasoning({
    this.categoryBasis,
    this.financialAnalysis,
    this.monthlySavingsNeeded,
    this.achievementDifficulty,
  });

  factory DetailedReasoning.fromJson(Map<String, dynamic> json) {
    return DetailedReasoning(
      categoryBasis: json['category_basis'] as String?,
      financialAnalysis: json['financial_analysis'] as String?,
      monthlySavingsNeeded:
          (json['monthly_savings_needed'] as num?)?.toDouble(),
      achievementDifficulty: json['achievement_difficulty'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'category_basis': categoryBasis,
    'financial_analysis': financialAnalysis,
    'monthly_savings_needed': monthlySavingsNeeded,
    'achievement_difficulty': achievementDifficulty,
  };
}

class FinionInsights {
  final List<String>? savingsStrategy;
  final List<String>? lifestyleRecommendations;
  final List<String>? investmentOpportunities;
  final String? riskAssessment;
  final String? successProbability;

  FinionInsights({
    this.savingsStrategy,
    this.lifestyleRecommendations,
    this.investmentOpportunities,
    this.riskAssessment,
    this.successProbability,
  });

  factory FinionInsights.fromJson(Map<String, dynamic> json) {
    return FinionInsights(
      savingsStrategy:
          (json['savings_strategy'] as List<dynamic>?)?.cast<String>(),
      lifestyleRecommendations:
          (json['lifestyle_recommendations'] as List<dynamic>?)?.cast<String>(),
      investmentOpportunities:
          (json['investment_opportunities'] as List<dynamic>?)?.cast<String>(),
      riskAssessment: json['risk_assessment'] as String?,
      successProbability: json['success_probability'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'savings_strategy': savingsStrategy,
    'lifestyle_recommendations': lifestyleRecommendations,
    'investment_opportunities': investmentOpportunities,
    'risk_assessment': riskAssessment,
    'success_probability': successProbability,
  };
}
