#!/usr/bin/env python3
"""Generate Syndicate Dashboard with comprehensive system status"""
import os
import json
import glob
from datetime import datetime, timezone
from pathlib import Path

def create_syndicate_dashboard():
    # Collect all scan results
    scan_files = []
    if os.path.exists("output/scan_results.json"):
        scan_files.append("output/scan_results.json")
    
    # Check for archived results
    archive_files = glob.glob("archive/scan_results_*.json")
    scan_files.extend(archive_files[-5:])  # Last 5 archived results
    
    # Count overlay files
    overlay_count = len(glob.glob("overlays/*.yml"))
    
    # Generate dashboard data
    dashboard_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "system_status": "operational",
        "scan_files": scan_files,
        "overlay_count": overlay_count,
        "active_workflows": [
            "Trust Scan Bot",
            "Reddit Trace Bot",
            "GLEIF Scan",
            "Archive Scan"
        ],
        "summary": {
            "total_scan_runs": len(scan_files),
            "last_scan": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "syndicate_status": "active"
        }
    }
    
    # Save dashboard data
    with open("output/syndicate_dashboard_data.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)
    
    print(f"📊 Syndicate dashboard generated")
    print(f"📄 Found {len(scan_files)} scan result files")
    print(f"🔧 Found {overlay_count} overlay files")
    print(f"📅 Last updated: {dashboard_data['timestamp']}")

if __name__ == "__main__":
    create_syndicate_dashboard()
