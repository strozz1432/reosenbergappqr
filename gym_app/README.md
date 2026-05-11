# Student Gym QR Check-in

FastAPI + SQLite backend and a Flutter client for **Windows/Linux (admin kiosk + attendance)** and **iPhone/Android (student scanner)**.

## Architecture

- **Backend**: JWT login; **multi-school** (each school has its own QR secret and attendance list); rotating QR token (`GET /qr/current`, admin only); students post scans to `POST /attendance/scan`; attendance toggles in/out automatically.
- **Flutter**: One app; students see scan UI; admins see a **Kiosk** tab (polls QR every 12s) and **Attendance** tab (list + date filter + auto-refresh every 10s).
- **Browser staff UI**: `/teacher` (sign-in + attendance + door QR) and **`/teacher/setup`** (create a new school + master admin with a **strong** password).

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

On Windows you can use **[`backend/run.ps1`](gym_app/backend/run.ps1)** so the port stays **8000** every day (bookmark `http://<PC-LAN-IP>:8000/teacher` on secondary monitors).

API root: `http://127.0.0.1:8000` · OpenAPI: `http://127.0.0.1:8000/docs`

### Staff browser desk (no Flutter)

After `uvicorn` is running:

- **`http://127.0.0.1:8000/teacher`** — sign in as **admin**, see attendance for **your school only** and the rotating **door QR**.
- **`http://127.0.0.1:8000/teacher/kiosk`** — **QR-only** fullscreen for a projector or second PC. **Admin / master login required** (same API account as the desk). Uses the same browser session key as `/teacher`, so signing in on one tab can unlock the other on the same machine. On another device on the LAN use `http://<PC-IP>:8000/teacher/kiosk` and sign in there.
- **`http://127.0.0.1:8000/teacher/setup`** — **Create new school**: school name, optional director name, master username, and a **strong** password (12+ chars, upper, lower, digit, symbol). You are signed in afterward and redirected to `/teacher`.

The **door QR** is drawn on the **server** (SVG in the `/qr/current` JSON) — no browser CDN, so it works offline on the staff PC.

**Usernames** can be the same in two different schools; if login says several accounts share the username, enter the **school ID** shown on the staff bar after setup (Flutter login has an optional “School ID” field too).

### Limiting check-in to the gym network (not dorm rooms)

Tokens already expire in ~15 seconds, but anyone who can **reach your API** could still try to send a captured code. For stronger control:

1. Set **`SCAN_ALLOWED_CIDRS`** in `.env` to the **Wi-Fi subnet used at the gym / check-in desk only** (comma-separated CIDRs). Student phones must get an IP in that range for `POST /attendance/scan` to succeed. If dorm Wi-Fi uses a **different** subnet than the gym, phones in rooms will be **rejected** even with a valid QR string.
2. If dorm and gym share one flat subnet, **IT needs separate VLANs / SSIDs** for this to separate traffic; software cannot invent two networks from one.
3. Keep the API off the public internet; use LAN or a VPN only staff should use for the kiosk browser if needed.

**Upgrading from an older single-school `gym.db`:** SQLite will not always migrate cleanly. If the app fails on start, stop uvicorn, delete `gym.db`, run `python seed.py` again.

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
flutter create . --platforms=ios,windows,linux,web --project-name gym_app_flutter
flutter pub get
```

The `web/` folder is already in the repo (`index.html`, `flutter_bootstrap.js`, `manifest.json`). If `flutter create` warns about existing files, choose to **merge** or skip overwriting those three.

### Run in Chrome (preview UI / theme)

Useful when you do not have a Mac or want a quick layout check. Camera QR scanning is limited in the browser; admin + login + paste-token flows work best.

```bash
cd gym_app/flutter_app
flutter pub get
flutter run -d chrome
```

Ensure the backend is running; on the login screen set **API base URL** to `http://127.0.0.1:8000` (same machine).

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
- QR tokens rotate every **15 seconds** and are verified per school with that school’s **stored secret** (new schools get a random secret on creation). Legacy env `QR_SECRET` / `GYM_ID` in `.env` are unused for new installs.
- Change `JWT_SECRET` in `.env` for anything beyond local testing.
