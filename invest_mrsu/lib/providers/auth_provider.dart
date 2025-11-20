import 'package:flutter/foundation.dart';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = false;
  String? _userEmail;

  bool get isAuthenticated => _isAuthenticated;
  String? get userEmail => _userEmail;

  // Вход (mock версия)
  Future<bool> login(String email, String password) async {
    // Симуляция запроса к серверу
    await Future.delayed(const Duration(seconds: 1));

    // В MVP принимаем любой email/password
    if (email.isNotEmpty && password.length >= 6) {
      _isAuthenticated = true;
      _userEmail = email;
      notifyListeners();
      return true;
    }

    return false;
  }

  // Регистрация (mock версия)
  Future<bool> register(String email, String password) async {
    // Симуляция запроса к серверу
    await Future.delayed(const Duration(seconds: 1));

    // В MVP принимаем любой email/password
    if (email.isNotEmpty && password.length >= 6) {
      _isAuthenticated = true;
      _userEmail = email;
      notifyListeners();
      return true;
    }

    return false;
  }

  // Выход
  void logout() {
    _isAuthenticated = false;
    _userEmail = null;
    notifyListeners();
  }
}
