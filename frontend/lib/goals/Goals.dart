import 'package:finion/goals/AddGoals.dart';
import 'package:finion/config/UriConstant.dart';
import 'package:finion/goals/GoalDetail.dart';
import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:finion/config/SessionManager.dart';
import 'package:finion/models/Goal.dart';

class GoalsScreen extends StatefulWidget {
  const GoalsScreen({super.key});

  @override
  _GoalsScreenState createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  List<Goal> goals = [];

  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchGoals();
  }

  Future<void> fetchGoals() async {
    final url = Uri.parse("${UriConstant.baseUrl}/goals");
    final headers = {
      'Content-Type': 'application/json',
      'Cookie': 'sessionid=${SessionManager().sessionId}',
    };

    try {
      final response = await http.get(url, headers: headers);
      if (response.statusCode == 200) {
        final resData = jsonDecode(response.body);

        // Properly cast each goal as Map<String, dynamic>
        final List<dynamic> rawGoals = resData["goals"];
        final List<Goal> parsedGoals =
            rawGoals.map((j) => Goal.fromJson(j)).toList();

        final jsonList = parsedGoals.map((g) => g.toJson()).toList();
        print(jsonEncode({'goals': jsonList}));

        setState(() {
          goals = parsedGoals;
          isLoading = false;
        });
      } else {
        throw Exception("Failed to load goals");
      }
    } catch (e) {
      print("Error fetching goals: $e");
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text("Error loading goals")));
    }
  }

  IconData _getGoalIcon(String? category) {
    switch (category?.toLowerCase()) {
      case 'vehicle':
        return Icons.directions_car;
      case 'vacation':
        return Icons.beach_access;
      case 'travel':
        return Icons.flight;
      case 'education':
        return Icons.school;
      case 'home':
        return Icons.home;
      default:
        return Icons.star;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.white,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.black),
          onPressed:
              () => {
                Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (context) => HomeNavigation()),
                  (route) => false,
                ),
              },
        ),
        title: const Text(
          'Goals',
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        elevation: 1,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFe0f7fa), Color(0xFFffffff)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Column(
            children: [
              if (isLoading)
                const Center(child: CircularProgressIndicator())
              else if (goals.isEmpty)
                const Center(child: Text("No goals found."))
              else
                Expanded(
                  child: ListView.builder(
                    itemCount: goals.length,
                    itemBuilder: (context, index) {
                      final g = goals[index];
                      final double progress =
                          (g.progressPercentage ?? 0.0) / 100;
                      final int months = g.remainingMonths ?? 1;
                      return GoalCard(
                        goal: g,
                        icon: _getGoalIcon(g.category),
                        title: g.name ?? "Goal",
                        target: '₹ ${g.targetAmount.round() ?? 0}',
                        saved: '₹ ${g.currentAmount.round() ?? 0}',
                        monthlyNeed:
                            '₹ ${g.monthlyNeeded.round() ?? 0} (${months} m)',
                        progress: progress,
                        progressLabel: 'Progress',
                        color: const Color.fromARGB(255, 13, 126, 115),
                      );
                    },
                  ),
                ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 12.0),
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => AddGoalScreen(),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add),
                    label: const Text('Add New Goal'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class GoalCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String target;
  final String saved;
  final String monthlyNeed;
  final double progress;
  final String progressLabel;
  final Color color;

  final Goal goal;

  const GoalCard({
    super.key,
    required this.goal,
    required this.icon,
    required this.title,
    required this.target,
    required this.saved,
    required this.monthlyNeed,
    required this.progress,
    required this.progressLabel,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            spreadRadius: 1,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              CircleAvatar(
                backgroundColor: color.withOpacity(0.1),
                child: Icon(icon, color: color),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  title,
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Details
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Target', style: TextStyle(fontSize: 16)),
              Text(
                target,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Saved', style: TextStyle(fontSize: 16)),
              Text(
                saved,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
          const SizedBox(height: 6),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text('Need/mo', style: TextStyle(fontSize: 16)),
              Text(
                monthlyNeed,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Progress bar
          LinearProgressIndicator(
            value: progress,
            color: color,
            backgroundColor: Colors.grey[300],
            minHeight: 8,
          ),
          const SizedBox(height: 6),
          Align(
            alignment: Alignment.centerRight,
            child: Text(
              '$progressLabel ${(progress * 100).toStringAsFixed(0)}%',
              style: TextStyle(color: color, fontWeight: FontWeight.w600),
            ),
          ),
          SizedBox(
            width: double.infinity,

            child: Padding(
              padding: const EdgeInsets.only(top: 8),
              child: ElevatedButton(
                onPressed: () {
                  print("Goal debug: ${jsonEncode(goal)}");

                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => Goaldetail(goal: goal),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'View All Details',
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
