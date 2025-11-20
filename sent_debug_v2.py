import os
import tweepy
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

# Get API keys from .env file
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    print("Warning: BEARER_TOKEN is not set. Please check your .env file or environment variables.")

# Authenticate with Twitter API v2 if credentials are present
client = None
if BEARER_TOKEN:
    try:
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
    except Exception as e:
        print(f"⚠️ Failed to initialize Twitter client: {e}")
        client = None

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to fetch tweets with rate limit handling and sentiment categorization
def fetch_tweets_v2(keyword, count=10):
    # If client is not initialized (missing/invalid credentials), return structured error
    if client is None:
        return {"error": "no_credentials", "message": "BEARER_TOKEN is not set or invalid. Set it in .env or environment."}
    if count < 10:
        count = 10
    elif count > 100:
        count = 100

    query = f"{keyword}"

    # Limit to last 1 hour to reduce duplicates and API hits
    now = datetime.utcnow()
    start_time = now - timedelta(hours=1)
    start_time_str = start_time.isoformat("T") + "Z"

    tweets_data = []

    max_retries = 3  # Reduced to avoid long waits in dashboard
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        try:
            response = client.search_recent_tweets(
                query=query,
                max_results=count,
                start_time=start_time_str,
                tweet_fields=["author_id", "text"]
            )

            # Debug: print response meta when available
            try:
                meta = getattr(response, 'meta', None)
                if meta:
                    print(f"Response meta: {meta}")
            except Exception:
                pass

            if response.data:
                for tweet in response.data:
                    sentiment = analyzer.polarity_scores(tweet.text)
                    compound = sentiment['compound']

                    # Corrected sentiment categorization with stricter thresholds
                    if compound >= 0.05:
                        category = "Positive"
                    elif compound <= -0.8:  # Stricter threshold for Highly Negative
                        category = "Highly Negative"
                    elif compound < 0.05 and compound > -0.8:
                        category = "Less Negative"
                    else:
                        category = "Neutral"

                    tweet_dict = {
                        "id": tweet.id,
                        "text": tweet.text,
                        "sentiment": sentiment,
                        "category": category
                    }
                    tweets_data.append(tweet_dict)

                return tweets_data  # Return the list of tweet dictionaries

            else:
                print("No tweets found. Retrying...")

        except tweepy.TooManyRequests as e:
            # Improved rate limit handling: wait exactly until reset and include headers for debugging
            resp = getattr(e, 'response', None)
            headers = {}
            status = None
            try:
                if resp is not None:
                    status = getattr(resp, 'status_code', None)
                    headers = dict(getattr(resp, 'headers', {}) or {})
            except Exception:
                headers = {}

            reset_time = None
            try:
                if headers and headers.get('x-rate-limit-reset'):
                    reset_time = int(headers.get('x-rate-limit-reset'))
                else:
                    reset_time = int(time.time() + 60)
            except Exception:
                reset_time = int(time.time() + 60)

            wait_time = max(reset_time - time.time(), 0)
            print(f"🚫 Rate limit response status={status} headers={headers}")
            if wait_time > 60:
                print(f"🚫 Rate limit exceeded. Wait time too long ({int(wait_time)}s). Try again later.")
                # Return structured error including headers and status for debugging/comparison
                return {"error": "rate_limit", "wait_time": int(wait_time), "status": status, "headers": headers}
            print(f"🚫 Rate limit exceeded. Waiting for {int(wait_time)} seconds before retrying...")
            time.sleep(wait_time + 1)

        except KeyboardInterrupt:
            print("\n⛔ Process interrupted by user. Exiting.")
            return []

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            # Return a structured error to the caller so UI can handle it gracefully
            return {"error": "unexpected", "message": str(e)}

    print("❌ Failed after multiple attempts. Try again later.")
    return []

if __name__ == "__main__":
    # Simple CLI test — this will only run when the module is executed directly,
    # not when it's imported by `dashboard.py` (prevents unwanted API calls).
    tweets = fetch_tweets_v2("AI", count=10)
    print(f"Fetched {len(tweets)} tweets")
