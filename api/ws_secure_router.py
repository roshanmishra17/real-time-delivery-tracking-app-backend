import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from Service.ws_permission import can_track_orders
from core.jwt_helper import get_user_from_token
from database import SessionLocal
from ws.manager import manager
from models.models import Order
router = APIRouter(prefix="/ws", tags=["Test WS"])

@router.websocket("/track/{order_id}")
async def ws_track_order(websocket : WebSocket,order_id : int,token : str = Query(None)):

    if not token:
        await websocket.close(code=1008)
        return
    
    user = get_user_from_token(token)

    if not user:        
        await websocket.close(code=1008)
        return
    
    db = SessionLocal()
    allowed = can_track_orders(user,order_id)
    db.close()
    if not allowed:
        await websocket.close(code=1008)
        return
    
    await websocket.accept()

    await manager.connect(order_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "ping":
                continue

            agent_lat = data.get("lat")
            agent_lng = data.get("lng")

            if not agent_lat or not agent_lng:
                continue

            db = SessionLocal()
            order = db.query(Order).filter(Order.id == order_id).first()

            if not order:
                db.close()
                continue

            drop_lat = order.drop_lat
            drop_lng = order.drop_lng

            distance = ((agent_lat - drop_lat)**2 + (agent_lng - drop_lng)**2)**0.5

            print("Distance:", distance)

            if distance < 0.0005 and order.status != "delivered":
                order.status = "delivered"
                db.commit()

                await manager.broadcast_to_order(order_id, {
                    "type": "ORDER_UPDATE",
                    "status": "delivered"
                })
    except WebSocketDisconnect:
        await manager.disconnect(order_id, websocket)

        