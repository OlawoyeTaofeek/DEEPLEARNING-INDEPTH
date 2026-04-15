from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional, Union, Dict


class Movie(BaseModel):
    movie_id: int
    title: str
    original_language: Optional[str]
    overview: Optional[str] = None
    genres: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    credits: Optional[List[str]] = None
    year: Optional[int]
    popularity: Optional[float]
    budget: Optional[int]
    revenue: Optional[int]
    vote_average: Optional[float]
    vote_count: Optional[int]
    runtime: Optional[int]

class InfoResponse(BaseModel):
    movies_count: int
    sample_movies: List[Movie]

class MovieDetailResponse(BaseModel):
    movie: Movie
    similar_movies: list[Movie]

class RecommendationRequest(BaseModel):
    ...