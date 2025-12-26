
from enums import OrderStatus
import models.models as models
from sqlalchemy.orm import Session

def  create_order(db : Session,customer_id : int,data):
    order = models.Order(
        customer_id = customer_id,
        pickup_add = data.pickup_add,
        pickup_lat = data.pickup_lat,
        pickup_lng = data.pickup_lng,
        drop_add = data.drop_add,
        drop_lat=data.drop_lat,
        drop_lng=data.drop_lng
    )

    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def assign_agent(db : Session,order_id : int,agent_id : int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        return None
    
    order.agent_id = agent_id
    order.status = OrderStatus.assigned

    db.commit()
    db.refresh(order)
    return order

def update_status(db : Session,order_id : int,status:OrderStatus):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order is None:
        return None
    
    order.status = status

    db.commit()
    db.refresh(order)
    return order

def get_customer_order(db : Session,customer_id : int):
    return(
        db.query(models.Order)
        .filter(models.Order.customer_id == customer_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )

def get_agent_orders(db: Session, agent_id: int):
    return (
        db.query(models.Order)
        .filter(models.Order.agent_id == agent_id)
        .order_by(models.Order.created_at.desc())
        .all()
    )

def get_all_order(db : Session):
    return (
        db.query(models.Order)
        .order_by(models.Order.created_at.desc())
        .all()
    )
