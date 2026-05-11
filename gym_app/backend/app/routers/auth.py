from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import School, User
from app.schemas import LoginRequest, TokenResponse
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    q = select(User).where(User.username == body.username)
    if body.school_id is not None:
        q = q.where(User.school_id == body.school_id)
    candidates = db.scalars(q).all()
    matching = [u for u in candidates if verify_password(body.password, u.password_hash)]
    if len(matching) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    if len(matching) > 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Several accounts use this username. Enter your school ID and try again.",
        )
    user = matching[0]
    school = db.get(School, user.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="School record missing")
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        role=user.role,
        school_id=school.id,
    )
    return TokenResponse(
        access_token=token,
        role=user.role,
        school_id=school.id,
        school_name=school.name,
    )
