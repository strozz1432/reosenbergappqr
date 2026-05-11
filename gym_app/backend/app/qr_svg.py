import io

try:
    import segno
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "Missing package 'segno'. In the same environment you use for uvicorn, run:\n"
        "  pip install segno\n"
        "or:\n"
        "  pip install -r requirements.txt\n"
        "(If you use a venv, activate it first.)"
    ) from e


def token_to_svg(token: str) -> str:
    """Render QR payload as an SVG string (no external JS/CDN)."""
    qr = segno.make(token, error="m", micro=False)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", scale=4, border=2, dark="#111827", light="#ffffff")
    return buf.getvalue().decode("utf-8")
