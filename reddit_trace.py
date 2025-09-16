import requests

def query_reddit_threads(identifier):
    """Query Reddit for threads mentioning the identifier with error handling"""
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [post["data"]["title"] for post in data["data"]["children"]]
        else:
            print(f"⚠️ Reddit API returned status {response.status_code} for identifier {identifier}")
            return []
    except requests.exceptions.ConnectionError:
        print(f"⚠️ Network connection failed for Reddit query of {identifier}")
        return []
    except requests.exceptions.Timeout:
        print(f"⚠️ Reddit query timeout for identifier {identifier}")
        return []
    except Exception as e:
        print(f"⚠️ Reddit query failed for {identifier}: {e}")
        return []
