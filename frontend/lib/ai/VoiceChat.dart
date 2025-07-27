import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:flutter/material.dart';
import 'package:lottie/lottie.dart';

class Voicechat extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFabdbcc), Color(0xFF1db193)],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              const SizedBox(height: 40),
              const Text(
                "AI Voice Chat",
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                "04:37",
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.black45,
                  letterSpacing: 2,
                ),
              ),
              const Spacer(),

              Container(
                height: 340,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.white.withOpacity(0.2),
                  border: Border.all(color: Colors.white70, width: 2),
                ),
                child: Center(
                  child: Lottie.asset(
                    'assets/voiceChat.json',
                    height: 300,
                    repeat: true,
                    fit: BoxFit.contain,
                  ),
                ),
              ),
              const Spacer(),
              Padding(
                padding: const EdgeInsets.only(bottom: 40),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildIconButton(
                      Icons.mic,
                      Colors.greenAccent.shade400,
                      context,
                    ),
                    _buildIconButton(Icons.call_end, Colors.redAccent, context),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildIconButton(IconData icon, Color color, BuildContext context) {
    return Container(
      width: 60,
      height: 60,
      decoration: BoxDecoration(color: color, shape: BoxShape.circle),
      child: IconButton(
        icon: Icon(icon, color: Colors.white),
        onPressed:
            () => {
              Navigator.pushAndRemoveUntil(
                context,
                MaterialPageRoute(builder: (context) => HomeNavigation()),
                (route) => false,
              ),
            },
      ),
    );
  }
}
