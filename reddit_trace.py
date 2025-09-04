import requests

def query_reddit_threads(identifier):
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Reddit API error for {identifier}: {e}")
    return []
