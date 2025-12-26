from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import UserOut
from database import get_db
from enums import UserRole
import models.models as models
from oauth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/agents")
def get_all_agents(
    admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    agents = db.query(models.User).filter(models.User.role == UserRole.agent).all()
    return agents
