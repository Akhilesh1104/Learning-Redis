# src/db.py
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
DB_DELAY_MS = int(os.getenv("DB_DELAY_MS", "600"))

# in-memory fake DB
_MOVIES = {
    "1": {"id": "1", "title": "Inception", "year": 2010},
    "2": {"id": "2", "title": "Interstellar", "year": 2014},
}

async def get_movie_by_id(movie_id: str):
    # simulate DB latency
    await asyncio.sleep(DB_DELAY_MS / 1000)
    return _MOVIES.get(str(movie_id))

async def upsert_movie(movie: dict):
    await asyncio.sleep(0.1)  # small write latency
    movie_id = str(movie["id"])
    movie["id"] = movie_id
    _MOVIES[movie_id] = movie
    return movie
