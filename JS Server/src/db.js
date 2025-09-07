const delay = (ms) => new Promise((r) => setTimeout(r, ms));
const DB_DELAY_MS = Number(process.env.DB_DELAY_MS || 600);

const MOVIES = {
  "1": { id: "1", title: "Inception", year: 2010 },
  "2": { id: "2", title: "Interstellar", year: 2014 }
};

export async function getMovieById(id) {
  await delay(DB_DELAY_MS);
  return MOVIES[id] || null;
}

export async function upsertMovie(movie) {
  await delay(100);
  MOVIES[movie.id] = movie;
  return movie;
}
