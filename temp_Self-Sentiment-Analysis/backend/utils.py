from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str) -> float:
    """Analyzes the sentiment of a given text and returns a score (-1 to 1)."""
    vs = analyzer.polarity_scores(text)
    return vs['compound']

def detect_mood_shift(previous_score: float, current_score: float, threshold=0.1) -> str:
    """Detects significant mood shifts based on sentiment score changes."""
    if previous_score is None:
        return "Neutral"  # No previous data to compare
    diff = current_score - previous_score
    if diff > threshold:
        return "Positive"
    elif diff < -threshold:
        return "Negative"
    return "Neutral"

# You can explore more advanced sentiment analysis techniques using libraries like:
# - spaCy with its sentiment component
# - Transformers (Hugging Face) for fine-tuned models