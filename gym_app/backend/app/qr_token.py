import base64
import hashlib
import hmac
import struct
from datetime import datetime, timezone

from app.config import QR_WINDOW_SECONDS


def _window_at(ts: float) -> int:
    return int(ts // QR_WINDOW_SECONDS)


def _build_token(gym_id: str, window: int, qr_secret: str) -> str:
    secret = qr_secret.encode("utf-8")
    msg = f"{gym_id}:{window}".encode("utf-8")
    sig = hmac.new(secret, msg, hashlib.sha256).digest()
    gid = gym_id.encode("utf-8")
    payload = struct.pack(">H", len(gid)) + gid + struct.pack(">q", window) + sig
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def generate_current_token(
    *,
    gym_id: str,
    qr_secret: str,
    now: datetime | None = None,
) -> tuple[str, datetime]:
    if now is None:
        now = datetime.now(timezone.utc)
    ts = now.timestamp()
    w = _window_at(ts)
    token = _build_token(gym_id, w, qr_secret)
    window_end = (w + 1) * QR_WINDOW_SECONDS
    expires_at = datetime.fromtimestamp(window_end, tz=timezone.utc)
    return token, expires_at


def verify_token(
    token: str,
    *,
    gym_id: str,
    qr_secret: str,
    now: datetime | None = None,
) -> bool:
    if now is None:
        now = datetime.now(timezone.utc)
    ts = now.timestamp()
    w_cur = _window_at(ts)
    for w in (w_cur, w_cur - 1):
        expected = _build_token(gym_id, w, qr_secret)
        if hmac.compare_digest(token, expected):
            return True
    return False
