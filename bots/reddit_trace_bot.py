#!/usr/bin/env python3
"""
Reddit Trace Bot - Comprehensive Reddit profiler for trust identifiers
"""
import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

# Load identifiers
try:
    with open('identifiers.json', 'r') as f:
        identifiers = json.load(f)
except FileNotFoundError:
    print("⚠️ identifiers.json not found, using default identifiers")
    identifiers = [
        {"identifier": "EIN-92-6319308", "source": "EIN"},
        {"identifier": "SSN-602-05-7209", "source": "SSN"},
        {"identifier": "IRS-TRACK-108541264370", "source": "IRSTrack"}
    ]

def query_reddit_with_risk_profile(identifier):
    """Query Reddit and generate risk profile"""
    try:
        headers = {"User-Agent": "RedditTraceBot/1.0"}
        url = f"https://www.reddit.com/search.json?q={identifier}&limit=10"
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            posts = [post["data"]["title"] for post in data["data"]["children"]]
            
            # Generate risk profile
            mention_count = len(posts)
            if mention_count > 5:
                risk_level = "HIGH"
            elif mention_count > 2:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                "mentions": posts,
                "mention_count": mention_count,
                "risk_level": risk_level,
                "scan_timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            print(f"⚠️ Reddit API returned status code: {response.status_code}")
            return None
    
    except requests.exceptions.ConnectionError:
        print(f"⚠️ Network connection failed for Reddit query of {identifier}")
        # Return mock data for offline mode
        return {
            "mentions": [f"Mock Reddit mention of {identifier} (offline mode)"],
            "mention_count": 1,
            "risk_level": "LOW",
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "offline_mode": True
        }
    except Exception as e:
        print(f"⚠️ Error querying Reddit for {identifier}: {e}")
        return None

# Create output directory
os.makedirs("output", exist_ok=True)

# Generate Reddit profiles for all identifiers
reddit_profiles = []
for item in identifiers:
    identifier = item["identifier"]
    print(f"🔍 Profiling Reddit mentions for: {identifier}")
    
    profile = query_reddit_with_risk_profile(identifier)
    if profile:
        reddit_profiles.append({
            "identifier": identifier,
            "source": item.get("source", "Unknown"),
            "reddit_profile": profile
        })

# Save results
output_file = "output/reddit_trace_results.json"
with open(output_file, "w") as f:
    json.dump(reddit_profiles, f, indent=2)

print(f"📄 Reddit trace complete. Results saved to {output_file}")
print(f"📊 Processed {len(reddit_profiles)} identifiers")

# Generate summary
high_risk = sum(1 for p in reddit_profiles if p["reddit_profile"]["risk_level"] == "HIGH")
medium_risk = sum(1 for p in reddit_profiles if p["reddit_profile"]["risk_level"] == "MEDIUM")
low_risk = sum(1 for p in reddit_profiles if p["reddit_profile"]["risk_level"] == "LOW")

print(f"🎯 Risk Summary: {high_risk} HIGH, {medium_risk} MEDIUM, {low_risk} LOW")
