from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_student
from app.models import AttendanceEvent, School, User
from app.network_policy import require_scan_from_allowed_network
from app.qr_token import verify_token
from app.schemas import ScanRequest, ScanResponse

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.post("/scan", response_model=ScanResponse)
def scan(
    request: Request,
    body: ScanRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_student)],
) -> ScanResponse:
    require_scan_from_allowed_network(request)
    school = db.get(School, user.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="School not found")
    if not verify_token(
        body.qr_token.strip(),
        gym_id=str(school.id),
        qr_secret=school.qr_secret,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired QR token",
        )

    last = db.scalar(
        select(AttendanceEvent)
        .where(AttendanceEvent.user_id == user.id)
        .order_by(AttendanceEvent.timestamp.desc())
        .limit(1)
    )
    if last is None or last.event_type == "out":
        new_type = "in"
    else:
        new_type = "out"

    ev = AttendanceEvent(user_id=user.id, event_type=new_type)
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ScanResponse(event_type=new_type, timestamp=ev.timestamp)
