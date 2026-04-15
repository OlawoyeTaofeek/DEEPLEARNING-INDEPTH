## FastAPI endpoints

from fastapi import FastAPI, HTTPException
from schema import InfoResponse, Movie, MovieDetailResponse, MovieDetailResponse
from helpers import connect_to_weaviate, CollectionName, CollectionPageSize
from weaviate.classes.query import Filter

app = FastAPI(
    title="MovieInsights API",
    description="A movie discovery and recommendation platform using Weaviate",
    version="0.1.0",
)

PAGE_SIZE = CollectionPageSize.PAGE_SIZE

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "MovieInsights API - Powered by Weaviate",
        "version": "1.0.0",
        "endpoints": [
            "/info - Get basic information about the dataset",
            "/search - Search movies by text",
            "/movie/{movie_id} - Get movie details and similar movies",
            "/explore - Explore movies by genre and year",
            "/recommend - Get movie recommendations for occasions",
        ],
    }

@app.get("/info", response_model=InfoResponse)
def get_dataset_info():
    """
    Get basic information about the dataset
    - Total movie count
    - Some example movies
    """
    try:
        with connect_to_weaviate() as client:
            movies = client.collections.use(CollectionName.MOVIES)
            movies_count = len(movies)
            sample_movies_response = movies.query.fetch_objects(limit=5).objects
            sample_movies = [o.properties for o in sample_movies_response]

        return InfoResponse(movies_count=movies_count, sample_movies=sample_movies)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
@app.get("/movies/{movie_id}", response_model=MovieDetailResponse)
async def get_movie(movie_id: str):
    """
    Get detailed information about a specific movie by its ID
    """
    try:
        with connect_to_weaviate() as client:
            movies = client.collections.use(CollectionName.MOVIES)
            movie = movies.query.fetch_objects(
                filters=Filter.by_property("movie_id").equal(int(movie_id)),
                limit=1
            ).objects
            if len(movie) == 0:
                raise HTTPException(status_code=404, detail="Movie not found")

            movie_data = movie[0].properties
            response = movies.query.near_object(
                near_object=movie[0].uuid, target_vector="default", limit=PAGE_SIZE
            )
            similar_movies = [o.properties for o in response.objects[1:]]
            return MovieDetailResponse(movie=Movie(**movie_data), similar_movies=similar_movies)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")