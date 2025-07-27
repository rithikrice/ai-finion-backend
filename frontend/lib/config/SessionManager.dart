class SessionManager {
  static final SessionManager _instance = SessionManager._internal();
  String? sessionId;
  String? phoneNumber;

  factory SessionManager() => _instance;

  SessionManager._internal();
}
