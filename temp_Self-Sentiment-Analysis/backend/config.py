import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    SOCIAL_MEDIA_PLATFORMS = ["twitter", "reddit"]  # Add more as needed
    TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
    TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
    FETCH_INTERVAL_SECONDS = 60 * 5  # Fetch every 5 minutes
    KEYWORDS = ["your product", "your competitor"]  # Keywords to track

settings = Settings()