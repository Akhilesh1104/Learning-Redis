# src/redis.py
from dotenv import load_dotenv
import os
from redis.asyncio import Redis

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")

# decode_responses=True so we get str instead of bytes
redis = Redis.from_url(REDIS_URL, decode_responses=True)

async def ping_redis():
    try:
        await redis.ping()
        print("✅ Redis connected")
    except Exception as e:
        print("❌ Redis connection error:", e)
        raise
