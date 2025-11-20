import streamlit as st
import plotly.express as px
import json
from sent_debug_v2 import fetch_tweets_v2

# Set page config
st.set_page_config(page_title="Sentiment Analysis Dashboard", page_icon="📊", layout="wide")

# Title
st.title("📊 Sentiment Analysis Dashboard for Tweets")

# Sidebar
st.sidebar.header("🔍 Search Parameters")
keyword = st.sidebar.text_input("Keyword", value="AI", help="Enter a keyword to search for tweets")
count = st.sidebar.slider("Number of Tweets", min_value=10, max_value=30, value=10, step=10, help="Select the number of tweets to fetch (10-30)")
use_sample = st.sidebar.checkbox("Use sample data (dev)", value=False, help="Display local sample tweets instead of calling Twitter API")

# Fetch tweets with a small, explicit cache stored in session state.
def get_tweets(keyword, count):
    # Use session-state keyed cache so we can avoid caching error responses
    cache_key = f"tweets::{keyword}::{count}"
    cached = st.session_state.get(cache_key)
    if cached is not None:
        return cached

    result = fetch_tweets_v2(keyword, count)

    # Only cache successful results (a list of tweets). Do not cache dict errors.
    if isinstance(result, list):
        st.session_state[cache_key] = result

    return result

# Fetch button
if st.sidebar.button("🚀 Fetch Tweets"):
    with st.spinner("Fetching tweets and analyzing sentiment..."):
        if use_sample:
            # Load sample data from single keyword-indexed JSON file
            try:
                with open("sample_data.json", "r", encoding="utf-8") as f:
                    all_samples = json.load(f)
                # Get samples for the current keyword, or show not-found message
                keyword_lower = keyword.lower()
                if keyword_lower in all_samples:
                    tweets = all_samples[keyword_lower]
                else:
                    tweets = []  # Empty list will trigger the "No tweets found" message
                    st.info(f"ℹ️ Can't find relevant info about '{keyword}'. Available sample keywords: {', '.join(all_samples.keys())}")
            except Exception as e:
                tweets = {"error": "unexpected", "message": f"Failed to load sample data: {e}"}
        else:
            tweets = get_tweets(keyword, count)

    # Handle structured error responses from fetch_tweets_v2
    if isinstance(tweets, dict) and tweets.get("error") == "rate_limit":
        wait_time = tweets.get("wait_time", 0)
        minutes = wait_time // 60
        st.warning(f"⚠️ Twitter API rate limit. Please wait {minutes} minute(s) ({wait_time} seconds) and try again.")
    elif isinstance(tweets, dict) and tweets.get("error") == "unexpected":
        st.error(f"⚠️ Error fetching tweets: {tweets.get('message')}")
    elif isinstance(tweets, dict) and tweets.get("error") == "no_credentials":
        st.error("⚠️ Twitter credentials not found. Please set `BEARER_TOKEN` in your .env or environment and restart the app.")
    elif tweets:
        # Display summary
        st.success(f"✅ Fetched {len(tweets)} tweets for keyword '{keyword}'")

        # Pie chart for sentiment distribution
        categories = [tweet['category'] for tweet in tweets]
        category_counts = {cat: categories.count(cat) for cat in set(categories)}
        fig = px.pie(values=list(category_counts.values()), names=list(category_counts.keys()),
                     title="Sentiment Distribution", color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig, use_container_width=True)

        # Display tweets by category
        categories_order = ["Positive", "Neutral", "Less Negative", "Highly Negative"]
        for cat in categories_order:
            if cat in category_counts:
                with st.expander(f"📈 {cat} Tweets ({category_counts[cat]})", expanded=False):
                    for tweet in tweets:
                        if tweet['category'] == cat:
                            if cat == "Highly Negative":
                                st.markdown(f"<p style='color:red; font-weight:bold;'>🛑 Tweet ID: {tweet['id']}</p>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"**Tweet ID: {tweet['id']}**")
                            st.write(f"**Text:** {tweet['text']}")
                            st.write(f"**Sentiment Scores:** {tweet['sentiment']}")
                            st.divider()
    else:
        st.warning("⚠️ No tweets found or Twitter API rate limit reached. Please wait a few minutes and try again.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and VADER Sentiment Analysis")
