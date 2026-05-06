import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'screens/admin/admin_home_screen.dart';
import 'screens/login_screen.dart';
import 'screens/student/scan_screen.dart';
import 'state/auth_state.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final auth = AuthState();
  await auth.load();

  final router = GoRouter(
    initialLocation: '/login',
    refreshListenable: auth,
    redirect: (context, state) {
      final loggedIn = auth.token != null;
      final loc = state.uri.path;
      if (!loggedIn) {
        return loc == '/login' ? null : '/login';
      }
      if (loc == '/login') {
        return auth.role == 'admin' ? '/admin' : '/student';
      }
      if (auth.role == 'student' && loc.startsWith('/admin')) {
        return '/student';
      }
      if (auth.role == 'admin' && loc.startsWith('/student')) {
        return '/admin';
      }
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        builder: (context, state) => const LoginScreen(),
      ),
      GoRoute(
        path: '/student',
        builder: (context, state) => const ScanScreen(),
      ),
      GoRoute(
        path: '/admin',
        builder: (context, state) => const AdminHomeScreen(),
      ),
    ],
  );

  runApp(
    ChangeNotifierProvider.value(
      value: auth,
      child: GymApp(router: router),
    ),
  );
}

class GymApp extends StatelessWidget {
  const GymApp({super.key, required this.router});

  final GoRouter router;

  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: 'Gym check-in',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      routerConfig: router,
    );
  }
}
