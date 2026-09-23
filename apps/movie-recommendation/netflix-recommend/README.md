# MovieFlix Recommender

A single-page React + Vite app with a Netflix-style UI that calls your local
movie recommendation API.

## Setup

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually http://localhost:5173).

Make sure your recommendation API is running at:
- `POST http://127.0.0.1:8000/recommend`
- `POST http://127.0.0.1:8000/show-more-recommend`

both expecting a body like:

```json
{ "query": "I want to watch sci-fi space movies", "top_k": 3 }
```

## How it works

- The hero search bar at the top sends the typed query to `/recommend`
  (`top_k: 3`) and renders the results as a Netflix-style card row.
- Each card shows the poster image, title, a similarity "match" badge, and a
  short 5-word description teaser ending in "...see more".
- Clicking a card opens a full-screen modal with the complete description and
  similarity score, and immediately calls `/show-more-recommend` with the
  same request body, showing those results as a "More Like This" row at the
  bottom of the modal — clicking one of those swaps the modal to that movie
  and fetches more recommendations again, just like Netflix's related-titles
  flow.

## Notes

- If the API is unreachable (e.g. CORS not enabled on the FastAPI/Flask
  server, or it isn't running), an error banner is shown. If you hit a CORS
  error in the browser console, enable CORS on your backend for
  `http://localhost:5173`.
- Styling is done entirely with Tailwind CSS utility classes.
