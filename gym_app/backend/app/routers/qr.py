from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import require_admin
from app.models import School, User
from app.qr_svg import token_to_svg
from app.qr_token import generate_current_token
from app.schemas import QrCurrentResponse

router = APIRouter(prefix="/qr", tags=["qr"])


@router.get("/current", response_model=QrCurrentResponse)
def get_current_qr(
    admin: Annotated[User, Depends(require_admin)],
    db: Annotated[Session, Depends(get_db)],
) -> QrCurrentResponse:
    school = db.get(School, admin.school_id)
    if school is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="School not found")
    token, expires_at = generate_current_token(
        gym_id=str(school.id),
        qr_secret=school.qr_secret,
    )
    return QrCurrentResponse(
        token=token,
        expires_at=expires_at,
        qr_svg=token_to_svg(token),
    )
