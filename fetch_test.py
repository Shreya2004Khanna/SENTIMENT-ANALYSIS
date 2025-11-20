import sys
from sent_debug_v2 import fetch_tweets_v2

def main():
    keyword = sys.argv[1] if len(sys.argv) > 1 else "AI"
    try:
        result = fetch_tweets_v2(keyword, count=10)
        import json as _json
        print("--- RAW RESULT ---")
        print(type(result))
        try:
            print(_json.dumps(result, indent=2, ensure_ascii=False))
        except Exception:
            print(result)

        if isinstance(result, list):
            print(f"Fetched {len(result)} tweets (list).")
        elif isinstance(result, dict) and result.get('error') == 'rate_limit':
            print(f"Rate limit. Wait time: {result.get('wait_time')} seconds")
            print(f"Status: {result.get('status')}")
            print(f"Headers: {_json.dumps(result.get('headers', {}), indent=2, ensure_ascii=False)}")
        elif isinstance(result, dict) and result.get('error') == 'unexpected':
            print(f"Unexpected error: {result.get('message')}")
        elif isinstance(result, dict) and result.get('error') == 'no_credentials':
            print(f"No credentials: {result.get('message')}")
        else:
            print("No tweets found or returned an unexpected type.")
    except Exception as e:
        print(f"Exception while fetching tweets: {e}")

if __name__ == '__main__':
    main()
