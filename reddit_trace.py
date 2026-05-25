import requests

def query_reddit_threads(identifier):
    """Query Reddit threads for a given identifier with error handling"""
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
        else:
            print(f"⚠️ Reddit API returned status code: {response.status_code}")
            return []
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        print(f"⚠️ Network error querying Reddit for {identifier}: {e}")
        # Return mock data for offline mode
        return [f"Mock Reddit post mentioning {identifier} (offline mode)"]
