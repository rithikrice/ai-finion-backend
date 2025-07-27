import 'package:finion/ai/CelebrityInputScreen.dart';
import 'package:finion/ai/Comparison.dart';
import 'package:finion/auth/LoginScreen.dart';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Finion',
      debugShowCheckedModeBanner: false,
      home: LoginScreen(), // Your entry screen
      routes: {
        '/compare': (context) => NetworthCompareScreen(),
        // You can still pushNamed('/compare') later
      },
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Color.fromARGB(255, 6, 67, 72),
        ),
      ),
    );
  }
}
