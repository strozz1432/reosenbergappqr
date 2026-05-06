import base64
import hashlib
import hmac
import struct
from datetime import datetime, timezone

from app.config import GYM_ID, QR_SECRET, QR_WINDOW_SECONDS


def _window_at(ts: float) -> int:
    return int(ts // QR_WINDOW_SECONDS)


def generate_current_token(now: datetime | None = None) -> tuple[str, datetime]:
    """Returns (token, expires_at) for the current QR window."""
    if now is None:
        now = datetime.now(timezone.utc)
    ts = now.timestamp()
    w = _window_at(ts)
    token = _build_token(GYM_ID, w)
    window_end = (w + 1) * QR_WINDOW_SECONDS
    expires_at = datetime.fromtimestamp(window_end, tz=timezone.utc)
    return token, expires_at


def _build_token(gym_id: str, window: int) -> str:
    secret = QR_SECRET.encode("utf-8")
    msg = f"{gym_id}:{window}".encode("utf-8")
    sig = hmac.new(secret, msg, hashlib.sha256).digest()
    # Binary payload: len(gym_id u16) | gym_id | window i64 | sig 32 bytes
    gid = gym_id.encode("utf-8")
    payload = struct.pack(">H", len(gid)) + gid + struct.pack(">q", window) + sig
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def verify_token(token: str, now: datetime | None = None) -> bool:
    """Accept current or previous window."""
    if now is None:
        now = datetime.now(timezone.utc)
    ts = now.timestamp()
    w_cur = _window_at(ts)
    for w in (w_cur, w_cur - 1):
        expected = _build_token(GYM_ID, w)
        if hmac.compare_digest(token, expected):
            return True
    return False


def token_expires_at_for_window(window: int) -> datetime:
    window_end = (window + 1) * QR_WINDOW_SECONDS
    return datetime.fromtimestamp(window_end, tz=timezone.utc)
