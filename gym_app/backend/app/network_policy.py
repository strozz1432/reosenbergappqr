import ipaddress
import os

from fastapi import HTTPException, Request, status


def _scan_allowed_networks():
    raw = os.getenv("SCAN_ALLOWED_CIDRS", "").strip()
    if not raw:
        return None
    nets: list = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            nets.append(ipaddress.ip_network(part, strict=False))
        except ValueError:
            continue
    return nets if nets else None


def client_host(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


def require_scan_from_allowed_network(request: Request) -> None:
    """
    If SCAN_ALLOWED_CIDRS is set, only clients whose IP falls in one of the
    listed networks may POST /attendance/scan. Use the gym (or trusted) Wi-Fi
    subnet — not the dorm subnet — so phones in rooms cannot check in remotely
    when those networks differ.
    """
    nets = _scan_allowed_networks()
    if nets is None:
        return
    host = client_host(request)
    if not host:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not verify network for check-in.",
        )
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        # Starlette/FastAPI TestClient uses host "testclient". Treat as loopback so
        # allowlists can be tested (e.g. include 127.0.0.0/8 for local integration tests).
        if host == "testclient":
            addr = ipaddress.ip_address("127.0.0.1")
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not verify client network (invalid IP).",
            )
    if not any(addr in n for n in nets):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Check-in is only allowed from the gym network. Connect to the designated Wi‑Fi at the facility, or ask IT for access.",
        )
