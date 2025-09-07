# Redis Cache

This repository demonstrates caching strategies using Redis with both Python (FastAPI) and JavaScript (Express) servers.

## Folder Structure

```
JS Server/
  .env
  package.json
  src/
    db.js
    index.js
    redis.js

Python Server/
  .env
  requirements.txt
  src/
    db.py
    main.py
    redis_client.py
```

## Prerequisites

- [Redis](https://redis.io/) running locally (`redis://127.0.0.1:6379`)
- Node.js (for JS Server)
- Python 3.10+ (for Python Server)

---

## Python Server Setup

1. **Install dependencies:**
   ```sh
   cd "Python Server"
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   - Edit `.env` if needed (default Redis URL and port are set).

3. **Run the server:**
   ```sh
   uvicorn src.main:app --reload --host 0.0.0.0 --port 3000
   ```

---

## JS Server Setup

1. **Install dependencies:**
   ```sh
   cd "JS Server"
   npm install
   ```

2. **Configure environment:**
   - Edit `.env` if needed.

3. **Run the server:**
   ```sh
   npm run dev
   # or
   npm start
   ```

---

## API Endpoints

### Python Server

- `GET /health` – Health check
- `GET /movies/{id}` – Get movie (with Redis string cache)
- `POST /movies` – Create/update movie (invalidates cache)
- `PATCH /users/{id}` – Update user profile (Redis hash)
- `GET /users/{id}` – Get user profile
- `POST /leaderboard/score` – Update leaderboard score (Redis sorted set)
- `GET /leaderboard/top/{n}` – Get top N leaderboard
- `DELETE /cache/{key}` – Delete cache key

---

## Environment Variables

Both servers use `.env` files for configuration:
- `PORT` – Server port
- `REDIS_URL` – Redis connection string
- `DB_DELAY_MS` – Simulated DB latency (Python server)

---