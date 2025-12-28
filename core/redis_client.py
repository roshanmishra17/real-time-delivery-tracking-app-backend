import os
import redis.asyncio as redis

_redis = None

async def get_redis():
    global _redis

    REDIS_URL = os.getenv("REDIS_URL")

    if not REDIS_URL:
        return None

    if _redis is None:
        _redis = redis.from_url(
            REDIS_URL,
            decode_responses=True
        )

    return _redis
