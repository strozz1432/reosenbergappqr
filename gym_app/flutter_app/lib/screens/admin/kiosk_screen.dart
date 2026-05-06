import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../../state/auth_state.dart';

class KioskScreen extends StatefulWidget {
  const KioskScreen({super.key});

  @override
  State<KioskScreen> createState() => _KioskScreenState();
}

class _KioskScreenState extends State<KioskScreen> {
  Timer? _timer;
  String? _token;
  String? _expires;
  String? _error;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fetch();
      _timer = Timer.periodic(const Duration(seconds: 12), (_) => _fetch());
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _fetch() async {
    final auth = context.read<AuthState>();
    try {
      final dio = auth.authenticatedClient();
      final r = await dio.get<Map<String, dynamic>>('/qr/current');
      final data = r.data!;
      if (mounted) {
        setState(() {
          _token = data['token'] as String?;
          _expires = data['expires_at'] as String?;
          _error = null;
        });
      }
    } on DioException catch (e) {
      if (mounted) {
        setState(() {
          _error = e.response?.data?.toString() ?? e.message ?? 'Failed to load QR';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final token = _token;
    return LayoutBuilder(
      builder: (context, constraints) {
        final size = (constraints.biggest.shortestSide * 0.55).clamp(200.0, 420.0);
        return Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  'Show this QR to students checking in/out',
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                if (_expires != null)
                  Text(
                    'Rotates ~every 15s · Next refresh: $_expires',
                    style: Theme.of(context).textTheme.bodySmall,
                    textAlign: TextAlign.center,
                  ),
                const SizedBox(height: 24),
                if (_error != null)
                  Text(
                    _error!,
                    style: TextStyle(color: Theme.of(context).colorScheme.error),
                    textAlign: TextAlign.center,
                  ),
                if (token != null && token.isNotEmpty)
                  QrImageView(
                    data: token,
                    version: QrVersions.auto,
                    size: size,
                    backgroundColor: Colors.white,
                  )
                else if (_error == null)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: CircularProgressIndicator(),
                  ),
                const SizedBox(height: 16),
                FilledButton.icon(
                  onPressed: _fetch,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Refresh now'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
