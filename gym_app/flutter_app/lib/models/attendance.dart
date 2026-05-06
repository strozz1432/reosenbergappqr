class AttendanceRow {
  const AttendanceRow({
    required this.id,
    required this.userId,
    required this.username,
    this.fullName,
    required this.eventType,
    required this.timestampIso,
  });

  final int id;
  final int userId;
  final String username;
  final String? fullName;
  final String eventType;
  final String timestampIso;

  factory AttendanceRow.fromJson(Map<String, dynamic> json) {
    return AttendanceRow(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      username: json['username'] as String,
      fullName: json['full_name'] as String?,
      eventType: json['event_type'] as String,
      timestampIso: json['timestamp'] as String,
    );
  }
}

class ScanResult {
  const ScanResult({
    required this.eventType,
    required this.timestampIso,
  });

  final String eventType;
  final String timestampIso;

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      eventType: json['event_type'] as String,
      timestampIso: json['timestamp'] as String,
    );
  }
}
