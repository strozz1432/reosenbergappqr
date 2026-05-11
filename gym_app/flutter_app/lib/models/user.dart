class UserOut {
  const UserOut({
    required this.id,
    required this.schoolId,
    required this.username,
    required this.role,
    this.fullName,
  });

  final int id;
  final int schoolId;
  final String username;
  final String role;
  final String? fullName;

  factory UserOut.fromJson(Map<String, dynamic> json) {
    return UserOut(
      id: json['id'] as int,
      schoolId: json['school_id'] as int,
      username: json['username'] as String,
      role: json['role'] as String,
      fullName: json['full_name'] as String?,
    );
  }
}
