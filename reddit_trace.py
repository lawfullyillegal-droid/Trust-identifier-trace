import requests
import time

def query_reddit_threads(identifier):
    headers = {"User-Agent": "TrustScanBot/1.0"}
    url = f"https://www.reddit.com/search.json?q={identifier}&limit=5"
    
    # Add timeout and retry logic
    max_retries = 3
    timeout_seconds = 10
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout_seconds)
            if response.status_code == 200:
                data = response.json()
                return [post["data"]["title"] for post in data["data"]["children"]]
            elif response.status_code == 429:  # Rate limited
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
            return []
        except requests.exceptions.RequestException as e:
            print(f"Network error querying Reddit for {identifier}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            # If all retries failed, return empty list instead of crashing
            return []
    
    return []
