// import 'package:flutter/material.dart';
// import 'package:fl_chart/fl_chart.dart';

// void main() {
//   runApp(MyApp());
// }

// class MyApp extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       debugShowCheckedModeBanner: false,
//       home: SpendingScreen(),
//     );
//   }
// }

// class SpendingScreen extends StatelessWidget {
//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       appBar: AppBar(
//         title: Text('Spending'),
//         centerTitle: true,
//         backgroundColor: Colors.white,
//         elevation: 0,
//         foregroundColor: Colors.black,
//       ),
//       body: SingleChildScrollView(
//         padding: EdgeInsets.all(16),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             Row(
//               mainAxisAlignment: MainAxisAlignment.spaceBetween,
//               children: [
//                 FilterChip(label: Text("Last 30 days"), onSelected: (_) {}),
//                 FilterChip(label: Text("All categories"), onSelected: (_) {}),
//               ],
//             ),
//             SizedBox(height: 20),

//             // Daily Spending
//             SpendingCard(
//               title: 'Daily spending',
//               amount: '₹1,234',
//               trend: '+12%',
//               trendColor: Colors.green,
//               chart: LineChart(
//                 LineChartData(
//                   titlesData: FlTitlesData(show: false),
//                   lineBarsData: [
//                     LineChartBarData(
//                       spots: [
//                         FlSpot(0, 1),
//                         FlSpot(1, 1.5),
//                         FlSpot(2, 1),
//                         FlSpot(3, 1.7),
//                         FlSpot(4, 0.7),
//                         FlSpot(5, 2),
//                         FlSpot(6, 1.8),
//                       ],
//                       isCurved: true,
//                       colors: [Colors.black],
//                       barWidth: 2,
//                       dotData: FlDotData(show: false),
//                     ),
//                   ],
//                   borderData: FlBorderData(show: false),
//                   gridData: FlGridData(show: false),
//                 ),
//               ),
//             ),
//             SizedBox(height: 20),

//             // Spending by category
//             SpendingCard(
//               title: 'Spending by category',
//               amount: '₹567',
//               trend: '-5%',
//               trendColor: Colors.red,
//               chart: BarChart(
//                 BarChartData(
//                   alignment: BarChartAlignment.spaceAround,
//                   titlesData: FlTitlesData(show: false),
//                   borderData: FlBorderData(show: false),
//                   barGroups: [
//                     BarChartGroupData(
//                       x: 0,
//                       barRods: [BarChartRodData(toY: 4, color: Colors.grey)],
//                     ),
//                     BarChartGroupData(
//                       x: 1,
//                       barRods: [BarChartRodData(toY: 2, color: Colors.grey)],
//                     ),
//                     BarChartGroupData(
//                       x: 2,
//                       barRods: [BarChartRodData(toY: 1, color: Colors.grey)],
//                     ),
//                     BarChartGroupData(
//                       x: 3,
//                       barRods: [BarChartRodData(toY: 6, color: Colors.grey)],
//                     ),
//                   ],
//                 ),
//               ),
//             ),
//             SizedBox(height: 20),

//             // Spending by date
//             SpendingCard(
//               title: 'Spending by date',
//               amount: '₹890',
//               trend: '+8%',
//               trendColor: Colors.green,
//               chart: Column(
//                 children: [
//                   for (var entry in [
//                     'Jan',
//                     'Feb',
//                     'Mar',
//                     'Apr',
//                     'May',
//                     'Jun',
//                     'Jul',
//                   ])
//                     Padding(
//                       padding: const EdgeInsets.symmetric(vertical: 4.0),
//                       child: Row(
//                         children: [
//                           SizedBox(width: 50, child: Text(entry)),
//                           Expanded(
//                             child: Container(
//                               height: 8,
//                               color: Colors.grey[300],
//                               child: FractionallySizedBox(
//                                 widthFactor:
//                                     entry == 'Jan'
//                                         ? 1.0
//                                         : entry == 'Feb'
//                                         ? 0.2
//                                         : entry == 'Mar'
//                                         ? 0.3
//                                         : entry == 'Apr'
//                                         ? 0.3
//                                         : entry == 'May'
//                                         ? 0.9
//                                         : entry == 'Jun'
//                                         ? 0.7
//                                         : 0.6,
//                                 alignment: Alignment.centerLeft,
//                                 child: Container(color: Colors.black),
//                               ),
//                             ),
//                           ),
//                         ],
//                       ),
//                     ),
//                 ],
//               ),
//             ),
//             SizedBox(height: 20),

//             // AI Insights
//             Container(
//               padding: EdgeInsets.all(16),
//               decoration: BoxDecoration(
//                 borderRadius: BorderRadius.circular(12),
//                 gradient: LinearGradient(
//                   colors: [Colors.grey.shade800, Colors.grey.shade400],
//                   begin: Alignment.bottomCenter,
//                   end: Alignment.topCenter,
//                 ),
//               ),
//               child: Column(
//                 crossAxisAlignment: CrossAxisAlignment.start,
//                 children: [
//                   Text(
//                     'AI Insights',
//                     style: TextStyle(
//                       color: Colors.white,
//                       fontSize: 16,
//                       fontWeight: FontWeight.bold,
//                     ),
//                   ),
//                   SizedBox(height: 8),
//                   Text(
//                     'Your spending on dining out increased by 15% compared to the previous month.\nConsider setting a budget for this category to manage your expenses better.',
//                     style: TextStyle(color: Colors.white70),
//                   ),
//                 ],
//               ),
//             ),
//           ],
//         ),
//       ),
//       bottomNavigationBar: BottomNavigationBar(
//         currentIndex: 1,
//         selectedItemColor: Colors.black,
//         unselectedItemColor: Colors.grey,
//         showUnselectedLabels: true,
//         items: [
//           BottomNavigationBarItem(
//             icon: Icon(Icons.dashboard),
//             label: 'Overview',
//           ),
//           BottomNavigationBarItem(
//             icon: Icon(Icons.list),
//             label: 'Transactions',
//           ),
//           BottomNavigationBarItem(
//             icon: Icon(Icons.auto_awesome),
//             label: 'AI Mode',
//           ),
//           BottomNavigationBarItem(icon: Icon(Icons.flag), label: 'Goals'),
//           BottomNavigationBarItem(icon: Icon(Icons.person), label: 'Profile'),
//         ],
//       ),
//     );
//   }
// }

// class SpendingCard extends StatelessWidget {
//   final String title;
//   final String amount;
//   final String trend;
//   final Color trendColor;
//   final Widget chart;

//   const SpendingCard({
//     required this.title,
//     required this.amount,
//     required this.trend,
//     required this.trendColor,
//     required this.chart,
//   });

//   @override
//   Widget build(BuildContext context) {
//     return Card(
//       elevation: 2,
//       shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
//       child: Padding(
//         padding: const EdgeInsets.all(16.0),
//         child: Column(
//           crossAxisAlignment: CrossAxisAlignment.start,
//           children: [
//             Text(
//               title,
//               style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
//             ),
//             SizedBox(height: 8),
//             Row(
//               mainAxisAlignment: MainAxisAlignment.spaceBetween,
//               children: [
//                 Text(
//                   amount,
//                   style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
//                 ),
//                 Text(trend, style: TextStyle(color: trendColor)),
//               ],
//             ),
//             SizedBox(height: 16),
//             SizedBox(height: 150, child: chart),
//           ],
//         ),
//       ),
//     );
//   }
// }
