import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

import '../../models/attendance.dart';
import '../../state/auth_state.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Timer? _timer;
  List<AttendanceRow> _rows = [];
  String? _error;
  bool _loading = false;
  DateTime _day = DateTime.now();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _load();
      _timer = Timer.periodic(const Duration(seconds: 10), (_) => _load());
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  String get _dateParam => DateFormat('yyyy-MM-dd').format(_day);

  Future<void> _load() async {
    final auth = context.read<AuthState>();
    setState(() => _loading = true);
    try {
      final dio = auth.authenticatedClient();
      final r = await dio.get<List<dynamic>>(
        '/admin/attendance',
        queryParameters: {'date': _dateParam},
      );
      final list = r.data ?? [];
      if (mounted) {
        setState(() {
          _rows = list
              .map((e) =>
                  AttendanceRow.fromJson(Map<String, dynamic>.from(e as Map)))
              .toList();
          _error = null;
        });
      }
    } on DioException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.response?.data?.toString() ?? e.message;
        });
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _pickDay() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _day,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() => _day = picked);
      await _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    final fmt = DateFormat.yMMMd();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          child: Row(
            children: [
              Text('Day: ${fmt.format(_day)}', style: Theme.of(context).textTheme.titleMedium),
              const SizedBox(width: 8),
              OutlinedButton(onPressed: _pickDay, child: const Text('Pick date')),
              const Spacer(),
              IconButton(
                tooltip: 'Refresh',
                onPressed: _load,
                icon: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.refresh),
              ),
            ],
          ),
        ),
        if (_error != null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
          ),
        Expanded(
          child: ListView.builder(
            itemCount: _rows.length,
            itemBuilder: (context, i) {
              final row = _rows[i];
              final name = row.fullName ?? row.username;
              return ListTile(
                leading:
                    Icon(row.eventType == 'in' ? Icons.login : Icons.logout),
                title: Text(name),
                subtitle: Text(row.username),
                trailing: Text(row.timestampIso),
              );
            },
          ),
        ),
      ],
    );
  }
}

/// Shared with [AdminHomeScreen] FAB.
Future<void> showCreateUserDialog(BuildContext context) async {
  final usernameCtrl = TextEditingController();
  final passCtrl = TextEditingController();
  final nameCtrl = TextEditingController();
  String role = 'student';

  final ok = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Create user'),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: usernameCtrl,
              decoration: const InputDecoration(labelText: 'Username'),
            ),
            TextField(
              controller: passCtrl,
              decoration: const InputDecoration(labelText: 'Password'),
              obscureText: true,
            ),
            TextField(
              controller: nameCtrl,
              decoration: const InputDecoration(labelText: 'Full name (optional)'),
            ),
            const SizedBox(height: 8),
            StatefulBuilder(
              builder: (context, setDialogState) {
                return DropdownButtonFormField<String>(
                  value: role,
                  items: const [
                    DropdownMenuItem(value: 'student', child: Text('Student')),
                    DropdownMenuItem(value: 'admin', child: Text('Admin')),
                  ],
                  onChanged: (v) => setDialogState(() => role = v ?? 'student'),
                  decoration: const InputDecoration(labelText: 'Role'),
                );
              },
            ),
          ],
        ),
      ),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
        FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Create')),
      ],
    ),
  );

  if (ok != true || !context.mounted) return;

  await createUserWithControllers(
    context,
    usernameCtrl: usernameCtrl,
    passCtrl: passCtrl,
    nameCtrl: nameCtrl,
    role: role,
  );
}

Future<void> createUserWithControllers(
  BuildContext context, {
  required TextEditingController usernameCtrl,
  required TextEditingController passCtrl,
  required TextEditingController nameCtrl,
  required String role,
}) async {
  try {
    final dio = context.read<AuthState>().authenticatedClient();
    await dio.post('/admin/users', data: {
      'username': usernameCtrl.text.trim(),
      'password': passCtrl.text,
      'full_name': nameCtrl.text.trim().isEmpty ? null : nameCtrl.text.trim(),
      'role': role,
    });
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('User created')),
      );
    }
  } on DioException catch (e) {
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.response?.data?.toString() ?? 'Failed')),
      );
    }
  }
}
