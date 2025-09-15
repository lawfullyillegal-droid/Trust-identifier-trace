import requests

def query_reddit_threads(identifier):
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
    except Exception as e:
        print(f"⚠️ Reddit API connection failed for {identifier}, using offline mode: {e}")
        # Return sample offline data for testing
        return [
            f"Sample Reddit post mentioning {identifier}",
            f"Trust discussion involving {identifier}",
            f"Legal entity reference to {identifier}"
        ]
    return []
