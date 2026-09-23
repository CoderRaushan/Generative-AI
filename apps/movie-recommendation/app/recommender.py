import json
import numpy as np
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env explicitly
load_dotenv(BASE_DIR / ".env")

MOVIES_FILE = BASE_DIR / "data" / "movies.json"
EMBEDDINGS_FILE = BASE_DIR / "data" / "movie_embeddings.npy"


class MovieRecommender:

    def __init__(self):

        # Load movies
        with open(MOVIES_FILE, "r", encoding="utf-8") as file:
            self.movies = json.load(file)

        # Load pre-generated movie embeddings
        self.movie_embeddings = np.load(EMBEDDINGS_FILE)

        # Embedding model
        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2"
        )

        print("Movie recommender loaded.")
        print(f"Movies: {len(self.movies)}")
        print(f"Embeddings: {self.movie_embeddings.shape}")


    def recommend(self, query: str, top_k: int = 3, exclude_title:str | None = None):

        # Generate embedding for user's query
        query_embedding = self.embedding_model.embed_query(query)

        # Convert to numpy
        query_embedding = np.array(query_embedding)

        # Calculate cosine similarity
        similarities = self.cosine_similarity(
            query_embedding,
            self.movie_embeddings
        )

        # Get indexes of highest similarity
        top_indexes = np.argsort(similarities)[::-1][:top_k]

        # Create response
        recommendations = []

        for index in top_indexes:

            movie = self.movies[index]

              # Skip clicked movie
            if exclude_title and movie["title"].lower() == exclude_title.lower():
                continue

            recommendations.append({
                "title": movie["title"],
                "description": movie["description"],
                "image":movie["image"],
                "similarity": round(float(similarities[index]), 4)
            })

        return recommendations


    def cosine_similarity(self, query_vector, movie_vectors):

        # Dot product
        dot_product = np.dot(movie_vectors, query_vector)

        # Magnitudes
        movie_norms = np.linalg.norm(movie_vectors, axis=1)

        query_norm = np.linalg.norm(query_vector)

        # Cosine similarity
        similarity = dot_product / (
            movie_norms * query_norm
        )

        return similarity