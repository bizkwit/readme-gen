from typing import List
import tweepy
from datetime import datetime
from ..config import settings
from ..models import SocialMediaPost

async def fetch_twitter_data(keywords: List[str]) -> List[SocialMediaPost]:
    client = tweepy.Client(settings.TWITTER_BEARER_TOKEN)
    all_tweets = []
    for keyword in keywords:
        response = client.search_recent_tweets(
            keyword,
            tweet_fields=["created_at", "author_id", "id"],
            expansions=["author_id"],
            user_fields=["username"]
        )
        if response and response.data:
            for tweet in response.data:
                user = next((user for user in response.includes['users'] if user.id == tweet.author_id), None)
                if user:
                    all_tweets.append(SocialMediaPost(
                        platform="twitter",
                        timestamp=tweet.created_at,
                        text=tweet.text,
                        author=user.username,
                        url=f"https://twitter.com/{user.username}/status/{tweet.id}"
                    ))
    return all_tweets