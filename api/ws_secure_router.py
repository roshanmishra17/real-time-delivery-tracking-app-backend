import asyncio
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from Service.ws_permission import can_track_orders
from core.jwt_helper import get_user_from_token
from database import SessionLocal
from ws.manager import manager

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
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        await manager.disconnect(order_id, websocket)

        