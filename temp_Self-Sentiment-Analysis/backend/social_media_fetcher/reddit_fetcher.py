from typing import List
import praw
from datetime import datetime
from ..config import settings
from ..models import SocialMediaPost

async def fetch_reddit_data(keywords: List[str]) -> List[SocialMediaPost]:
    reddit = praw.Reddit(
        client_id=settings.REDDIT_CLIENT_ID,
        client_secret=settings.REDDIT_CLIENT_SECRET,
        user_agent=settings.REDDIT_USER_AGENT,
    )
    all_posts = []
    for keyword in keywords:
        for submission in reddit.subreddit("all").search(keyword, limit=10):  # Adjust limit
            all_posts.append(SocialMediaPost(
                platform="reddit",
                timestamp=datetime.fromtimestamp(submission.created_utc),
                text=submission.title + "\n" + submission.selftext,
                author=submission.author.name,
                url=f"https://www.reddit.com{submission.permalink}"
            ))
    return all_posts