import 'package:finion/config/SessionManager.dart';
import 'package:finion/models/DailySpend.dart';
import 'package:finion/models/ExpenseCategory.dart';
import 'package:finion/transactions/Transactions.dart';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:finion/config/UriConstant.dart';

class TransactionAnalysis extends StatefulWidget {
  @override
  _TransactionAnalysisState createState() => _TransactionAnalysisState();
}

class _TransactionAnalysisState extends State<TransactionAnalysis>
    with SingleTickerProviderStateMixin {
  final sessionId = SessionManager().sessionId;

  DateTime fromDate = DateTime(2024, 6, 1);
  DateTime toDate = DateTime(2024, 7, 31);

  List<ExpenseCategory> apiExpenses = [];
  List<DailySpend> dailySpending = [];

  bool isLoading = false;

  late AnimationController _animationController;
  late Animation<double> _radiusAnimation;

  @override
  void initState() {
    super.initState();

    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );

    _radiusAnimation = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );

    _animationController.forward();
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<List<ExpenseCategory>> fetchExpenses() async {
    final from = DateFormat('yyyy-MM-dd').format(fromDate);
    final to = DateFormat('yyyy-MM-dd').format(toDate);

    final response = await http.get(
      Uri.parse(
        "${UriConstant.baseUrl}/spend_by_category?from_date=$from&to_date=$to",
      ),
      headers: {"Cookie": "sessionid=$sessionId"},
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final breakdown = List<Map<String, dynamic>>.from(data['breakdown']);
      return breakdown.map((e) => ExpenseCategory.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load expense data');
    }
  }

  Future<List<DailySpend>> fetchDailySpending() async {
    final from = DateFormat('yyyy-MM-dd').format(fromDate);
    final to = DateFormat('yyyy-MM-dd').format(toDate);

    final response = await http.get(
      Uri.parse(
        "${UriConstant.baseUrl}/spend_daily?from_date=$from&to_date=$to",
      ),
      headers: {"Cookie": "sessionid=$sessionId"},
    );

    if (response.statusCode == 200) {
      final List<dynamic> jsonData = json.decode(response.body);
      return jsonData.map((e) => DailySpend.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load daily spending');
    }
  }

  Future<void> _selectDate(BuildContext context, bool isFrom) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: isFrom ? fromDate : toDate,
      firstDate: DateTime(2020),
      lastDate: DateTime(2030),
      builder: (context, child) {
        return Theme(
          data: Theme.of(
            context,
          ).copyWith(colorScheme: ColorScheme.light(onPrimary: Colors.white)),
          child: child!,
        );
      },
    );
    if (picked != null) {
      setState(() {
        if (isFrom) {
          fromDate = picked;
        } else {
          toDate = picked;
        }
      });
    }
  }

  final List<Map<String, dynamic>> iconColorMap = [
    {
      "gradient": [Color(0xFF36D1DC), Color.fromARGB(255, 55, 94, 176)],
      "icon": Icons.account_balance_wallet,
    },
    {
      "gradient": [Color(0xFFFF416C), Color.fromARGB(255, 151, 45, 26)],
      "icon": Icons.home,
    },
    {
      "gradient": [Color(0xFF56ab2f), Color.fromARGB(255, 100, 139, 52)],
      "icon": Icons.trending_up,
    },
    {
      "gradient": [Color(0xFFDA22FF), Color.fromARGB(255, 70, 23, 111)],
      "icon": Icons.shopping_bag,
    },
    {
      "gradient": [Color(0xFF614385), Color.fromARGB(255, 56, 79, 142)],
      "icon": Icons.movie,
    },
    {
      "gradient": [Color(0xFFFFB75E), Color.fromARGB(255, 111, 74, 18)],
      "icon": Icons.category,
    },
  ];

  List<_ExpenseData> get mappedExpenses {
    return apiExpenses.map((e) {
      final colorIndex = apiExpenses.indexOf(e) % iconColorMap.length;
      final color = iconColorMap[colorIndex];

      return _ExpenseData(
        e.category,
        e.amount.toInt(),
        e.percentage,
        color['gradient']!,
        color['icon']!,
      );
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd/MM/yyyy');
    int touchedIndex = -1;

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text('Spending', style: TextStyle(color: Colors.black)),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    readOnly: true,
                    onTap: () => _selectDate(context, true),
                    controller: TextEditingController(
                      text: dateFormat.format(fromDate),
                    ),
                    decoration: InputDecoration(
                      labelText: 'From',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: TextFormField(
                    readOnly: true,
                    onTap: () => _selectDate(context, false),
                    controller: TextEditingController(
                      text: dateFormat.format(toDate),
                    ),
                    decoration: InputDecoration(
                      labelText: 'To',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ],
            ),
            SizedBox(height: 20),
            Container(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () async {
                  setState(() => isLoading = true);
                  try {
                    final expenseData = await fetchExpenses();
                    final dailyData = await fetchDailySpending();
                    setState(() {
                      apiExpenses = expenseData;
                      dailySpending = dailyData;
                      isLoading = false;
                    });
                  } catch (e) {
                    debugPrint(' Error: $e');
                    debugPrint(' Stacktrace: $e');
                    setState(() => isLoading = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('Failed to load data')),
                    );
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Analyze',
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),
            SizedBox(height: 12),
            Container(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => Transactions()),
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
                  'All Transactions',
                  style: TextStyle(color: Colors.white, fontSize: 16),
                ),
              ),
            ),
            SizedBox(height: 16),
            Center(
              child: SizedBox(
                height: 360,
                child: AnimatedBuilder(
                  animation: _radiusAnimation,
                  builder: (context, child) {
                    return PieChart(
                      PieChartData(
                        pieTouchData: PieTouchData(
                          touchCallback: (event, response) {
                            setState(() {
                              touchedIndex =
                                  response
                                      ?.touchedSection
                                      ?.touchedSectionIndex ??
                                  -1;
                            });
                          },
                        ),
                        startDegreeOffset: 180,
                        sectionsSpace: 4,
                        centerSpaceRadius: 6,
                        sections: List.generate(mappedExpenses.length, (index) {
                          final e = mappedExpenses[index];
                          final isTouched = index == touchedIndex;
                          final baseRadius = isTouched ? 180.0 : 150.0;

                          return PieChartSectionData(
                            value: e.percent,
                            title: '${e.percent}%',
                            radius: baseRadius * _radiusAnimation.value,
                            titleStyle: TextStyle(
                              fontSize: isTouched ? 18 : 14,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                            gradient: LinearGradient(
                              colors: e.gradientColors,
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                          );
                        }),
                      ),
                    );
                  },
                ),
              ),
            ),
            SizedBox(height: 24),
            dailySpending.isEmpty
                ? Container()
                : Text(
                  "Details",
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 16),
                ),
            SizedBox(height: 10),
            Column(
              children:
                  mappedExpenses.map((e) {
                    return Column(
                      children: [
                        ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: CircleAvatar(
                            backgroundColor: e.gradientColors[0].withOpacity(
                              0.1,
                            ),
                            child: Icon(e.icon, color: e.gradientColors[0]),
                          ),
                          title: Text(
                            e.name,
                            style: TextStyle(fontWeight: FontWeight.w500),
                          ),
                          subtitle: Text(
                            "${(e.amount / 100).round()} transactions",
                            style: TextStyle(
                              fontSize: 13,
                              color: Colors.grey[600],
                            ),
                          ),
                          trailing: Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                " ₹${e.amount}",
                                style: TextStyle(
                                  color: Colors.red,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                "${e.percent}%",
                                style: TextStyle(
                                  fontSize: 12,
                                  color: Colors.grey,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Divider(color: Colors.grey.shade200),
                      ],
                    );
                  }).toList(),
            ),
            dailySpending.isEmpty
                ? Container()
                : SpendingCard(
                  title: 'Daily spending',
                  chart: LineChartWidget(data: dailySpending),
                ),
          ],
        ),
      ),
    );
  }
}

class FilterChipWidget extends StatelessWidget {
  final String label;
  const FilterChipWidget({required this.label});

  @override
  Widget build(BuildContext context) {
    return Chip(label: Text(label), backgroundColor: Colors.grey[200]);
  }
}

class SpendingCard extends StatelessWidget {
  final String title;
  final Widget chart;

  const SpendingCard({required this.title, required this.chart});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      color: const Color.fromARGB(255, 236, 249, 250),
      elevation: 1,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 12),
            SizedBox(height: 240, child: chart),
          ],
        ),
      ),
    );
  }
}

class LineChartWidget extends StatelessWidget {
  final List<DailySpend> data;

  const LineChartWidget({required this.data});

  @override
  Widget build(BuildContext context) {
    if (data.isEmpty) {
      return Center(child: Text("No data"));
    }

    final spots =
        data
            .asMap()
            .entries
            .map((entry) => FlSpot(entry.key.toDouble(), entry.value.amount))
            .toList();

    final maxAmount = data.map((e) => e.amount).reduce((a, b) => a > b ? a : b);

    return LineChart(
      LineChartData(
        titlesData: FlTitlesData(
          show: true,
          bottomTitles: AxisTitles(
            axisNameWidget: Text(
              'Date',
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
            ),
            sideTitles: SideTitles(
              showTitles: true,
              interval: (data.length / 5).floorToDouble(),
              getTitlesWidget: (value, meta) {
                int index = value.toInt();
                if (index < 0 || index >= data.length) return const SizedBox();
                return SideTitleWidget(
                  axisSide: meta.axisSide,
                  child: Text(
                    DateFormat('dd').format(data[index].date),
                    style: const TextStyle(fontSize: 10),
                  ),
                );
              },
              reservedSize: 30,
            ),
          ),
          leftTitles: AxisTitles(
            // axisNameWidget: Text(
            //   'Amount',
            //   style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
            // ),
            sideTitles: SideTitles(
              showTitles: true,
              interval: maxAmount / 6,
              getTitlesWidget: (value, meta) {
                return Text(
                  '₹${value.toInt()}',
                  style: const TextStyle(fontSize: 10),
                );
              },
              reservedSize: 40,
            ),
          ),
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: FlGridData(show: true),
        borderData: FlBorderData(
          show: true,
          border: const Border(left: BorderSide(), bottom: BorderSide()),
        ),
        lineBarsData: [
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: const Color.fromARGB(255, 6, 67, 72),
            barWidth: 3,
            dotData: FlDotData(show: false),
          ),
        ],
        minY: 0,
        maxY: maxAmount + 500,
      ),
    );
  }
}

class _ExpenseData {
  final String name;
  final int amount;
  final double percent;
  final List<Color> gradientColors;
  final IconData icon;

  _ExpenseData(
    this.name,
    this.amount,
    this.percent,
    this.gradientColors,
    this.icon,
  );
}
