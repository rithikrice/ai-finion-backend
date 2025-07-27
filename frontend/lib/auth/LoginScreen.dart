import 'package:finion/config/UriConstant.dart';
import 'package:finion/homeScreen/HomeNavigation.dart';
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:finion/config/SessionManager.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _passwordVisible = false;
  TextEditingController phoneController = TextEditingController();
  bool isLoading = false;

  Future<void> login() async {
    setState(() => isLoading = true);
    final phone = phoneController.text.trim();

    final response = await http.post(
      Uri.parse("${UriConstant.baseUrl}/login"),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'phone_number': phone, 'session_id': phone}),
    );
    print('Status code: ${response.statusCode}');
    print('Response body: ${response.body}');

    setState(() => isLoading = false);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);

      if (json['success'] == true) {
        SessionManager().sessionId = json['session_id'];
        SessionManager().phoneNumber = json['phone_number'];

        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => HomeNavigation()),
        );
      } else {
        // Show error if success = false
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(json['message'] ?? 'Login failed')),
        );
      }
    } else {
      // Handle unexpected server error
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text("Server error: ${response.statusCode}")),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    var theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 6, 67, 72),
      body: ListView(
        padding: EdgeInsets.all(0),
        children: <Widget>[
          Container(
            height: MediaQuery.of(context).size.height * 3 / 8,
            child: Stack(
              children: <Widget>[
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.only(
                      bottomLeft: Radius.circular(50),
                    ),
                  ),
                ),
                Positioned(
                  top: 30,
                  left: 10,
                  child: BackButton(
                    color: theme.colorScheme.onPrimary,
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ),
                Positioned(
                  bottom: 20,
                  right: 40,
                  child: Text("LOGIN", style: TextStyle(fontSize: 36)),
                ),
              ],
            ),
          ),
          Container(
            margin: EdgeInsets.only(left: 16, right: 16, top: 16),
            child: Card(
              color: Colors.white,
              elevation: 8,
              child: Padding(
                padding: EdgeInsets.only(
                  top: 12,
                  left: 16,
                  right: 16,
                  bottom: 16,
                ),
                child: Column(
                  children: <Widget>[
                    TextFormField(
                      controller: phoneController,
                      keyboardType: TextInputType.phone,
                      style: TextStyle(
                        letterSpacing: 0.1,
                        color: theme.colorScheme.primary,
                      ),
                      decoration: InputDecoration(
                        hintText: "Phone Number",
                        hintStyle: TextStyle(
                          letterSpacing: 0.1,
                          color: theme.colorScheme.primary,
                        ),
                        prefixIcon: Icon(Icons.phone),
                      ),
                    ),

                    Container(
                      margin: EdgeInsets.only(top: 16),
                      child: TextFormField(
                        style: TextStyle(
                          letterSpacing: 0.1,
                          color: theme.colorScheme.primary,
                        ),
                        decoration: InputDecoration(
                          hintText: "Password",
                          hintStyle: TextStyle(
                            letterSpacing: 0.1,
                            color: theme.colorScheme.primary,
                          ),
                          prefixIcon: Icon(Icons.star),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _passwordVisible
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                            onPressed: () {
                              setState(() {
                                _passwordVisible = !_passwordVisible;
                              });
                            },
                          ),
                        ),

                        obscureText: _passwordVisible,
                      ),
                    ),
                    Container(
                      margin: EdgeInsets.only(top: 16),
                      alignment: Alignment.centerRight,
                      child: Text("Forgot Password ?"),
                    ),
                    Container(
                      margin: EdgeInsets.only(top: 36),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.all(Radius.circular(24)),
                        boxShadow: [
                          BoxShadow(
                            color: theme.colorScheme.shadow.withOpacity(0.1),
                            blurRadius: 3,
                            offset: Offset(0, 1),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        style: ButtonStyle(
                          backgroundColor: MaterialStateProperty.all(
                            const Color.fromARGB(255, 6, 67, 72),
                          ),
                          padding: WidgetStateProperty.all(
                            EdgeInsets.only(left: 32, right: 32),
                          ),
                        ),
                        onPressed: () {
                          if (phoneController.text.trim().isNotEmpty) {
                            login(); // Navigation handled inside this
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text("Please enter phone number"),
                              ),
                            );
                          }
                        },

                        child: Text(
                          "LOGIN",
                          style: TextStyle(
                            color: Colors.white,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Container(
            margin: EdgeInsets.only(top: 24),
            child: Center(
              child: Text(
                "OR",
                style: TextStyle(fontSize: 16, color: Colors.white),
              ),
            ),
          ),
          Container(
            margin: EdgeInsets.only(top: 16, bottom: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: <Widget>[
                InkWell(
                  splashColor: Colors.white.withAlpha(100),
                  highlightColor: theme.colorScheme.primary,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.all(Radius.circular(24)),
                      boxShadow: [
                        BoxShadow(
                          color: theme.colorScheme.primary,
                          blurRadius: 3,
                          offset: Offset(0, 1),
                        ),
                      ],
                    ),
                    padding: EdgeInsets.only(
                      left: 12,
                      right: 12,
                      // top: 8,
                      bottom: 4,
                    ),

                    child: Image.asset(
                      'assets/google.png',
                      height: 60,
                      // width: 30,
                      fit: BoxFit.fill,
                    ),
                  ),
                  onTap: () {},
                ),
              ],
            ),
          ),
          GestureDetector(
            onTap: () {
              // Navigator.pushReplacement(
              //   context,
              // MaterialPageRoute(builder: (context) => RegisterScreen()),
              // );
            },
            child: Center(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "Dont't have an Account? ",
                    style: theme.textTheme.labelSmall!.copyWith(
                      color: theme.colorScheme.onPrimary,
                    ),
                  ),

                  Text(
                    " Register",
                    style: theme.textTheme.labelSmall!.copyWith(
                      fontWeight: FontWeight.w700,
                      color: theme.colorScheme.onPrimary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
