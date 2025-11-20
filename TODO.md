# TODO for Sentiment Analysis Dashboard

## Step 1: Modify sent_debug_v2.py ✅
- Update fetch_tweets_v2 function to return a list of dictionaries containing tweet data (text, sentiment scores, category) instead of printing to console.
- Categorize tweets as: Positive, Neutral, Less Negative, Highly Negative.

## Step 2: Create dashboard.py ✅
- Import necessary libraries: streamlit, plotly.express for pie chart.
- Create sidebar with inputs: keyword (text input), count (slider or number input).
- Add a "Fetch Tweets" button.
- Display tweets in expandable sections by category (Positive, Neutral, Less Negative, Highly Negative in red).
- Add a pie chart showing sentiment distribution.

## Step 3: Install Dependencies ✅
- Ensure streamlit and plotly are installed (pip install streamlit plotly).

## Step 4: Test the Dashboard ✅
- Run the Streamlit app and verify functionality.
- Check for errors and UI cleanliness.
