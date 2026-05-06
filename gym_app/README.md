# Student Gym QR Check-in

FastAPI + SQLite backend and a Flutter client for **Windows/Linux (admin kiosk + attendance)** and **iPhone/Android (student scanner)**.

## Architecture

- **Backend**: JWT login; rotating HMAC QR token (`GET /qr/current`, admin only); students post scans to `POST /attendance/scan`; attendance toggles in/out automatically.
- **Flutter**: One app; students see scan UI; admins see a **Kiosk** tab (polls QR every 12s) and **Attendance** tab (list + date filter + auto-refresh every 10s).

## Prerequisites

- Python 3.11+
- [Flutter SDK](https://docs.flutter.dev/get-started/install) (for the mobile/desktop UI)

## Backend

```bash
cd gym_app/backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS

pip install -r requirements.txt
copy .env.example .env          # optional; defaults work for local dev
python seed.py                  # demo users (idempotent)
uvicorn app.main:app --host 0.0.0.0 --reload --port 8000
```

API root: `http://127.0.0.1:8000` · OpenAPI: `http://127.0.0.1:8000/docs`

### Demo accounts (from `seed.py`)

| Username | Password   | Role    |
|----------|------------|---------|
| admin    | admin123   | admin   |
| student1 | student123 | student |
| student2 | student456 | student |

### iPhone on the same Wi-Fi

The phone cannot use `127.0.0.1` for your PC. Find your PC’s LAN IP (e.g. `192.168.1.10`) and:

1. Start the backend with `--host 0.0.0.0` (above).
2. Allow Python through Windows Firewall if prompted.
3. In the app **login screen**, set **API base URL** to `http://<PC-LAN-IP>:8000`.

Optional one-shot build:

```bash
flutter run --dart-define=API_BASE_URL=http://192.168.x.x:8000
```

(Default in code is `http://127.0.0.1:8000`, suitable for desktop/simulator.)

## Flutter app (first-time setup)

This repo includes `pubspec.yaml` and Dart sources only. Generate platform runners once:

```bash
cd gym_app/flutter_app
flutter create . --platforms=ios,windows,linux --project-name gym_app_flutter
flutter pub get
```

### Run on Windows desktop (admin)

```bash
flutter run -d windows
```

Log in as **admin** → **Kiosk QR** tab shows the rotating code; **Attendance** lists check-ins/outs.

### Run on iPhone

1. Open `ios/Runner.xcworkspace` in Xcode (after `flutter create`), select your device, set signing team.
2. Add **Privacy - Camera Usage Description** in `ios/Runner/Info.plist` if not present (Flutter plugins often add it; use a string like “Scan gym QR codes”).
3. `flutter run -d <device-id>` or Run from Xcode.

Log in as **student1** / **student123**, set API URL to your PC’s LAN IP, tap **Scan gym QR** and point at the kiosk screen.

### Desktop “student” role

Camera scanning is only enabled on iOS/Android. On Windows/Linux, the student screen offers a **paste token** field so you can copy the raw token from the kiosk API response for quick testing.

## Endpoints (summary)

| Method | Path | Auth |
|--------|------|------|
| POST | `/auth/login` | — |
| GET | `/qr/current` | admin JWT |
| POST | `/attendance/scan` | student JWT, body `{ "qr_token": "..." }` |
| GET | `/admin/attendance?date=YYYY-MM-DD` | admin JWT |
| GET / POST | `/admin/users` | admin JWT |

## Security notes (MVP)

- JWT is long-lived for demos; use refresh tokens + HTTPS in production.
- QR tokens rotate every **15 seconds** and are verified server-side with `QR_SECRET`.
- Change `JWT_SECRET` and `QR_SECRET` in `.env` for anything beyond local testing.
