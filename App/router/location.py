from datetime import datetime, timezone
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from core.distance import haversine
from core.redis_client import get_redis
from database import get_db
from enums import UserRole
from location_helper import get_location_history, save_location
import models.models as models
from oauth import get_current_user
from schemas import LocationResponse, LocationUpdate
from location_helper import get_last_location_for_order


router = APIRouter(prefix='/location',tags=['Location'])

MIN_TIME_SEC = 3
MIN_DIST_METERS = 10

@router.post('/update')
async def update_location(payload : LocationUpdate,db : Session = Depends(get_db),current_user = Depends(get_current_user)):
    if current_user.role != UserRole.agent:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Only delivery agents can send location")
    
    order = db.query(models.Order).filter(models.Order.id == payload.order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Order not found")
    
    # print(order.agent_id)
    # print(current_user.id)

    if order.agent_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail = "This order is not assigned to you")
    
    last = get_last_location_for_order(db,payload.order_id)
    now = datetime.now(timezone.utc)

    if last:
        dt = (now-last.timestamp).total_seconds()
        if dt < MIN_TIME_SEC:
            return {"status" : "ignored","reason" : "too_fast"}
        
        dist = haversine(last.lat,last.lng,payload.lat,payload.lng)
        if dist < MIN_DIST_METERS:
            return {"status": "ignored", "reason": "too_close"}

    loc = save_location(
        db,
        agent_id=current_user.id,
        order_id=payload.order_id,
        lat=payload.lat,
        lng=payload.lng,
    )

    redis = await get_redis()
    data = {
        "order_id" : payload.order_id,
        "agent_id" : current_user.id,
        "lat": payload.lat,
        "lng": payload.lng,
        "timestamp" : loc.timestamp.isoformat()
    }
    
    await redis.publish(f"order:{payload.order_id}", json.dumps(data))

    return {"status": "ok", "saved": True}



@router.get("/{order_id}/history",response_model=List[LocationResponse])
def get_history(order_id : int,db : Session = Depends(get_db),current_user = Depends(get_current_user)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order Not Found")

    if(current_user.role == UserRole.customer and order.customer_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Your Order")
    
    if (current_user.role == UserRole.agent and order.agent_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not Your Order")

    history = get_location_history(db, order_id)
    return history