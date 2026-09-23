import json
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Load environment variables
load_dotenv()


# File paths
BASE_DIR = Path(__file__).resolve().parent.parent
# Explicitly load .env from project root
load_dotenv(BASE_DIR / ".env")

MOVIES_FILE = BASE_DIR / "data" / "movies.json"
EMBEDDINGS_FILE = BASE_DIR / "data" / "movie_embeddings.npy"


# Load movies
with open(MOVIES_FILE, "r", encoding="utf-8") as file:
    movies = json.load(file)


print(f"Total movies: {len(movies)}")


# Create embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-2"
)


# Prepare text for embedding
movie_texts = []

for movie in movies:

    text = f"""
    Movie Title: {movie["title"]}
    Description: {movie["description"]}
    """

    movie_texts.append(text)


# Generate embeddings
print("Generating embeddings...")

movie_vectors = embeddings.embed_documents(movie_texts)


# Convert to numpy array
movie_vectors = np.array(movie_vectors)


print("Embedding shape:", movie_vectors.shape)


# Save embeddings
np.save(EMBEDDINGS_FILE, movie_vectors)


print("Movie embeddings saved successfully!")
print(f"File: {EMBEDDINGS_FILE}")