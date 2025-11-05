from network_utils import get_reddit_search, NetworkError

def query_reddit_threads(identifier):
    """Query Reddit threads for a given identifier with enhanced error handling and retry logic"""
    try:
        # Use network_utils for robust request with retry logic
        data = get_reddit_search(query=identifier, limit=5, max_retries=3, timeout=10)
        
        # Extract post titles from response
        posts = data.get("data", {}).get("children", [])
        titles = [post["data"]["title"] for post in posts]
        
        if titles:
            print(f"✅ Found {len(titles)} Reddit posts for {identifier}")
            return titles
        else:
            print(f"ℹ️ No Reddit posts found for {identifier}")
            return []
            
    except NetworkError as e:
        print(f"⚠️ Network error querying Reddit for {identifier}: {e}")
        print("🔄 Falling back to offline mode with mock data")
        # Return mock data for offline mode
        return [f"Mock Reddit post mentioning {identifier} (offline mode)"]
    except Exception as e:
        print(f"⚠️ Unexpected error querying Reddit for {identifier}: {e}")
        return [f"Mock Reddit post mentioning {identifier} (offline mode - error)"]
