#!/usr/bin/env python3
"""
Reddit Thread Profiler Bot
Scans Reddit for mentions of trust identifiers and profiles suspicious activity.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path to import reddit_trace
sys.path.append(str(Path(__file__).parent.parent))
from reddit_trace import query_reddit_threads

def load_identifiers():
    """Load identifiers from identifiers.json"""
    identifiers_file = Path(__file__).parent.parent / "identifiers.json"
    with open(identifiers_file, "r") as f:
        return json.load(f)

def scan_reddit_profiles():
    """Scan Reddit for identifier mentions and create profile data"""
    identifiers = load_identifiers()
    profile_results = []
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    
    for ident in identifiers:
        identifier_value = ident["identifier"]
        
        try:
            # Query Reddit for mentions
            reddit_hits = query_reddit_threads(identifier_value)
            
            profile_entry = {
                "identifier": identifier_value,
                "source": ident["source"],
                "reddit_mentions": len(reddit_hits) if reddit_hits else 0,
                "reddit_threads": reddit_hits[:3] if reddit_hits else [],  # Limit to top 3
                "timestamp": timestamp,
                "risk_level": "high" if reddit_hits and len(reddit_hits) > 2 else "low"
            }
            
            profile_results.append(profile_entry)
            
        except Exception as e:
            # Handle network errors gracefully
            profile_entry = {
                "identifier": identifier_value,
                "source": ident["source"],
                "reddit_mentions": 0,
                "reddit_threads": [],
                "timestamp": timestamp,
                "risk_level": "unknown",
                "error": f"Failed to scan: {str(e)}"
            }
            profile_results.append(profile_entry)
    
    return profile_results

def save_profile_results(results):
    """Save results to JSON file"""
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "reddit_profile_results.json"
    
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Reddit profile results saved to {output_file}")
    return output_file

def main():
    """Main execution function"""
    print("🔍 Starting Reddit Thread Profiler...")
    
    try:
        results = scan_reddit_profiles()
        output_file = save_profile_results(results)
        
        # Print summary
        total_identifiers = len(results)
        high_risk_count = sum(1 for r in results if r.get("risk_level") == "high")
        
        print(f"📊 Scan Summary:")
        print(f"   - Total identifiers scanned: {total_identifiers}")
        print(f"   - High-risk identifiers: {high_risk_count}")
        print(f"   - Results saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Reddit profiler failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()