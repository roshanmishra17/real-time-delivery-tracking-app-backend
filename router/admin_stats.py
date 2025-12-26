from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from enums import UserRole
import models.models as models
from oauth import get_current_user
from sqlalchemy import func



router = APIRouter(prefix="/admin", tags=["Admin"])


def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/stats")
def admin_stats(admin=Depends(require_admin), db: Session = Depends(get_db)):
    total_orders = db.query(models.Order).count()
    total_agents = db.query(models.User).filter(models.User.role == UserRole.agent).count()
    total_customers = db.query(models.User).filter(models.User.role == UserRole.customer).count()

    status_counts = (
        db.query(models.Order.status, func.count(models.Order.id))
        .group_by(models.Order.status)
        .all()
    )

    stats = {s: c for s, c in status_counts}

    return {
        "total_orders": total_orders,
        "total_agents": total_agents,
        "total_customers": total_customers,
        "status_counts": stats
    }