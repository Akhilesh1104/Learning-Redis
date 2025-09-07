import "dotenv/config.js";
import express from "express";
import morgan from "morgan";
import redis from "./redis.js";
import { getMovieById, upsertMovie } from "./db.js";

const app = express();
app.use(express.json());
app.use(morgan("dev"));

// ---- Health ----
app.get("/health", (req, res) => res.json({ ok: true }));

// =====================
// 1) STRING cache (movies)
// =====================
app.get("/movies/:id", async (req, res) => {
  const id = req.params.id;
  const cacheKey = `movie:${id}`;
  const cached = await redis.get(cacheKey);

  if (cached) {
    return res.json({ source: "cache", data: JSON.parse(cached) });
  }

  const movie = await getMovieById(id);
  if (!movie) return res.status(404).json({ error: "Not found" });

  await redis.set(cacheKey, JSON.stringify(movie), "EX", 60);
  res.json({ source: "db", data: movie });
});

app.post("/movies", async (req, res) => {
  const { id, title, year } = req.body;
  if (!id || !title || !year) {
    return res.status(400).json({ error: "id, title, year required" });
  }

  const movie = await upsertMovie({ id: String(id), title, year: Number(year) });
  await redis.del(`movie:${movie.id}`);
  res.status(201).json({ ok: true, data: movie });
});

// =====================
// 2) HASH (user profiles)
// =====================
app.patch("/users/:id", async (req, res) => {
  const key = `user:${req.params.id}`;
  const updates = {};
  for (const [k, v] of Object.entries(req.body)) {
    updates[k] = String(v);
  }

  await redis.hset(key, updates);
  await redis.expire(key, 600);

  const data = await redis.hgetall(key);
  res.json({ key, data });
});

app.get("/users/:id", async (req, res) => {
  const key = `user:${req.params.id}`;
  const data = await redis.hgetall(key);
  if (!data || Object.keys(data).length === 0) {
    return res.status(404).json({ error: "User not found" });
  }
  res.json({ key, data });
});

// =====================
// 3) SORTED SET (leaderboard)
// =====================
app.post("/leaderboard/score", async (req, res) => {
  const { userId, delta } = req.body;
  if (!userId || delta === undefined) {
    return res.status(400).json({ error: "userId and delta required" });
  }

  const member = `user:${userId}`;
  const score = await redis.zincrby("lb:global", Number(delta), member);
  const rank = await redis.zrevrank("lb:global", member);
  res.json({ userId, score: Number(score), rank: rank + 1 });
});

app.get("/leaderboard/top/:n", async (req, res) => {
  const n = parseInt(req.params.n) || 10;
  const raw = await redis.zrevrange("lb:global", 0, n - 1, "WITHSCORES");

  const result = [];
  for (let i = 0; i < raw.length; i += 2) {
    result.push({
      userId: raw[i].replace("user:", ""),
      score: Number(raw[i + 1]),
      rank: i / 2 + 1
    });
  }
  res.json({ top: result });
});

// ---- Error handler ----
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).json({ error: err.message });
});

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`🚀 Server running at http://localhost:${port}`));
