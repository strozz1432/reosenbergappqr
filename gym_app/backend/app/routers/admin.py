from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin
from app.models import AttendanceEvent, User
from app.schemas import AttendanceRow, UserCreate, UserOut
from app.security import hash_password

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> list[UserOut]:
    users = db.scalars(select(User).order_by(User.username)).all()
    return [UserOut.model_validate(u) for u in users]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> UserOut:
    exists = db.scalar(select(User).where(User.username == body.username))
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")
    u = User(
        username=body.username,
        password_hash=hash_password(body.password),
        role=body.role,
        full_name=body.full_name,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return UserOut.model_validate(u)


@router.get("/attendance", response_model=list[AttendanceRow])
def list_attendance(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
    date: Annotated[str | None, Query(description="YYYY-MM-DD, defaults to today UTC")] = None,
) -> list[AttendanceRow]:
    if date:
        try:
            day = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
    else:
        day = datetime.now(timezone.utc).date()

    start = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)

    q = (
        select(AttendanceEvent, User)
        .join(User, AttendanceEvent.user_id == User.id)
        .where(AttendanceEvent.timestamp >= start, AttendanceEvent.timestamp < end)
        .order_by(AttendanceEvent.timestamp.desc())
    )
    rows = db.execute(q).all()
    out: list[AttendanceRow] = []
    for ev, u in rows:
        out.append(
            AttendanceRow(
                id=ev.id,
                user_id=u.id,
                username=u.username,
                full_name=u.full_name,
                event_type=ev.event_type,
                timestamp=ev.timestamp,
            )
        )
    return out
