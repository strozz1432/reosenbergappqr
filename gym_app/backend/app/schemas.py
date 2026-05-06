from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1)
    full_name: str | None = None
    role: str = Field(default="student", pattern="^(student|admin)$")


class UserOut(BaseModel):
    id: int
    username: str
    role: str
    full_name: str | None = None

    model_config = {"from_attributes": True}


class ScanRequest(BaseModel):
    qr_token: str


class ScanResponse(BaseModel):
    event_type: str
    timestamp: datetime


class QrCurrentResponse(BaseModel):
    token: str
    expires_at: datetime


class AttendanceRow(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: str | None
    event_type: str
    timestamp: datetime

    model_config = {"from_attributes": True}
