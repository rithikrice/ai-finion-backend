import 'package:finion/config/SessionManager.dart';
import 'package:finion/config/UriConstant.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';

class Transactions extends StatefulWidget {
  @override
  _TransactionsState createState() => _TransactionsState();
}

class _TransactionsState extends State<Transactions> {
  double totalExpenses = 0;
  double balanceAmount = 0;
  List<dynamic> transactions = [];

  String _selectedTransactionCategory = 'Groceries';
  String _selectedTransactionType = 'Debit';
  DateTime _selectedDate = DateTime.now();

  bool isLoading = false;
  final sessionId = SessionManager().sessionId;

  DateTime fromDate = DateTime(2024, 6, 1);
  DateTime toDate = DateTime(2024, 7, 31);

  final _transactionCategories = [
    'Groceries',
    'Health',
    'Food',
    'Travel',
    'Shopping',
    'Savings',
    'Investment',
    'Transfer',
    'Credit Card Payment',
    'Others',
    'Bills',
    'Entertainment',
  ];

  final _transactionTypes = ['Debit', 'Credit'];

  final _titleController = TextEditingController();
  final _amountController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadTransactions(); // fetch when screen opens
  }

  Future<void> _loadTransactions() async {
    setState(() => isLoading = true);

    final fromDateStr = DateFormat('yyyy-MM-dd').format(fromDate);
    final toDateStr = DateFormat('yyyy-MM-dd').format(toDate);

    final headers = {'Cookie': 'sessionid=${SessionManager().sessionId}'};

    try {
      // Summary API
      final summaryRes = await http.get(
        Uri.parse(
          '${UriConstant.baseUrl}/transactions/summary?from_date=$fromDateStr&to_date=$toDateStr',
        ),
        headers: headers,
      );

      if (summaryRes.statusCode == 200) {
        final data = jsonDecode(summaryRes.body);
        totalExpenses = data['total_expenses'];
        balanceAmount = data['balance'];
      }

      // Transactions API
      final txnRes = await http.get(
        Uri.parse(
          '${UriConstant.baseUrl}/transactions?from_date=$fromDateStr&to_date=$toDateStr',
        ),
        headers: headers,
      );

      if (txnRes.statusCode == 200) {
        setState(() {
          transactions = jsonDecode(txnRes.body);
        });
      } else {
        throw Exception("Transaction list failed: ${txnRes.statusCode}");
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to load transactions: $e')),
      );
    } finally {
      setState(() => isLoading = false);
    }
  }

  void _showFormatDialog() {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: Text('Choose File Format'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: Icon(Icons.description),
                  title: Text('CSV'),
                  onTap: () {
                    Navigator.pop(context);
                    downloadReport('csv');
                  },
                ),
                ListTile(
                  leading: Icon(Icons.code),
                  title: Text('JSON'),
                  onTap: () {
                    Navigator.pop(context);
                    downloadReport('json');
                  },
                ),
              ],
            ),
          ),
    );
  }

  Future<void> downloadReport(String format) async {
    final url = Uri.parse("${UriConstant.baseUrl}/export/data?format=$format");
    final headers = {'Cookie': 'sessionid=${SessionManager().sessionId}'};

    try {
      // Request storage permission
      final status = await Permission.manageExternalStorage.request();
      if (!status.isGranted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Manage external storage permission is required.'),
          ),
        );
        return;
      }

      final response = await http.get(url, headers: headers);

      if (response.statusCode == 200) {
        final directory = await getExternalStorageDirectory();
        final path = directory?.path ?? '/storage/emulated/0/Download';
        final file = File('$path/report.$format');

        await file.writeAsBytes(response.bodyBytes);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Report downloaded to: ${file.path}')),
        );
        setState(() => isLoading = false);
      } else {
        throw Exception('Failed to download report');
      }
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Download failed: $e')));
    }
  }

  Map<String, List<dynamic>> _groupTransactionsByDate(List<dynamic> txns) {
    Map<String, List<dynamic>> grouped = {};

    for (var txn in txns) {
      final date = txn['date'];
      if (!grouped.containsKey(date)) {
        grouped[date] = [];
      }
      grouped[date]!.add(txn);
    }

    return grouped;
  }

  Widget _buildTransactionSectionGrouped(
    String dateStr,
    double totalAmount,
    List<dynamic> txns,
  ) {
    final dateLabel = DateFormat('dd MMM yyyy').format(DateTime.parse(dateStr));

    return Card(
      color: const Color.fromARGB(255, 233, 242, 242),
      margin: EdgeInsets.symmetric(vertical: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(dateLabel, style: TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  totalAmount < 0
                      ? '- ₹${totalAmount.abs().toStringAsFixed(0)}'
                      : '+ ₹${totalAmount.toStringAsFixed(0)}',
                  style:
                      totalAmount < 0
                          ? TextStyle(color: Colors.red)
                          : TextStyle(color: Colors.green),
                ),
              ],
            ),
            Divider(),
            ...txns.map((txn) {
              return _buildTransactionItem(
                Icons.currency_rupee,
                txn['narration'],
                txn['category'],
                (txn['amount'] as num).toDouble(),
                txn['txn_type'] == 'DEBIT' ? Colors.red : Colors.green,
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  void _showAddExpensePopup() {
    showModalBottomSheet(
      context: context,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder:
          (context) => Padding(
            padding: EdgeInsets.fromLTRB(
              20,
              20,
              20,
              MediaQuery.of(context).viewInsets.bottom + 20,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Add Expense',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 10),
                TextField(
                  controller: _titleController,
                  decoration: InputDecoration(labelText: 'Title'),
                ),
                TextField(
                  controller: _amountController,
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(labelText: 'Amount (₹)'),
                ),
                SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: _selectedTransactionCategory,
                  items:
                      _transactionCategories
                          .map(
                            (cat) =>
                                DropdownMenuItem(value: cat, child: Text(cat)),
                          )
                          .toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedTransactionCategory = value!;
                    });
                  },
                  decoration: InputDecoration(labelText: 'Category'),
                ),
                SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  value: _selectedTransactionType,
                  items:
                      _transactionTypes
                          .map(
                            (type) => DropdownMenuItem(
                              value: type,
                              child: Text(type),
                            ),
                          )
                          .toList(),
                  onChanged: (value) {
                    setState(() {
                      _selectedTransactionType = value!;
                    });
                  },
                  decoration: InputDecoration(labelText: 'Transaction Type'),
                ),
                SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        'Date: ${DateFormat.yMMMd().format(_selectedDate)}',
                      ),
                    ),
                    TextButton(
                      onPressed: () async {
                        final pickedDate = await showDatePicker(
                          context: context,
                          initialDate: _selectedDate,
                          firstDate: DateTime(2020),
                          lastDate: DateTime.now(),
                        );
                        if (pickedDate != null) {
                          setState(() {
                            _selectedDate = pickedDate;
                          });
                        }
                      },
                      child: Text('Pick Date'),
                    ),
                  ],
                ),
                SizedBox(height: 20),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  onPressed: () async {
                    final amountText = _amountController.text.trim();
                    final titleText = _titleController.text.trim();

                    if (amountText.isEmpty || titleText.isEmpty) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text("Please enter title and amount"),
                        ),
                      );
                      return;
                    }

                    final amount = double.tryParse(amountText);
                    if (amount == null || amount <= 0) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text("Please enter a valid amount")),
                      );
                      return;
                    }

                    final txnType =
                        _selectedTransactionType.toLowerCase() == 'debit'
                            ? 'expense'
                            : 'income';

                    final url = Uri.parse(
                      "${UriConstant.baseUrl}/transactions",
                    );

                    final headers = {
                      'Content-Type': 'application/json',
                      'Cookie': 'sessionid=${SessionManager().sessionId}',
                    };

                    final body = jsonEncode({
                      "amount": amount,
                      "narration": titleText,
                      "type": txnType,
                      "date":
                          DateFormat(
                            'yyyy-MM-dd',
                          ).format(_selectedDate).toString(),
                    });

                    try {
                      final response = await http.post(
                        url,
                        headers: headers,
                        body: body,
                      );

                      if (response.statusCode == 200 ||
                          response.statusCode == 201) {
                        final resData = jsonDecode(response.body);
                        if (resData["success"] == true) {
                          final newTxn = resData["transaction"];
                          setState(() {
                            transactions.add(newTxn);
                          });

                          Navigator.of(context).pop();

                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text("Transaction added successfully"),
                            ),
                          );
                        } else {
                          throw Exception("Server rejected the transaction");
                        }
                      } else {
                        throw Exception("Failed to add transaction");
                      }
                    } catch (e) {
                      Navigator.of(context).pop();
                      ScaffoldMessenger.of(
                        context,
                      ).showSnackBar(SnackBar(content: Text("Error: $e")));
                    } finally {
                      setState(() => isLoading = false);
                    }
                  },

                  child: SizedBox(
                    width: double.infinity,
                    child: Center(
                      child: Text(
                        'Add Expense',
                        style: TextStyle(color: Colors.white),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final dateFormat = DateFormat('dd/MM/yyyy');

    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 241, 249, 249),
      appBar: AppBar(
        backgroundColor: const Color.fromARGB(255, 241, 249, 249),
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () => Navigator.of(context).pop(),
        ),
        title: Text('Transactions', style: TextStyle(color: Colors.black)),
        centerTitle: true,
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          Column(
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
                  SizedBox(width: 12),
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
                  onPressed: _loadTransactions,

                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color.fromARGB(255, 6, 67, 72),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child:
                      isLoading
                          ? CircularProgressIndicator(color: Colors.white)
                          : Text(
                            'Filter',
                            style: TextStyle(color: Colors.white, fontSize: 16),
                          ),
                ),
              ),
              SizedBox(height: 8),
              Container(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    setState(() => isLoading = true);
                    try {
                      _showFormatDialog();
                    } catch (e) {
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
                    'Download Report',
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ),
              ),
            ],
          ),
          SizedBox(height: 30),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryCard(
                '-₹${totalExpenses.toStringAsFixed(0)}',
                'Expenses',
                Colors.red,
              ),
              _buildSummaryCard(
                '₹${balanceAmount.toStringAsFixed(0)}',
                'Balance',
                Colors.green,
              ),
            ],
          ),

          SizedBox(height: 20),
          ..._groupTransactionsByDate(transactions).entries.map((entry) {
            final date = entry.key;
            final dateTxns = entry.value;

            double totalForDate = 0;
            for (var txn in dateTxns) {
              if (txn['txn_type'] == 'DEBIT') {
                totalForDate -= txn['amount'];
              }
              if (txn['txn_type'] == 'CREDIT') {
                totalForDate += txn['amount'];
              }
            }

            return _buildTransactionSectionGrouped(
              date,
              totalForDate,
              dateTxns,
            );
          }).toList(),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: const Color.fromARGB(255, 6, 67, 72),
        onPressed: _showAddExpensePopup,
        icon: Icon(Icons.add, color: Colors.white),
        label: Text('Add new', style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildSummaryCard(String amount, String label, Color color) {
    return Column(
      children: [
        Text(
          amount,
          style: TextStyle(
            color: color,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(label, style: TextStyle(color: Colors.grey)),
      ],
    );
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

  Widget _buildTransactionItem(
    IconData icon,
    String title,
    String subtitle,
    double amount,
    Color iconBg,
  ) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      leading: CircleAvatar(
        backgroundColor: iconBg.withOpacity(0.2),
        child: Icon(icon, color: iconBg),
      ),
      title: Text(title.length > 30 ? title.substring(0, 30) : title),
      subtitle: Text(subtitle),
      trailing: Text('₹$amount', style: TextStyle(color: iconBg)),
    );
  }
}
