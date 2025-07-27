import 'package:finion/models/Goal.dart';
import 'package:flutter/material.dart';

class Goaldetail extends StatelessWidget {
  final Goal goal;

  const Goaldetail({Key? key, required this.goal}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    const Color accentColor = Color(0xFF0D4D4D);
    const double sidePadding = 28.0;

    final String goalName = goal.name ?? "";
    final String description = goal.estimationReasoning ?? "";
    final double targetAmount = (goal.targetAmount ?? 0).toDouble();
    final String targetDate = goal.targetDate?.substring(0, 10) ?? "";
    final int remainingMonths = goal.remainingMonths ?? 0;
    final double progressPercentage = (goal.progressPercentage ?? 0).toDouble();
    final double currentSavings = (goal.currentAmount ?? 0).toDouble();

    final DetailedReasoning? detailedReasoning = goal.detailedReasoning;

    final String categoryBasis =
        detailedReasoning?.categoryBasis ?? "Not available";
    final String financialAnalysis =
        detailedReasoning?.financialAnalysis ?? "Not available";
    final double monthlySavingsNeeded =
        (detailedReasoning?.monthlySavingsNeeded ?? 0).toDouble();
    final String achievementDifficulty =
        detailedReasoning?.achievementDifficulty ?? "Unknown";

    final List<String> insights = [categoryBasis, financialAnalysis];

    final FinionInsights? finionInsights = goal.finionInsights;
    final String successProbability =
        finionInsights?.successProbability ?? "Unknown";
    final List<String> savingsStrategy = finionInsights?.savingsStrategy ?? [];
    final List<String> lifestyleRecommendations =
        finionInsights?.lifestyleRecommendations ?? [];
    final List<String> investmentOpportunities =
        finionInsights?.investmentOpportunities ?? [];
    final String riskAssessment = finionInsights?.riskAssessment ?? "None";

    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 244, 247, 247),
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: const Text(
          'Goal Details',
          style: TextStyle(color: Colors.black),
        ),
        centerTitle: true,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFF2F8F7), Color(0xFFE3F2EF)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(
              horizontal: sidePadding,
              vertical: 20,
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 20),

                // Title and duration
                Text(
                  goalName,
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w700,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  '$remainingMonths months to achieve',
                  style: const TextStyle(fontSize: 16, color: Colors.black54),
                ),
                const SizedBox(height: 30),

                // Progress section
                const Text(
                  'Progress',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 12),
                Stack(
                  children: [
                    Container(
                      height: 14,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                    FractionallySizedBox(
                      widthFactor: (progressPercentage / 100).clamp(0.0, 1.0),
                      child: Container(
                        height: 14,
                        decoration: BoxDecoration(
                          color: accentColor,
                          borderRadius: BorderRadius.circular(30),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text("0%", style: TextStyle(color: Colors.black87)),
                    Text(
                      "${progressPercentage.toStringAsFixed(0)}%",
                      style: const TextStyle(color: Colors.black87),
                    ),
                  ],
                ),
                const SizedBox(height: 30),

                // Goal Overview
                const Text(
                  'Goal Overview',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 14),
                GlassCard(
                  children: [
                    InfoTile(
                      title: "Current savings",
                      value: "₹ ${currentSavings.toStringAsFixed(0)}",
                    ),
                    InfoTile(
                      title: "Achievement Difficulty",
                      value: achievementDifficulty,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                GlassCard(
                  children: [
                    InfoTile(
                      title: "Required Savings pm",
                      value: "₹ ${monthlySavingsNeeded.toStringAsFixed(0)}",
                    ),
                    InfoTile(
                      title: "Success Probability",
                      value: successProbability,
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                GlassCard(
                  children: [
                    InfoTile(
                      title: "Target Amount",
                      value: "₹ ${targetAmount.toStringAsFixed(0)}",
                    ),
                    InfoTile(title: "Target Date", value: targetDate),
                  ],
                ),
                const SizedBox(height: 12),
                GlassCard(
                  children: [
                    // InfoTile(
                    //   title: "AI Estimated",
                    //   value: aiEstimated ? "Yes" : "No",
                    // ),
                    InfoTile(title: "Goal Description", value: description),
                  ],
                ),
                const SizedBox(height: 30),

                // Financial analysis
                const Text(
                  'Analysis',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),
                ...insights
                    .map((text) => BulletPoint(text: text.toString()))
                    .toList(),

                const SizedBox(height: 30),
                const Text(
                  'AI Estimation Reasoning',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 8),

                // Text(
                //   estimationReasoning,
                //   style: const TextStyle(fontSize: 14, color: Colors.black87),
                // ),
                // const SizedBox(height: 16),
                // const Text(
                //   'Category Basis',
                //   style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                // ),
                // const SizedBox(height: 4),
                // Text(
                //   categoryBasis,
                //   style: const TextStyle(fontSize: 14, color: Colors.black87),
                // ),
                const SizedBox(height: 30),

                // Path to achieve
                const Text(
                  'Path to Achieve',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.95),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 10,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ...savingsStrategy
                          .map((text) => BulletPoint(text: text.toString()))
                          .toList(),
                      ...lifestyleRecommendations
                          .map((text) => BulletPoint(text: text.toString()))
                          .toList(),
                    ],
                  ),
                ),

                const SizedBox(height: 30),

                // Additional insights
                const Text(
                  'Additional Insights',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.95),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 10,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Investment Opportunities",
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 8),
                      ...investmentOpportunities
                          .map((text) => BulletPoint(text: text.toString()))
                          .toList(),
                      const SizedBox(height: 16),
                      const Text(
                        "Risk Assessment",
                        style: TextStyle(fontWeight: FontWeight.w600),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        riskAssessment,
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class InfoTile extends StatelessWidget {
  final String title;
  final String value;

  const InfoTile({required this.title, required this.value, Key? key})
    : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: const TextStyle(fontSize: 14, color: Colors.black54),
            ),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class GlassCard extends StatelessWidget {
  final List<Widget> children;

  const GlassCard({required this.children, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.95),
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            color: Colors.black12,
            blurRadius: 10,
            offset: Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: children,
      ),
    );
  }
}

class BulletPoint extends StatelessWidget {
  final String text;

  const BulletPoint({required this.text, Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text("• ", style: TextStyle(fontSize: 16)),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(fontSize: 14, color: Colors.black87),
            ),
          ),
        ],
      ),
    );
  }
}
