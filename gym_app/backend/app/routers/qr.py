from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import require_admin
from app.models import User
from app.qr_token import generate_current_token
from app.schemas import QrCurrentResponse

router = APIRouter(prefix="/qr", tags=["qr"])


@router.get("/current", response_model=QrCurrentResponse)
def get_current_qr(_admin: Annotated[User, Depends(require_admin)]) -> QrCurrentResponse:
    token, expires_at = generate_current_token()
    return QrCurrentResponse(token=token, expires_at=expires_at)
