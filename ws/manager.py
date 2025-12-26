import asyncio
from typing import Dict, Set
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self.active: Dict[int, list[WebSocket]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self,order_id : int,websocket : WebSocket):
        async with self._lock:
            conns = self.active.setdefault(order_id,set())
            conns.add(websocket)

    async def disconnect(self,order_id : int,websocket : WebSocket):
        async with self._lock:
            conns = self.active.get(order_id)
            if not conns:
                return 
            conns.discard(websocket)
            if not conns:
                self.active.pop(order_id,None)

    async def broadcast_to_order(self,order_id : int,message : dict):
        async with self._lock:
            conns = list(self.active.get(order_id,set()))
        for ws in conns:
            try:
                await ws.send_json(message)
            except:
                pass
        
manager = WebSocketManager()