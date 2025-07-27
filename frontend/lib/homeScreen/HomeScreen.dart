import 'package:finion/ai/AIChatScreen.dart';
import 'package:finion/ai/CelebrityInputScreen.dart';
import 'package:finion/ai/VoiceChat.dart';
import 'package:finion/config/SessionManager.dart';
import 'package:finion/config/UriConstant.dart';
import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:finion/models/PaymentNudge.dart';
import 'package:finion/payement/PaymentGateway.dart';
import 'package:finion/profile/ProfileScreen.dart';
import 'package:finion/transactions/TransactionAnalysis.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<PaymentNudge> nudges = [];
  bool isLoading = true;
  final sessionId = SessionManager().sessionId;
  String? insightMessage;

  @override
  void initState() {
    super.initState();
    fetchNudges();
    fetchInsightMessage();
  }

  Future<void> fetchNudges() async {
    final response = await http.get(
      Uri.parse("${UriConstant.baseUrl}/nudges"),
      headers: {"Cookie": "sessionid=$sessionId"},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      final List<PaymentNudge> loaded =
          data.map((json) => PaymentNudge.fromJson(json)).toList();
      setState(() {
        nudges = loaded;
        isLoading = false;
      });
    } else {
      print("Failed to load nudges");
    }
  }

  Future<void> fetchInsightMessage() async {
    final response = await http.get(
      Uri.parse("${UriConstant.baseUrl}/insights"),
      headers: {"Cookie": "sessionid=$sessionId"},
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> json = jsonDecode(response.body);
      final insights = json['insights'] as List<dynamic>;

      if (insights.isNotEmpty) {
        setState(() {
          insightMessage = insights.first['message'];
        });
      }
    } else {
      print("Failed to load insights");
    }
  }

  @override
  Widget build(BuildContext context) {
    // final Color iconColor = const Color.fromARGB(255, 13, 126, 115);
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 243, 245, 246),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      SizedBox(height: 4),
                      Text(
                        "Hey Anya,",
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.black87,
                        ),
                      ),
                    ],
                  ),
                  GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => const ProfileScreen(),
                        ),
                      );
                    },
                    child: CircleAvatar(
                      radius: 26,
                      backgroundImage: AssetImage('assets/profile.avif'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 30),
              const Text(
                "Upcoming Payments",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 12),

              isLoading
                  ? Center(child: CircularProgressIndicator())
                  : Column(
                    children:
                        nudges.map((nudge) {
                          final now = DateTime.now();
                          final dueInDays = nudge.due.difference(now).inDays;

                          String dueText;
                          if (dueInDays == 0) {
                            dueText = "Due Today";
                          } else if (dueInDays == 1) {
                            dueText = "Due Tomorrow";
                          } else {
                            dueText = "Due in $dueInDays days";
                          }

                          return Padding(
                            padding: const EdgeInsets.only(bottom: 12),
                            child: _paymentCard(
                              context: context,
                              icon: Icons.monetization_on_outlined,
                              title: nudge.category,
                              amount: "₹${nudge.amount.toStringAsFixed(0)}",
                              due: dueText,
                            ),
                          );
                        }).toList(),
                  ),
              const SizedBox(height: 30),

              const Text(
                "Quick Actions",
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),
              GridView.count(
                physics: const NeverScrollableScrollPhysics(),
                shrinkWrap: true,
                crossAxisCount: 2,
                mainAxisSpacing: 20,
                crossAxisSpacing: 20,
                childAspectRatio: 1,
                children: const [
                  _QuickActionCard("Spend Trends", 'assets/trend.jpeg'),
                  _QuickActionCard("AI Chat", 'assets/chat.jpeg'),
                  _QuickActionCard(
                    "Are you this Rich?",
                    'assets/calculator.jpeg',
                  ),
                  _QuickActionCard("Voice Mode", 'assets/mic.jpeg'),
                ],
              ),
              SizedBox(height: 24),

              /// AI Insights
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  gradient: LinearGradient(
                    colors: [
                      const Color.fromARGB(255, 92, 92, 92),
                      const Color.fromARGB(255, 192, 191, 191),
                    ],
                    begin: Alignment.bottomLeft,
                    end: Alignment.topRight,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'FinSights! ✨',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 8),
                    insightMessage != null
                        ? Text(
                          insightMessage!,
                          style: TextStyle(color: Colors.white70),
                        )
                        : SizedBox(
                          height: 40,
                          child: Center(
                            child: CircularProgressIndicator(
                              color: Colors.white,
                            ),
                          ),
                        ),
                  ],
                ),
              ),
              SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _paymentCard({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String amount,
    required String due,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        color: Colors.white,
        boxShadow: [
          BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2)),
        ],
      ),
      child: Row(
        children: [
          CircleAvatar(
            backgroundColor: Colors.teal.shade50,
            child: Icon(icon, color: Colors.teal),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  "$amount • $due",
                  style: TextStyle(color: Colors.grey.shade700),
                ),
              ],
            ),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder:
                      (context) => PaymentGateway(
                        amount: double.parse(
                          amount.replaceAll('₹', '').replaceAll(',', '').trim(),
                        ),
                        category: title,
                      ),
                ),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.teal.shade100,
              foregroundColor: Colors.teal.shade900,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(20),
              ),
              elevation: 0,
            ),
            child: const Text("Pay Now"),
          ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final String label;
  final String imageAsset;
  const _QuickActionCard(this.label, this.imageAsset);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black12,
              blurRadius: 6,
              offset: Offset(0, 2),
            ),
          ],
          image: DecorationImage(
            image: AssetImage(imageAsset),
            fit: BoxFit.cover,
          ),
        ),
        alignment: Alignment.bottomLeft,
        padding: const EdgeInsets.all(12),
        child: Text(
          label,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
            color: Colors.white,
            shadows: [
              Shadow(
                color: Colors.black38,
                offset: Offset(1, 1),
                blurRadius: 3,
              ),
            ],
          ),
        ),
      ),
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (context) {
              if (label == "Spend Trends") {
                return TransactionAnalysis();
              } else if (label == "AI Chat") {
                return AIChatScreen();
              } else if (label == "Are you this Rich?") {
                return CelebrityInputScreen();
              } else if (label == "Voice Mode") {
                return Voicechat();
              }
              return HomeNavigation();
            },
          ),
        );
      },
    );
  }
}
