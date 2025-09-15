import requests

def query_reddit_threads(identifier):
    """Query Reddit threads with error handling for network issues"""
    try:
        headers = {"User-Agent": "TrustScanBot/1.0"}
        url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
        return []
    except Exception as e:
        print(f"⚠️ Reddit query failed for '{identifier}': {e}")
        return []
