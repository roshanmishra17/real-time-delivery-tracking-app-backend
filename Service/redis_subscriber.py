import asyncio
import json
from core.redis_client import get_redis
from ws.manager import manager


async def redis_listener():
    print("Redis listener started")
    redis = await get_redis()
    pubsub = redis.pubsub()
    await pubsub.psubscribe("order:*")

    try:
        async for message in pubsub.listen():
            if message is None:
                await asyncio.sleep(0.01)
                continue

            msg_type = message.get("type")
            if msg_type not in ("message","pmessage"):
                continue
                
            channel = message.get("channel")
            data = message.get("data")

            try:
                payload = json.loads(data)
            except Exception:
                continue

            if "order_id" in payload:
                order_id = int(payload["order_id"])
            else:
                try:
                    order_id = int(channel.split(":")[1])
                except Exception:
                    continue
            
            await manager.broadcast_to_order(order_id,payload)
    finally:
        try:
            await pubsub.unsubscribe()
            await pubsub.close()
        except:
            pass
