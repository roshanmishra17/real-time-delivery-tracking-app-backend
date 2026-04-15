import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from core.distance import haversine
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

            print("Received:", data) 

            if data.get("type") == "ping":
                continue

            agent_lat = data.get("lat")
            agent_lng = data.get("lng")

            if agent_lat is None or agent_lng is None:
                continue

            await manager.broadcast_to_order(order_id, {
                "lat": agent_lat,
                "lng": agent_lng
            })

            db = SessionLocal()
            try:
                order = db.query(Order).filter(Order.id == order_id).first()

                if not order:
                    continue

                drop_lat = order.drop_lat
                drop_lng = order.drop_lng

                distance = haversine(agent_lat, agent_lng, drop_lat, drop_lng)

                print("Distance:", distance)

                if distance < 200 and order.status != "delivered":
                    order.status = "delivered"
                    db.commit()

                    print("✅ Delivered!")

                    await manager.broadcast_to_order(order_id, {
                        "type": "ORDER_UPDATE",
                        "status": "delivered"
                    })

            finally:
                db.close()
    except WebSocketDisconnect:
        await manager.disconnect(order_id, websocket)

        