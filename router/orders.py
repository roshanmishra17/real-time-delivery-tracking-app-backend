from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from database import get_db
from enums import UserRole
from location_helper import get_last_location_for_order
import models.models as models
from oauth import get_current_user
from schemas import OrderAssign, OrderCreate, OrderResponse, OrderStatus,OrderUpdateStatus
from services import assign_agent, create_order, get_agent_orders, get_all_order, get_customer_order, update_status

router = APIRouter(prefix='/order',tags=['Orders'])


@router.post('/',response_model=OrderResponse)
def create_new_order(payload : OrderCreate,db : Session = Depends(get_db),current_user = Depends(get_current_user)):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only customers can create orders")

    order = create_order(db, customer_id=current_user.id, data=payload)
    return order

@router.post("/{order_id}/assign",response_model=OrderResponse)
def assign_order(
    order_id : int,
    payload : OrderAssign,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    order = assign_agent(db,order_id,payload.agent_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order

@router.put('/{order_id}/status',response_model=OrderResponse)
def update_order_status(
    order_id : int,
    payload : OrderUpdateStatus,
    db : Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != UserRole.agent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent access required")

    order = update_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.agent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This order is not assigned to you")

    return order

@router.get('/my',response_model=List[OrderResponse])
def get_my_orders(db : Session = Depends(get_db),current_user = Depends(get_current_user)):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail = "Only customers can view their orders")

    return get_customer_order(db, current_user.id)

@router.get('/assigned',response_model=List[OrderResponse])
def get_assigned_orders(db: Session = Depends(get_db),current_user = Depends(get_current_user)):
    if current_user.role != UserRole.agent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail = "Only delivery agents can view assigned orders")

    return get_agent_orders(db, current_user.id)

@router.get("/", response_model=list[OrderResponse])
def admin_get_all_orders(db: Session = Depends(get_db),current_user = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail = "Admin access required")

    return get_all_order(db)

@router.get("/recent")
def recent_orders(
    limit: int = 5,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    orders = (
        db.query(models.Order)
        .order_by(models.Order.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "order_id": o.id,
            "status": o.status,
            "created_at": o.created_at
        }
        for o in orders
    ]


@router.get("/{order_id}")
def get_order_details(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.role == UserRole.customer and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    if current_user.role == UserRole.agent and order.agent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="this order is not assigned to you")

    last_loc = get_last_location_for_order(db, order_id)

    latest_location = None
    if last_loc:
        latest_location = {
            "lat": last_loc.lat,
            "lng": last_loc.lng,
            "timestamp": last_loc.timestamp.isoformat()
        }

    agent_data = None

    if order.agent:
        agent_data = {
            "id": order.agent.id,
            "name": order.agent.name,
            "email": order.agent.email
        }

    return {
        "order_id": order.id,
        "status": order.status.value,
        "pickup": {
            "address": order.pickup_add,
            "lat": order.pickup_lat,
            "lng": order.pickup_lng
        },
        "drop": {
            "address": order.drop_add,
            "lat": order.drop_lat,
            "lng": order.drop_lng
        },
        "customer": {
            "id": order.customer_id
        },
        "agent": agent_data,
        "latest_location": latest_location,
        "created_at": order.created_at.isoformat()
    }
@router.get("/{order_id}/latest-location")
def get_latest_location(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Permissions
    if current_user.role == UserRole.customer and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    if current_user.role == UserRole.agent and order.agent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="this order is not assigned to you")

    loc = get_last_location_for_order(db, order_id)
    if not loc:
        return {"latest_location": None}

    return {
        "latest_location": {
            "lat": loc.lat,
            "lng": loc.lng,
            "timestamp": loc.timestamp.isoformat()
        }
    }
