import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';

import '../../models/attendance.dart';
import '../../state/auth_state.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  String? _lastMessage;
  Color? _bannerColor;
  bool _submitting = false;

  bool get _hasCameraScanner {
    if (kIsWeb) return false;
    return defaultTargetPlatform == TargetPlatform.iOS ||
        defaultTargetPlatform == TargetPlatform.android;
  }

  Future<void> _submitToken(String raw) async {
    final trimmed = raw.trim();
    if (trimmed.isEmpty || _submitting) return;
    setState(() => _submitting = true);
    final auth = context.read<AuthState>();
    try {
      final dio = auth.authenticatedClient();
      final r = await dio.post<Map<String, dynamic>>(
        '/attendance/scan',
        data: {'qr_token': trimmed},
      );
      final scan = ScanResult.fromJson(r.data!);
      if (!mounted) return;
      setState(() {
        _lastMessage = scan.eventType == 'in'
            ? 'Checked in at ${scan.timestampIso}'
            : 'Checked out at ${scan.timestampIso}';
        _bannerColor =
            scan.eventType == 'in' ? Colors.green.shade800 : Colors.blue.shade800;
      });
    } on DioException catch (e) {
      final detail = e.response?.data;
      String msg = 'Request failed';
      if (detail is Map && detail['detail'] != null) {
        msg = detail['detail'].toString();
      }
      if (!mounted) return;
      setState(() {
        _lastMessage = msg;
        _bannerColor = Theme.of(context).colorScheme.error;
      });
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _openScanner() async {
    final code = await Navigator.of(context).push<String>(
      MaterialPageRoute(
        builder: (ctx) => const _QrScannerPage(),
      ),
    );
    if (code != null && mounted) await _submitToken(code);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Student'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => context.read<AuthState>().logout(),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            if (_lastMessage != null)
              Card(
                color: _bannerColor?.withOpacity(0.12),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: Row(
                    children: [
                      Expanded(child: Text(_lastMessage!)),
                      IconButton(
                        icon: const Icon(Icons.close),
                        onPressed: () => setState(() => _lastMessage = null),
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 16),
            Text(
              'Scan the QR shown on the gym desktop kiosk to check in or out.',
              style: Theme.of(context).textTheme.bodyLarge,
            ),
            const SizedBox(height: 24),
            if (_hasCameraScanner)
              FilledButton.icon(
                onPressed: _submitting ? null : _openScanner,
                icon: const Icon(Icons.qr_code_scanner),
                label: const Text('Scan gym QR'),
              )
            else
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    'Camera scanner runs on iPhone/Android. '
                    'Paste the kiosk token below to test from desktop.',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  const SizedBox(height: 12),
                  _PasteTokenField(onSubmit: _submitToken, enabled: !_submitting),
                ],
              ),
            if (_submitting) const LinearProgressIndicator(),
          ],
        ),
      ),
    );
  }
}

class _PasteTokenField extends StatefulWidget {
  const _PasteTokenField({required this.onSubmit, required this.enabled});

  final Future<void> Function(String) onSubmit;
  final bool enabled;

  @override
  State<_PasteTokenField> createState() => _PasteTokenFieldState();
}

class _PasteTokenFieldState extends State<_PasteTokenField> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: TextField(
            controller: _ctrl,
            enabled: widget.enabled,
            decoration: const InputDecoration(
              labelText: 'QR token',
              border: OutlineInputBorder(),
            ),
            maxLines: 2,
          ),
        ),
        const SizedBox(width: 8),
        FilledButton(
          onPressed: widget.enabled
              ? () => widget.onSubmit(_ctrl.text)
              : null,
          child: const Text('Submit'),
        ),
      ],
    );
  }
}

class _QrScannerPage extends StatefulWidget {
  const _QrScannerPage();

  @override
  State<_QrScannerPage> createState() => _QrScannerPageState();
}

class _QrScannerPageState extends State<_QrScannerPage> {
  bool _handled = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Scan gym QR')),
      body: MobileScanner(
        onDetect: (capture) {
          if (_handled) return;
          for (final b in capture.barcodes) {
            final v = b.rawValue;
            if (v != null && v.isNotEmpty) {
              _handled = true;
              Navigator.of(context).pop(v);
              break;
            }
          }
        },
      ),
    );
  }
}
