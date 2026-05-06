import os

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-change-in-production-min-32-chars!!")
QR_SECRET = os.getenv("QR_SECRET", "dev-qr-secret-change-in-production-min-32-chars!!")
GYM_ID = os.getenv("GYM_ID", "default-gym")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
QR_WINDOW_SECONDS = 15
