import 'package:flutter/foundation.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../api/api_client.dart';
import '../config.dart';

class AuthState extends ChangeNotifier {
  AuthState({FlutterSecureStorage? storage})
      : _storage = storage ?? const FlutterSecureStorage();

  final FlutterSecureStorage _storage;

  String? token;
  String? role;
  String apiBaseUrl = kDefaultApiBaseUrl;

  static const _kJwt = 'jwt';
  static const _kRole = 'role';
  static const _kApiBase = 'api_base_url';

  Future<void> load() async {
    token = await _storage.read(key: _kJwt);
    role = await _storage.read(key: _kRole);
    apiBaseUrl = await _storage.read(key: _kApiBase) ?? kDefaultApiBaseUrl;
    notifyListeners();
  }

  Future<void> setApiBaseUrl(String url) async {
    var u = url.trim();
    if (u.isEmpty) return;
    while (u.endsWith('/')) {
      u = u.substring(0, u.length - 1);
    }
    apiBaseUrl = u;
    await _storage.write(key: _kApiBase, value: apiBaseUrl);
    notifyListeners();
  }

  Future<void> login(String username, String password, {int? schoolId}) async {
    final dio = ApiClient.anonymous(apiBaseUrl).dio;
    final payload = <String, dynamic>{
      'username': username,
      'password': password,
    };
    if (schoolId != null) payload['school_id'] = schoolId;
    final response = await dio.post<Map<String, dynamic>>(
      '/auth/login',
      data: payload,
    );
    final data = response.data!;
    token = data['access_token'] as String?;
    role = data['role'] as String?;
    await _storage.write(key: _kJwt, value: token);
    await _storage.write(key: _kRole, value: role);
    notifyListeners();
  }

  Future<void> logout() async {
    token = null;
    role = null;
    await _storage.delete(key: _kJwt);
    await _storage.delete(key: _kRole);
    notifyListeners();
  }

  Dio authenticatedClient() {
    return ApiClient.authenticated(apiBaseUrl, () => token).dio;
  }
}
