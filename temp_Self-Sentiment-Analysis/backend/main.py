from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime, timedelta
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import settings
from .models import (
    SocialMediaPost,
    SentimentAnalysisResult,
    FetchDataRequest,
    AnalysisResultsResponse,
)
from .utils import analyze_sentiment, detect_mood_shift

# --- Social Media Data Fetching Modules ---
from . import social_media_fetchers

app = FastAPI()

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory storage for simplicity (replace with a database in production) ---
fetched_data: List[SocialMediaPost] = []
analysis_results: List[SentimentAnalysisResult] = []

# --- Background Task Scheduler ---
scheduler = AsyncIOScheduler()

async def fetch_and_analyze_data():
    global fetched_data, analysis_results
    print("Fetching and analyzing data...")
    new_data = []
    for platform in settings.SOCIAL_MEDIA_PLATFORMS:
        fetcher = getattr(social_media_fetchers, f"fetch_{platform}_data", None)
        if fetcher:
            try:
                platform_data = await fetcher(keywords=settings.KEYWORDS)
                new_data.extend(platform_data)
            except Exception as e:
                print(f"Error fetching data from {platform}: {e}")

    fetched_data.extend(new_data)

    # Perform Sentiment Analysis
    total_sentiment_score = 0
    valid_posts = 0
    for post in new_data:
        sentiment_score = analyze_sentiment(post.text)
        total_sentiment_score += sentiment_score
        valid_posts += 1

    if valid_posts > 0:
        average_sentiment = total_sentiment_score / valid_posts
        previous_result = analysis_results[-1].average_sentiment_score if analysis_results else None
        mood_shift = detect_mood_shift(previous_result, average_sentiment)

        analysis_results.append(
            SentimentAnalysisResult(
                timestamp=datetime.utcnow(),
                average_sentiment_score=average_sentiment,
                mood_shift=mood_shift,
            )
        )
        print(f"Analysis completed. Average sentiment: {average_sentiment}, Mood shift: {mood_shift}")
    else:
        print("No new posts to analyze.")

@app.on_event("startup")
async def startup_event():
    scheduler.add_job(fetch_and_analyze_data, 'interval', seconds=settings.FETCH_INTERVAL_SECONDS)
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()

# --- API Endpoints ---
@app.post("/fetch-data/", response_model=List[SocialMediaPost])
async def fetch_data_manually(request: FetchDataRequest):
    """Manually trigger data fetching (for testing or specific needs)."""
    new_data = []
    for platform in request.platforms:
        fetcher = getattr(social_media_fetchers, f"fetch_{platform}_data", None)
        if fetcher:
            try:
                platform_data = await fetcher(keywords=request.keywords)
                new_data.extend(platform_data)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching from {platform}: {e}")
    return new_data

@app.get("/analysis-results/", response_model=AnalysisResultsResponse)
async def get_analysis_results():
    """Get the latest sentiment analysis results."""
    return {"results": analysis_results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)