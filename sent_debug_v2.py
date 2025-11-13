import os
import tweepy
import time
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load environment variables
load_dotenv()

# Get API keys from .env file
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    print("Warning: BEARER_TOKEN is not set. Please check your .env file or environment variables.")

# Authenticate with Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Initialize sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Function to fetch tweets with rate limit handling and sentiment categorization
def fetch_tweets_v2(keyword, count=10):
    if count < 10:
        count = 10
    elif count > 100:
        count = 100

    query = f"{keyword}"

    max_retries = 5
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        try:
            response = client.search_recent_tweets(query=query, max_results=count, tweet_fields=["author_id", "text"])

            if response.data:
                for tweet in response.data:
                    sentiment = analyzer.polarity_scores(tweet.text)
                    compound = sentiment['compound']

                    if compound >= 0.05:
                        print(f"✅ Positive Tweet ID: {tweet.id}\nTweet: {tweet.text}\nSentiment: {sentiment}\n")
                    elif -0.05 < compound < 0.05:
                        print(f"😐 Neutral Tweet ID: {tweet.id}\nTweet: {tweet.text}\nSentiment: {sentiment}\n")
                    elif compound > -0.5:
                        print(f"⚠️ RED FLAG - Less Negative Tweet ID: {tweet.id}\nTweet: {tweet.text}\nSentiment: {sentiment}\n")
                    else:
                        # Highly negative - skipped
                        continue
                return  # Only return if actual data was processed

            else:
                print("No tweets found. Retrying...")

        except tweepy.TooManyRequests as e:
            reset_time = int(e.response.headers.get("x-rate-limit-reset", time.time() + 60))
            wait_time = max(reset_time - time.time(), 60)
            capped_wait_time = min(wait_time, 120)
            print(f"🚫 Rate limit exceeded. Waiting for {int(capped_wait_time)} seconds before retrying...")
            time.sleep(capped_wait_time)

        except KeyboardInterrupt:
            print("\n⛔ Process interrupted by user. Exiting.")
            return

        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            break

    print("❌ Failed after multiple attempts. Try again later.")

# Run it
fetch_tweets_v2("AI", count=10)
