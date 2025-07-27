import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class PaymentSuccessScreen extends StatelessWidget {
  const PaymentSuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFe0f7fa), Color(0xFFffffff)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        width: double.infinity,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Lottie.asset(
              'assets/PaymentDone.json',
              height: 250,
              repeat: false,
              fit: BoxFit.contain,
            ),

            const SizedBox(height: 40),

            const Text(
              'Payment Successful!',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: const Color.fromARGB(255, 6, 67, 72), // darker green
                letterSpacing: 1.2,
              ),
            ),

            const SizedBox(height: 15),

            const Text(
              "Thank you for your payment.",
              style: TextStyle(fontSize: 16, color: Colors.black87),
            ),

            const SizedBox(height: 50),

            // Done button with glow
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 40),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (context) => HomeNavigation()),
                    (route) => false,
                  );
                },
                style: ElevatedButton.styleFrom(
                  elevation: 10,
                  backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  textStyle: const TextStyle(fontSize: 18),
                  shadowColor: Colors.greenAccent,
                ),
                child: const Center(child: Text("Done")),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
