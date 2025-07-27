import 'package:finion/config/UriConstant.dart';
import 'package:finion/goals/Goals.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:finion/config/SessionManager.dart';

class AddGoalScreen extends StatefulWidget {
  const AddGoalScreen({Key? key}) : super(key: key);

  @override
  State<AddGoalScreen> createState() => _AddGoalScreenState();
}

class _AddGoalScreenState extends State<AddGoalScreen> {
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _monthsController = TextEditingController();
  final TextEditingController _descriptionController = TextEditingController();

  final Color primaryColor = const Color.fromARGB(255, 13, 126, 115);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add New Goal'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0.5,
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFFffffff), Color(0xFFe0f7fa)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Name of the Goal',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _nameController,
                  decoration: InputDecoration(
                    hintText: 'Eg. Europe Trip',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                const Text(
                  'Months to Achieve',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _monthsController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    hintText: 'Eg. 6',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                const Text(
                  'Describe your goal',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _descriptionController,
                  maxLines: 6,
                  decoration: InputDecoration(
                    hintText:
                        'Eg. I want to go on a 10 day Europe trip in December 2025... etc.',
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                    alignLabelWithHint: true,
                  ),
                ),
                const SizedBox(height: 312),

                Center(
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: primaryColor,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      onPressed: () async {
                        final goalName = _nameController.text.trim();
                        final months = int.tryParse(
                          _monthsController.text.trim(),
                        );
                        final description = _descriptionController.text.trim();

                        if (goalName.isEmpty ||
                            months == null ||
                            description.isEmpty) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text("Please fill all fields"),
                            ),
                          );
                          return;
                        }

                        final url = Uri.parse("${UriConstant.baseUrl}/goals");
                        final headers = {
                          'Content-Type': 'application/json',
                          'Cookie': 'sessionid=${SessionManager().sessionId}',
                        };
                        final body = jsonEncode({
                          "name": goalName,
                          "description": description,
                          "category":
                              "loan", // TODO: Make this dynamic if needed
                          "time_frame_months": months,
                        });

                        try {
                          final response = await http.post(
                            url,
                            headers: headers,
                            body: body,
                          );
                          if (response.statusCode == 200 ||
                              response.statusCode == 201) {
                            final data = jsonDecode(response.body);
                            final targetAmount = data['target_amount'] ?? 0;
                            final monthlySavings =
                                data['detailed_reasoning']['monthly_savings_needed'] ??
                                0;
                            final reasoning =
                                data['estimation_reasoning'] ?? '';

                            showDialog(
                              context: context,
                              builder:
                                  (_) => AlertDialog(
                                    backgroundColor: const Color.fromARGB(
                                      255,
                                      207,
                                      238,
                                      240,
                                    ),
                                    title: const Text(
                                      'Estimated Savings Needed',
                                      style: TextStyle(fontSize: 18),
                                    ),
                                    content: Column(
                                      mainAxisSize: MainAxisSize.min,
                                      crossAxisAlignment:
                                          CrossAxisAlignment.start,
                                      children: [
                                        Text(
                                          "Estimated Total: ₹${targetAmount.round()}",
                                        ),
                                        Text(
                                          "Monthly Needed: ₹${monthlySavings.round()}",
                                        ),
                                        const SizedBox(height: 12),
                                        Text(
                                          reasoning,
                                          style: const TextStyle(
                                            fontSize: 13,
                                            color: Color.fromARGB(
                                              255,
                                              88,
                                              87,
                                              87,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ),
                                    actions: [
                                      TextButton(
                                        onPressed: () {
                                          Navigator.pushAndRemoveUntil(
                                            context,
                                            MaterialPageRoute(
                                              builder:
                                                  (context) => GoalsScreen(),
                                            ),
                                            (route) => false,
                                          );
                                        },
                                        child: const Text('OK'),
                                      ),
                                    ],
                                  ),
                            );
                          } else {
                            throw Exception("Failed to estimate goal");
                          }
                        } catch (e) {
                          print("Error: $e");
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text("Failed to estimate goal"),
                            ),
                          );
                        }
                      },

                      child: const Text(
                        'Done',
                        style: TextStyle(fontSize: 16, color: Colors.white),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
