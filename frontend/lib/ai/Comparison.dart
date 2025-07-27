import 'package:finion/config/UriConstant.dart';
import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:finion/models/ComparisonData.dart';

class NetworthCompareScreen extends StatefulWidget {
  @override
  _NetworthCompareScreenState createState() => _NetworthCompareScreenState();
}

class _NetworthCompareScreenState extends State<NetworthCompareScreen>
    with SingleTickerProviderStateMixin {
  bool showUserCard = true;
  late AnimationController _controller;
  late Animation<double> _flipAnimation;

  UserData? userData;
  CelebrityData? celebrityData;
  Comparison? comparison;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 600),
      vsync: this,
    );
    _flipAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOutBack),
    );
  }

  // ✅ Moved argument parsing here
  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final celebrityName = ModalRoute.of(context)?.settings.arguments as String?;
    if (celebrityName != null) {
      _fetchComparison(celebrityName);
    } else {
      print('No celebrity name passed in route arguments');
    }
  }

  Future<void> _fetchComparison(String celebrityName) async {
    try {
      final response = await http.post(
        Uri.parse("${UriConstant.baseUrl}/celebrity-comparison"),
        headers: {
          'Content-Type': 'application/json',
          'Cookie': 'sessionid=8888888888',
        },
        body: jsonEncode({'celebrity_name': celebrityName}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          userData = UserData.fromJson(data['user_data']);
          celebrityData = CelebrityData.fromJson(data['celebrity_data']);
          comparison = Comparison.fromJson(data['comparison']);
        });
      } else {
        print('Error: ${response.statusCode}');
      }
    } catch (e) {
      print('Fetch failed: $e');
    }
  }

  void _toggleCard() {
    if (showUserCard) {
      _controller.forward();
    } else {
      _controller.reverse();
    }
    setState(() {
      showUserCard = !showUserCard;
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  String formatCurrency(num amount) {
    return NumberFormat.currency(locale: 'en_IN', symbol: '₹').format(amount);
  }

  Widget _buildCard({
    required String name,
    required String title,
    required num networth,
    required num monthlyIncome,
    required num investments,
    required num realEstate,
    required List<String> highlights,
    required Gradient gradient,
    required Color borderColor,
    required Icon icon,
  }) {
    return Container(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      padding: EdgeInsets.all(20),
      width: 320,
      decoration: BoxDecoration(
        gradient: gradient,
        borderRadius: BorderRadius.circular(30),
        border: Border.all(color: borderColor, width: 3),
        boxShadow: [
          BoxShadow(
            color: Colors.black38,
            blurRadius: 10,
            offset: Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          icon,
          SizedBox(height: 16),
          Text(
            name,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          Text(title, style: TextStyle(fontSize: 14, color: Colors.white70)),
          SizedBox(height: 20),
          Divider(color: Colors.white70),
          SizedBox(height: 10),
          ...[
            _infoRow("Net Worth", formatCurrency(networth)),
            _infoRow("Monthly Income", formatCurrency(monthlyIncome)),
            _infoRow("Investments", formatCurrency(investments)),
            _infoRow("Real Estate", formatCurrency(realEstate)),
          ],
          SizedBox(height: 20),
          for (final h in highlights)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 2.0),
              child: Text(
                h,
                style: TextStyle(
                  color: const Color.fromARGB(255, 241, 241, 241),
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ),
        ],
      ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.white, fontSize: 14)),
          Text(
            value,
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onHorizontalDragEnd: (details) {
        if (details.primaryVelocity != null) {
          if (details.primaryVelocity! > 0 && !showUserCard) {
            _toggleCard();
          } else if (details.primaryVelocity! < 0 && showUserCard) {
            _toggleCard();
          }
        }
      },
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: Color(0xFF111C27),
          elevation: 0,
          leading: IconButton(
            icon: Icon(Icons.arrow_back, color: Colors.white),
            onPressed:
                () => Navigator.pushAndRemoveUntil(
                  context,
                  MaterialPageRoute(builder: (context) => HomeNavigation()),
                  (route) => false,
                ),
          ),
        ),
        backgroundColor: Color(0xFF111C27),
        body: Center(
          // Ensures vertical and horizontal centering
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                "Are you this Rich?",
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              SizedBox(height: 40),
              AnimatedBuilder(
                animation: _flipAnimation,
                builder: (context, child) {
                  if (userData == null ||
                      celebrityData == null ||
                      comparison == null) {
                    return CircularProgressIndicator(); // Show loading
                  }

                  final angle = _flipAnimation.value * 3.1416;
                  return Transform(
                    alignment: Alignment.center,
                    transform: Matrix4.rotationY(angle),
                    child:
                        _flipAnimation.value <= 0.5
                            ? _buildCard(
                              name: "You",
                              title: "Aspiring Billionaire",
                              networth: userData!.netWorth,
                              monthlyIncome: userData!.monthlyIncome,
                              investments: userData!.investments,
                              realEstate: userData!.realEstate,
                              highlights: [comparison!.motivationalMessage],
                              gradient: LinearGradient(
                                colors: [
                                  const Color.fromARGB(255, 128, 72, 225),
                                  const Color.fromARGB(255, 54, 73, 179),
                                ],
                                begin: Alignment.topLeft,
                                end: Alignment.bottomRight,
                              ),
                              borderColor: Colors.yellow,
                              icon: Icon(
                                Icons.wb_sunny_rounded,
                                color: Colors.white,
                                size: 80,
                              ),
                            )
                            : Transform(
                              alignment: Alignment.center,
                              transform: Matrix4.rotationY(3.1416),
                              child: _buildCard(
                                name: celebrityData!.name,
                                title: "Someone richer than you!",
                                networth: celebrityData!.netWorth,
                                monthlyIncome: celebrityData!.monthlyIncome,
                                investments: celebrityData!.investments,
                                realEstate: celebrityData!.realEstate,
                                highlights: [
                                  "Income: ${celebrityData!.primaryIncomeSources.join(', ')}",
                                  "Source: ${celebrityData!.dataSource}",
                                  "Updated: ${celebrityData!.lastUpdated}",
                                ],
                                gradient: LinearGradient(
                                  colors: [
                                    Colors.orangeAccent,
                                    Colors.redAccent,
                                  ],
                                  begin: Alignment.topLeft,
                                  end: Alignment.bottomRight,
                                ),
                                borderColor: Colors.yellow,
                                icon: Icon(
                                  Icons.star,
                                  color: Colors.white,
                                  size: 80,
                                ),
                              ),
                            ),
                  );
                },
              ),

              SizedBox(height: 24),
              GestureDetector(
                onTap: _toggleCard,
                child: Container(
                  width: 90,
                  height: 90,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white,
                    border: Border.all(color: Colors.black, width: 3),
                  ),
                  child: Center(
                    child: Text(
                      "VS",
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.black,
                      ),
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
