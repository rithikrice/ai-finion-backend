import 'package:finion/config/SessionManager.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:finion/config/UriConstant.dart';

class AIChatScreen extends StatefulWidget {
  @override
  _AIChatScreenState createState() => _AIChatScreenState();
}

class _AIChatScreenState extends State<AIChatScreen> {
  final sessionId = SessionManager().sessionId;

  final TextEditingController _controller = TextEditingController();
  final List<Map<String, dynamic>> _messages = [
    {
      "sender": "Finion",
      "message":
          "Hi there! I'm Finion, your personal finance assistant. How can I help you today?",
      "isUser": false,
    },
  ];

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;

    setState(() {
      _messages.add({"sender": "You", "message": text, "isUser": true});
    });

    _controller.clear();

    try {
      final response = await http.post(
        Uri.parse("${UriConstant.baseUrl}/ask-ai"),
        headers: {
          "Content-Type": "application/json",
          "Cookie": "sessionid=$sessionId",
        },
        body: json.encode({"query": text}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final reply = data['response'] ?? "I'm not sure how to answer that.";

        setState(() {
          _messages.add({
            "sender": "Finion",
            "message": reply,
            "isUser": false,
          });
        });
      } else {
        setState(() {
          _messages.add({
            "sender": "Finion",
            "message": "Sorry, something went wrong.",
            "isUser": false,
          });
        });
      }
    } catch (e) {
      setState(() {
        _messages.add({
          "sender": "Finion",
          "message": "An error occurred: $e",
          "isUser": false,
        });
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      resizeToAvoidBottomInset: true,
      appBar: AppBar(
        leading: BackButton(color: Colors.black),
        backgroundColor: Colors.white,
        elevation: 0,
        title: Text(
          "Finion",
          style: TextStyle(color: Colors.black, fontWeight: FontWeight.w600),
        ),
        centerTitle: true,
      ),
      backgroundColor: Colors.white,
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFffffff), Color(0xFFe0f7fa)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final msg = _messages[index];
                    return Align(
                      alignment:
                          msg["isUser"]
                              ? Alignment.centerRight
                              : Alignment.centerLeft,
                      child: Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          mainAxisAlignment:
                              msg["isUser"]
                                  ? MainAxisAlignment.end
                                  : MainAxisAlignment.start,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (!msg["isUser"]) ...[
                              CircleAvatar(
                                radius: 18,
                                backgroundImage: AssetImage(
                                  'assets/aiProfile.png',
                                ),
                              ),
                              SizedBox(width: 8),
                            ],
                            Flexible(
                              child: Container(
                                padding: EdgeInsets.symmetric(
                                  horizontal: 14,
                                  vertical: 10,
                                ),
                                decoration: BoxDecoration(
                                  color:
                                      msg["isUser"]
                                          ? Colors.blue.shade50
                                          : Colors.grey.shade100,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Text(
                                  msg["message"],
                                  style: TextStyle(fontSize: 15),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              Container(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  border: Border(top: BorderSide(color: Colors.grey.shade200)),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _controller,
                            decoration: InputDecoration(
                              hintText: "Ask me about your money",
                              hintStyle: TextStyle(color: Colors.grey),
                              filled: true,
                              fillColor: Colors.grey.shade100,
                              contentPadding: EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 14,
                              ),
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(24),
                                borderSide: BorderSide.none,
                              ),
                            ),
                            onChanged: (_) => setState(() {}),
                            onSubmitted: (_) => _sendMessage(),
                          ),
                        ),
                        SizedBox(width: 10),
                        IconButton(
                          icon: Icon(Icons.mic, color: Colors.grey.shade700),
                          onPressed: () {},
                        ),
                        IconButton(
                          icon: Icon(
                            Icons.send,
                            color:
                                _controller.text.trim().isEmpty
                                    ? Colors.grey.shade400
                                    : Colors.blue,
                          ),
                          onPressed:
                              _controller.text.trim().isEmpty
                                  ? null
                                  : _sendMessage,
                        ),
                      ],
                    ),
                    SizedBox(height: 4),
                    Text(
                      "Powered by Gemini 1.5 Flash",
                      style: TextStyle(fontSize: 12, color: Colors.grey),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
