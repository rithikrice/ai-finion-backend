import 'package:finion/config/SessionManager.dart';
import 'package:finion/payement/PaymentSuccessful.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:finion/config/UriConstant.dart';

class PaymentGateway extends StatefulWidget {
  final double amount;
  final String category;

  const PaymentGateway({Key? key, required this.amount, required this.category})
    : super(key: key);

  @override
  State<PaymentGateway> createState() => _PaymentGatewayState();
}

class _PaymentGatewayState extends State<PaymentGateway> {
  String selectedMethod = '';
  bool paymentDetailsEntered = false;
  bool isProcessing = false;

  @override
  Widget build(BuildContext context) {
    final themeColor = const Color.fromARGB(255, 6, 67, 72);
    return Scaffold(
      appBar: AppBar(
        backgroundColor: themeColor,
        foregroundColor: Colors.white,
        title: Text("Choose Payment Method"),
        centerTitle: true,
      ),
      backgroundColor: Colors.white,
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            _amountCard(themeColor),
            SizedBox(height: 20),
            _paymentOption(
              label: "UPI",
              icon: Icons.qr_code,
              method: "upi",
              themeColor: themeColor,
            ),
            if (selectedMethod == "upi") _upiSection(),
            _paymentOption(
              label: "Credit / Debit Card",
              icon: Icons.credit_card,
              method: "card",
              themeColor: themeColor,
            ),
            if (selectedMethod == "card") _cardSection(),
            _paymentOption(
              label: "Netbanking",
              icon: Icons.account_balance,
              method: "netbanking",
              themeColor: themeColor,
            ),
            if (selectedMethod == "netbanking") _netbankingSection(),
            Spacer(),
            Container(
              margin: EdgeInsets.only(bottom: 60),
              child: ElevatedButton.icon(
                icon:
                    isProcessing
                        ? SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            color: Colors.white,
                            strokeWidth: 2,
                          ),
                        )
                        : Icon(Icons.lock),
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                      selectedMethod.isEmpty || isProcessing
                          ? Colors.grey.shade300
                          : themeColor,
                  padding: EdgeInsets.symmetric(horizontal: 40, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                onPressed:
                    selectedMethod.isEmpty || isProcessing
                        ? null
                        : () async {
                          setState(() => isProcessing = true);
                          final success = await deleteNudge(widget.category);
                          setState(() => isProcessing = false);

                          if (success) {
                            Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                builder: (context) => PaymentSuccessScreen(),
                              ),
                            );
                          } else {
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text("Failed to remove nudge")),
                            );
                          }
                        },
                label: Text(
                  "Pay ₹${widget.amount.toStringAsFixed(2)}",
                  style: TextStyle(fontSize: 16, color: Colors.white),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<bool> deleteNudge(String category) async {
    final encodedCategory = Uri.encodeComponent(category);
    final url = Uri.parse("${UriConstant.baseUrl}/nudges/$encodedCategory");

    final response = await http.delete(
      url,
      headers: {"Cookie": "sessionid=${SessionManager().sessionId}"},
    );

    if (response.statusCode == 200) {
      final body = response.body;
      return body.contains('"success":true');
    }
    return false;
  }

  Widget _amountCard(Color themeColor) {
    return Card(
      color: Colors.grey.shade50,
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            Icon(Icons.account_balance_wallet, size: 40, color: themeColor),
            SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "Total Amount",
                  style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                ),
                Text(
                  "₹${widget.amount.toStringAsFixed(2)}",
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _paymentOption({
    required String label,
    required IconData icon,
    required String method,
    required Color themeColor,
  }) {
    final isSelected = selectedMethod == method;
    return GestureDetector(
      onTap: () {
        setState(() {
          selectedMethod = method;
          paymentDetailsEntered = false;
        });
      },
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color:
              isSelected ? themeColor.withOpacity(0.1) : Colors.grey.shade100,
          border: Border.all(
            color: isSelected ? themeColor : Colors.grey.shade300,
          ),
          borderRadius: BorderRadius.circular(12),
        ),
        child: ListTile(
          leading: Icon(icon, color: themeColor),
          title: Text(
            label,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500),
          ),
          trailing: Icon(
            Icons.arrow_forward_ios_rounded,
            size: 16,
            color: Colors.grey.shade600,
          ),
        ),
      ),
    );
  }

  Widget _upiSection() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: TextField(
        decoration: InputDecoration(
          hintText: "Enter UPI ID",
          prefixIcon: Icon(Icons.alternate_email),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        onChanged: (_) => setState(() => paymentDetailsEntered = true),
      ),
    );
  }

  Widget _cardSection() {
    return Column(
      children: [
        TextField(
          decoration: InputDecoration(
            hintText: "Card Number",
            prefixIcon: Icon(Icons.credit_card),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
          ),
          onChanged: (_) => setState(() => paymentDetailsEntered = true),
        ),
        SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "MM/YY",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                onChanged: (_) => setState(() => paymentDetailsEntered = true),
              ),
            ),
            SizedBox(width: 10),
            Expanded(
              child: TextField(
                decoration: InputDecoration(
                  hintText: "CVV",
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                onChanged: (_) => setState(() => paymentDetailsEntered = true),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _netbankingSection() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: DropdownButtonFormField<String>(
        decoration: InputDecoration(
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
        ),
        hint: Text("Select your bank"),
        items:
            ["HDFC", "SBI", "ICICI", "Axis", "Kotak"]
                .map((bank) => DropdownMenuItem(value: bank, child: Text(bank)))
                .toList(),
        onChanged: (_) => setState(() => paymentDetailsEntered = true),
      ),
    );
  }
}
