from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from app.recommender import MovieRecommender


app = FastAPI(
    title="Movie Recommendation API",
    description="Embedding based movie recommendation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)

# Load recommender once when server starts
recommender = MovieRecommender()


class RecommendationRequest(BaseModel):

    query: str
    top_k: int = 5
    exclude_title:str = None 


@app.get("/")
def home():

    return {
        "message": "Movie Recommendation API is running"
    }


@app.post("/recommend")
def recommend_movies(request: RecommendationRequest):

    # Validate query
    if not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )


    # Limit top_k
    if request.top_k < 1 or request.top_k > 20:

        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20"
        )


    # Get recommendations
    recommendations = recommender.recommend(
        query=request.query,
        top_k=request.top_k
    )


    return {
        "query": request.query,
        "count": len(recommendations),
        "recommendations": recommendations
    }

# show-more-recommend
@app.post("/show-more-recommend")
def recommend_movies_when_click(request: RecommendationRequest):

    # Validate query
    if not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )


    # Limit top_k
    if request.top_k < 1 or request.top_k > 20:

        raise HTTPException(
            status_code=400,
            detail="top_k must be between 1 and 20"
        )


    # Get recommendations
    recommendations = recommender.recommend(
        query=request.query,
        top_k=request.top_k,
        exclude_title=request.exclude_title,
    )


    return {
        "query": request.query,
        "count": len(recommendations),
        "recommendations": recommendations
    }