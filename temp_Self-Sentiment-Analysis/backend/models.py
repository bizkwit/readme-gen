from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict
from backend.config import settings

class SocialMediaPost(BaseModel):
    platform: str
    timestamp: datetime
    text: str
    author: str
    url: str = None  # Optional URL

class SentimentAnalysisResult(BaseModel):
    timestamp: datetime
    average_sentiment_score: float
    mood_shift: str = None  # e.g., "Positive", "Negative", "Neutral"

class FetchDataRequest(BaseModel):
    platforms: List[str] = settings.SOCIAL_MEDIA_PLATFORMS
    keywords: List[str] = settings.KEYWORDS

class AnalysisResultsResponse(BaseModel):
    results: List[SentimentAnalysisResult]