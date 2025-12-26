from database import SessionLocal
from enums import UserRole
import models.models as models


def can_track_orders(user,order_id : int):
    db = SessionLocal()

    try:
        order = db.query(models.Order).filter(models.Order.id == order_id).first()
        if not order:
            return False

        if user.role == UserRole.admin:
            return True
        if user.role == UserRole.customer:
            order = db.query(models.Order).filter(models.Order.id == order_id).first()
            return order and order.customer_id == user.id
        if user.role == UserRole.agent:
            order = db.query(models.Order).filter(models.Order.id == order_id).first()
            return order and order.agent_id == user.id
        return False
    finally:
        db.close()