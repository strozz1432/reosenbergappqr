from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.password_policy import validate_strong_password


class LoginRequest(BaseModel):
    username: str
    password: str
    school_id: int | None = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    school_id: int
    school_name: str


class SchoolRegister(BaseModel):
    school_name: str = Field(min_length=2, max_length=200)
    master_username: str = Field(min_length=3, max_length=128)
    master_password: str = Field(min_length=12, max_length=128)
    master_display_name: str | None = Field(None, max_length=255)

    @field_validator("master_display_name", mode="before")
    @classmethod
    def strip_display(cls, v):
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @field_validator("master_password")
    @classmethod
    def strong_password(cls, v: str) -> str:
        validate_strong_password(v)
        return v


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1)
    full_name: str | None = None
    role: str = Field(default="student", pattern="^(student|admin)$")


class UserOut(BaseModel):
    id: int
    school_id: int
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
    qr_svg: str


class AttendanceRow(BaseModel):
    id: int
    user_id: int
    username: str
    full_name: str | None
    event_type: str
    timestamp: datetime

    model_config = {"from_attributes": True}
