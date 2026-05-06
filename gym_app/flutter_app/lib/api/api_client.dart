import 'package:dio/dio.dart';

/// Thin wrapper around [Dio] with optional Bearer injection per request.
class ApiClient {
  ApiClient({
    required String baseUrl,
    String? Function()? tokenGetter,
  }) : _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl,
            connectTimeout: const Duration(seconds: 15),
            receiveTimeout: const Duration(seconds: 15),
          ),
        ) {
    final getter = tokenGetter;
    if (getter != null) {
      _dio.interceptors.add(
        InterceptorsWrapper(
          onRequest: (options, handler) {
            final t = getter();
            if (t != null && t.isNotEmpty) {
              options.headers['Authorization'] = 'Bearer $t';
            }
            return handler.next(options);
          },
        ),
      );
    }
  }

  final Dio _dio;

  Dio get dio => _dio;

  /// Requests without `Authorization`.
  factory ApiClient.anonymous(String baseUrl) => ApiClient(baseUrl: baseUrl);

  /// Sends `Authorization: Bearer …` using [tokenGetter] on each request.
  factory ApiClient.authenticated(
    String baseUrl,
    String? Function() tokenGetter,
  ) =>
      ApiClient(baseUrl: baseUrl, tokenGetter: tokenGetter);
}
