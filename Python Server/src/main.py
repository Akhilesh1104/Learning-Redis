# src/main.py
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv

load_dotenv()

from redis_client import redis, ping_redis
from db import get_movie_by_id, upsert_movie

app = FastAPI()

# Startup: ensure Redis is reachable
@app.on_event("startup")
async def startup():
    await ping_redis()

# -------------------------
# Health
# -------------------------
@app.get("/health")
async def health():
    return {"ok": True}

# -------------------------
# 1) STRING cache (movies)
# -------------------------
@app.get("/movies/{id}")
async def get_movie(id: str):
    cache_key = f"movie:{id}"
    cached = await redis.get(cache_key)
    if cached:
        return {"source": "cache", "data": json.loads(cached)}

    movie = await get_movie_by_id(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Not found")

    await redis.set(cache_key, json.dumps(movie), ex=60)
    return {"source": "db", "data": movie}

class MovieIn(BaseModel):
    id: str
    title: str
    year: int

@app.post("/movies", status_code=201)
async def create_movie(payload: MovieIn):
    movie = await upsert_movie(payload.dict())
    await redis.delete(f"movie:{movie['id']}")  # invalidate cache
    return {"ok": True, "data": movie}

# -------------------------
# 2) HASH – user profiles
# -------------------------
@app.patch("/users/{id}")
async def patch_user(id: str, payload: Dict[str, Any] = Body(...)):
    key = f"user:{id}"
    if not payload or not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Provide at least one field")

    mapping = {k: ("true" if v is True else "false" if v is False else str(v))
               for k, v in payload.items()}

    await redis.hset(key, mapping)
    await redis.expire(key, 600)

    data = await redis.hgetall(key)
    for k, v in list(data.items()):
        if v == "true": data[k] = True
        elif v == "false": data[k] = False

    ttl = await redis.ttl(key)
    return {"key": key, "data": data, "ttl_seconds": ttl}

@app.get("/users/{id}")
async def get_user(id: str):
    key = f"user:{id}"
    data = await redis.hgetall(key)
    if not data:
        raise HTTPException(status_code=404, detail="User hash not found")

    for k, v in list(data.items()):
        if v == "true": data[k] = True
        elif v == "false": data[k] = False

    ttl = await redis.ttl(key)
    return {"key": key, "data": data, "ttl_seconds": ttl}

# -------------------------
# 3) SORTED SET – leaderboard
# -------------------------
class ScoreIn(BaseModel):
    userId: str
    delta: float

@app.post("/leaderboard/score")
async def leaderboard_score(payload: ScoreIn):
    member = f"user:{payload.userId}"
    new_score = await redis.zincrby("lb:global", payload.delta, member)
    rank = await redis.zrevrank("lb:global", member)
    return {
        "userId": payload.userId,
        "score": float(new_score),
        "rank": rank + 1 if rank is not None else None
    }

@app.get("/leaderboard/top/{n}")
async def leaderboard_top(n: int):
    n = max(1, min(100, n))
    raw = await redis.zrevrange("lb:global", 0, n - 1, withscores=True)
    result = [
        {"member": m, "userId": m.replace("user:", ""), "score": float(s), "rank": i+1}
        for i, (m, s) in enumerate(raw)
    ]
    return {"top": result}

# -------------------------
# Cache delete
# -------------------------
@app.delete("/cache/{key}")
async def delete_cache(key: str):
    deleted = await redis.delete(key)
    return {"deleted": deleted}

# -------------------------
# Main entrypoint
# -------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port, reload=True)
