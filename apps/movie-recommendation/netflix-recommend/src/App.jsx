import { useState } from "react";
import axios from "axios";

const BASE_URL = import.meta.env.VITE_BASE_URL;
console.log(BASE_URL)
const RECOMMEND_URL = `${BASE_URL}/recommend`;
const SHOW_MORE_URL = `${BASE_URL}/show-more-recommend`;

function truncateWords(text, count) {
  if (!text) return "";
  const words = text.trim().split(/\s+/);
  if (words.length <= count) return text;
  return words.slice(0, count).join(" ");
}

function SimilarityBadge({ value }) {
  const pct = Math.round((value ?? 0) * 100);
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-black/70 border border-netflix-red/60 px-2 py-0.5 text-xs font-semibold text-netflix-red">
      {pct}% match
    </span>
  );
}

function MovieCard({ movie, onClick }) {
  return (
    <button
      onClick={onClick}
      className="group relative flex-shrink-0 w-full text-left rounded-md overflow-hidden bg-[#181818] shadow-lg transition-transform duration-300 hover:scale-105 hover:z-10 hover:shadow-2xl hover:shadow-black/80 focus:outline-none focus:ring-2 focus:ring-netflix-red"
    >
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-neutral-800">
        <img
          src={movie.image}
          alt={movie.title}
          loading="lazy"
          onError={(e) => {
            e.currentTarget.src =
              "https://via.placeholder.com/300x450/181818/E50914?text=No+Image";
          }}
          className="h-full w-full object-cover"
        />
        <div className="absolute top-2 right-2">
          <SimilarityBadge value={movie.similarity} />
        </div>
        <div className="absolute inset-0 bg-gradient-to-t from-black via-black/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <div className="p-3">
        <h3 className="font-bold text-sm truncate">{movie.title}</h3>
        <p className="mt-1 text-xs text-neutral-400">
          {truncateWords(movie.description, 5)}
          <span className="text-netflix-red font-semibold">...see more</span>
        </p>
      </div>
    </button>
  );
}

function MovieRow({ title, movies, onSelect }) {
  if (!movies || movies.length === 0) return null;
  return (
    <div className="mb-8">
      <h2 className="text-lg md:text-xl font-bold mb-3 px-1">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {movies.map((m, i) => (
          <MovieCard key={`${m.title}-${i}`} movie={m} onClick={() => onSelect(m)} />
        ))}
      </div>
    </div>
  );
}

function MovieModal({ movie, onClose, moreMovies, moreLoading, onSelectMore }) {
  if (!movie) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/80 p-3 md:p-6 overflow-y-auto"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-2xl bg-[#181818] rounded-lg overflow-hidden shadow-2xl my-6"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-3 right-3 z-10 h-9 w-9 rounded-full bg-black/70 hover:bg-black text-white flex items-center justify-center text-lg font-bold"
        >
          ✕
        </button>

        <div className="relative w-full aspect-video bg-neutral-800">
          <img
            src={movie.image}
            alt={movie.title}
            onError={(e) => {
              e.currentTarget.src =
                "https://via.placeholder.com/800x450/181818/E50914?text=No+Image";
            }}
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#181818] via-black/20 to-transparent" />
        </div>

        <div className="p-5 md:p-6">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-2xl font-extrabold">{movie.title}</h2>
            <SimilarityBadge value={movie.similarity} />
          </div>
          <p className="mt-3 text-sm leading-relaxed text-neutral-200">
            {movie.description}
          </p>
          <div className="mt-4 text-xs text-neutral-500">
            Similarity score: {movie.similarity}
          </div>
        </div>

        <div className="px-5 md:px-6 pb-6">
          <h3 className="text-base font-bold mb-3 text-neutral-200">More Like This</h3>
          {moreLoading && (
            <p className="text-sm text-neutral-400">Loading recommendations...</p>
          )}
          {!moreLoading && moreMovies && moreMovies.length > 0 && (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {moreMovies.map((m, i) => (
                <MovieCard
                  key={`more-${m.title}-${i}`}
                  movie={m}
                  onClick={() => onSelectMore(m)}
                />
              ))}
            </div>
          )}
          {!moreLoading && moreMovies && moreMovies.length === 0 && (
            <p className="text-sm text-neutral-500">No further recommendations found.</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState([]);
  const [searchedOnce, setSearchedOnce] = useState(false);

  const [selectedMovie, setSelectedMovie] = useState(null);
  const [moreMovies, setMoreMovies] = useState([]);
  const [moreLoading, setMoreLoading] = useState(false);

  async function handleSearch(e) {
    e?.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setSearchedOnce(true);
    try {
      const res = await axios.post(RECOMMEND_URL, {
        query: query.trim(),
        top_k: 3,
      });
      setResults(res.data?.recommendations ?? []);
    } catch (err) {
      console.error(err);
      setError(
        "Couldn't reach the recommendation server. Make sure it's running at " +
          RECOMMEND_URL
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function openMovie(movie) {
    setSelectedMovie(movie);
    setMoreMovies([]);
    setMoreLoading(true);
    try {
      const res = await axios.post(SHOW_MORE_URL, {
        query:movie.title,
        top_k: 3,
        exclude_title:movie.title
      });
      setMoreMovies(res.data?.recommendations ?? []);
    } catch (err) {
      console.error(err);
      setMoreMovies([]);
    } finally {
      setMoreLoading(false);
    }
  }

  function closeModal() {
    setSelectedMovie(null);
    setMoreMovies([]);
  }

  return (
    <div className="min-h-screen bg-netflix-black text-white">
      {/* Header / Hero */}
      <header className="relative">
        <div className="absolute inset-0 bg-gradient-to-b from-black/80 via-black/40 to-netflix-black" />
        <div className="relative px-5 md:px-12 pt-6 pb-16 md:pb-24">
          <div className="flex items-center justify-between">
            <h1 className="text-netflix-red text-3xl md:text-4xl font-black tracking-tight">
              MOVIEFLIX
            </h1>
          </div>

          <div className="mt-16 md:mt-24 max-w-2xl flex flex-col justify-center">
            <h2 className="text-2xl md:text-4xl font-extrabold leading-tight">
              Unlimited movies, picked just for you.
            </h2>
            <p className="mt-3 text-neutral-300 text-sm md:text-base">
              Tell us what you're in the mood for, and we'll find your next watch.
            </p>

            <form
              onSubmit={handleSearch}
              className="mt-6 flex flex-col sm:flex-row gap-3 w-full"
            >
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g. I want to watch sci-fi space movies"
                className="flex-1 rounded-md bg-black/60 border border-neutral-600 px-4 py-3 text-sm md:text-base placeholder-neutral-500 focus:outline-none focus:border-netflix-red focus:ring-1 focus:ring-netflix-red"
              />
              <button
                type="submit"
                disabled={loading}
                className="rounded-md bg-netflix-red hover:bg-red-700 disabled:opacity-60 disabled:cursor-not-allowed px-6 py-3 text-sm md:text-base font-bold transition-colors"
              >
                {loading ? "Searching..." : "Search"}
              </button>
            </form>
          </div>
        </div>
      </header>

      {/* Results */}
      <main className="px-5 md:px-12 pb-16 -mt-6 md:-mt-10">
        {error && (
          <div className="mb-6 rounded-md border border-netflix-red/50 bg-netflix-red/10 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}

        {loading && (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div
                key={i}
                className="aspect-[2/3] rounded-md bg-neutral-800 animate-pulse"
              />
            ))}
          </div>
        )}

        {!loading && results.length > 0 && (
          <MovieRow title="Recommended For You" movies={results} onSelect={openMovie} />
        )}

        {!loading && !error && searchedOnce && results.length === 0 && (
          <p className="text-neutral-400 text-sm">
            No recommendations found. Try a different search.
          </p>
        )}

        {!searchedOnce && !loading && (
          <p className="text-neutral-500 text-sm">
            Search above to get personalized movie recommendations.
          </p>
        )}
      </main>

      <MovieModal
        movie={selectedMovie}
        onClose={closeModal}
        moreMovies={moreMovies}
        moreLoading={moreLoading}
        onSelectMore={openMovie}
      />
    </div>
  );
}
