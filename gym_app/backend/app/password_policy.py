import re


def validate_strong_password(password: str) -> None:
    """Raises ValueError with a short message if the password is too weak."""
    if len(password) < 12:
        raise ValueError("Use at least 12 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Include at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Include at least one digit.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Include at least one symbol (for example ! ? #).")
