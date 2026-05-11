import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import School, User
from app.schemas import SchoolRegister, TokenResponse
from app.security import create_access_token, hash_password

router = APIRouter(prefix="/schools", tags=["schools"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_school(
    body: SchoolRegister,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    uname = body.master_username.strip()
    school = School(
        name=body.school_name.strip(),
        qr_secret=secrets.token_urlsafe(32),
    )
    db.add(school)
    db.flush()

    display = body.master_display_name.strip() if body.master_display_name else None
    user = User(
        school_id=school.id,
        username=uname,
        password_hash=hash_password(body.master_password),
        role="admin",
        full_name=display,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not create school (username may already exist for this school).",
        )
    db.refresh(school)
    db.refresh(user)

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
