"""
Network utilities for Trust-identifier-trace bots
Provides robust HTTP request handling with retry logic, DNS fallback, and comprehensive error handling

Version: 2.0 (Network-Enhanced)
- All bots using network_utils will automatically use version 2.0 User-Agent
- User-Agent: "TrustScanBot/2.0 (Network-Enhanced)" for Reddit API
- This ensures consistent identification across all bot implementations
"""

import requests
import time
import socket
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class NetworkError(Exception):
    """Custom exception for network-related errors"""
    pass


def check_dns_resolution(hostname: str) -> bool:
    """
    Check if a hostname can be resolved via DNS
    
    Args:
        hostname: The hostname to resolve
        
    Returns:
        True if resolution succeeds, False otherwise
    """
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False


def make_request_with_retry(
    url: str,
    max_retries: int = 3,
    timeout: int = 10,
    backoff_factor: float = 1.0,
    headers: Optional[Dict[str, str]] = None,
    method: str = "GET",
    **kwargs
) -> requests.Response:
    """
    Make an HTTP request with retry logic and exponential backoff
    
    Args:
        url: The URL to request
        max_retries: Maximum number of retry attempts (default: 3)
        timeout: Request timeout in seconds (default: 10)
        backoff_factor: Multiplier for exponential backoff (default: 1.0)
        headers: Optional HTTP headers
        method: HTTP method (default: GET)
        **kwargs: Additional arguments passed to requests.request()
        
    Returns:
        requests.Response object
        
    Raises:
        NetworkError: If all retry attempts fail
    """
    if headers is None:
        headers = {}
    
    # Parse hostname for DNS check
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    # Check DNS resolution first
    print(f"🔍 Checking DNS resolution for {hostname}...")
    if not check_dns_resolution(hostname):
        raise NetworkError(
            f"DNS resolution failed for {hostname}. "
            f"Please check network configuration and DNS settings."
        )
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            print(f"📡 Attempt {attempt + 1}/{max_retries}: {method} {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=timeout,
                **kwargs
            )
            
            # Raise for bad status codes
            response.raise_for_status()
            
            print(f"✅ Request successful: Status {response.status_code}")
            return response
            
        except requests.exceptions.Timeout as e:
            last_exception = e
            print(f"⏱️ Timeout on attempt {attempt + 1}/{max_retries}")
            
        except requests.exceptions.ConnectionError as e:
            last_exception = e
            print(f"🔌 Connection error on attempt {attempt + 1}/{max_retries}: {e}")
            
        except requests.exceptions.HTTPError as e:
            # Don't retry on client errors (4xx)
            if 400 <= e.response.status_code < 500:
                print(f"❌ Client error {e.response.status_code}: {e}")
                raise NetworkError(f"HTTP {e.response.status_code}: {e}")
            
            last_exception = e
            print(f"⚠️ HTTP error on attempt {attempt + 1}/{max_retries}: {e}")
            
        except requests.exceptions.RequestException as e:
            last_exception = e
            print(f"⚠️ Request error on attempt {attempt + 1}/{max_retries}: {e}")
        
        # Wait before retry (exponential backoff)
        if attempt < max_retries - 1:
            wait_time = backoff_factor * (2 ** attempt)
            print(f"⏳ Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
    
    # All retries failed
    error_msg = (
        f"Failed to connect to {url} after {max_retries} attempts. "
        f"Last error: {type(last_exception).__name__}: {last_exception}"
    )
    raise NetworkError(error_msg)


def get_gleif_data(
    query_params: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    timeout: int = 15
) -> Dict[str, Any]:
    """
    Fetch data from GLEIF API with robust error handling
    
    Args:
        query_params: Optional query parameters for the API
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        JSON response from GLEIF API
        
    Raises:
        NetworkError: If request fails after all retries
    """
    base_url = "https://api.gleif.org/api/v1/lei-records"
    
    try:
        response = make_request_with_retry(
            url=base_url,
            params=query_params,
            max_retries=max_retries,
            timeout=timeout
        )
        
        return response.json()
        
    except NetworkError as e:
        print(f"❌ GLEIF API request failed: {e}")
        raise


def get_reddit_search(
    query: str,
    limit: int = 5,
    max_retries: int = 3,
    timeout: int = 10
) -> Dict[str, Any]:
    """
    Search Reddit with robust error handling
    
    Args:
        query: Search query
        limit: Maximum number of results
        max_retries: Maximum number of retry attempts
        timeout: Request timeout in seconds
        
    Returns:
        JSON response from Reddit API
        
    Raises:
        NetworkError: If request fails after all retries
    """
    url = f"https://www.reddit.com/search.json"
    headers = {"User-Agent": "TrustScanBot/2.0 (Network-Enhanced)"}
    params = {"q": query, "limit": limit}
    
    try:
        response = make_request_with_retry(
            url=url,
            headers=headers,
            params=params,
            max_retries=max_retries,
            timeout=timeout
        )
        
        return response.json()
        
    except NetworkError as e:
        print(f"❌ Reddit search failed: {e}")
        raise


def test_network_connectivity() -> Dict[str, bool]:
    """
    Test connectivity to key services
    
    Returns:
        Dictionary with connectivity status for each service
    """
    results = {}
    
    # Test DNS resolution
    print("🧪 Testing DNS resolution...")
    results['dns_gleif'] = check_dns_resolution('api.gleif.org')
    results['dns_reddit'] = check_dns_resolution('www.reddit.com')
    results['dns_google'] = check_dns_resolution('www.google.com')
    
    # Test HTTP connectivity
    print("🧪 Testing HTTP connectivity...")
    try:
        make_request_with_retry('https://www.google.com', max_retries=1, timeout=5)
        results['http_google'] = True
    except NetworkError:
        results['http_google'] = False
    
    try:
        make_request_with_retry('https://api.gleif.org/api/v1/lei-records?page[size]=1', max_retries=1, timeout=5)
        results['http_gleif'] = True
    except NetworkError:
        results['http_gleif'] = False
    
    try:
        make_request_with_retry('https://www.reddit.com/robots.txt', max_retries=1, timeout=5)
        results['http_reddit'] = True
    except NetworkError:
        results['http_reddit'] = False
    
    return results


if __name__ == "__main__":
    print("=" * 60)
    print("Network Connectivity Test")
    print("=" * 60)
    
    results = test_network_connectivity()
    
    print("\n" + "=" * 60)
    print("Results Summary")
    print("=" * 60)
    
    for test, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All connectivity tests PASSED")
    else:
        print("❌ Some connectivity tests FAILED")
        print("⚠️ Network configuration may need adjustment")
    print("=" * 60)
