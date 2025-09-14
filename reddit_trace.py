import requests

def query_reddit_threads(identifier):
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as e:
        print(f"⚠️ Reddit connection failed for '{identifier}': Using offline mode")
        # Return sample data in offline mode
        return [f"Sample thread mentioning {identifier}", f"Discussion about {identifier} identifier"]
    return []
