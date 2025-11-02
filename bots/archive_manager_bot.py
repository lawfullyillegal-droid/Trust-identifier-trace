#!/usr/bin/env python3
"""
Archive Manager Bot - Intelligent archival with cleanup and organization
Employed by: Trust Records Department
Role: Manage scan result archives, implement retention policies, and optimize storage
"""
import os
import json
import glob
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Bot metadata
BOT_NAME = "Archive Manager Bot"
BOT_ROLE = "Records Management & Archival"
BOT_DEPARTMENT = "Trust Records Department"
BOT_VERSION = "1.0.0"

# Configuration
ARCHIVE_DIR = Path("archive")
OUTPUT_DIR = Path("output")
MAX_ARCHIVES = 100  # Maximum number of archives to keep
RETENTION_DAYS = 90  # Keep archives for 90 days

def ensure_directories():
    """Ensure required directories exist"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

def archive_current_results():
    """Archive current scan results with timestamp"""
    print(f"📦 Archiving current scan results...")
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d_%H-%M-%S')
    archived_count = 0
    
    # Files to archive
    archive_targets = [
        ("output/scan_results.json", f"scan_results_{timestamp}.json"),
        ("output/reddit_trace_results.json", f"reddit_trace_{timestamp}.json"),
        ("output/overlay_verification_report.json", f"overlay_verification_{timestamp}.json"),
        ("output/syndicate_dashboard_data.json", f"syndicate_dashboard_{timestamp}.json"),
    ]
    
    for source, dest_name in archive_targets:
        source_path = Path(source)
        if source_path.exists():
            dest_path = ARCHIVE_DIR / dest_name
            shutil.copy2(source_path, dest_path)
            print(f"  ✅ Archived: {dest_name}")
            archived_count += 1
        else:
            print(f"  ⚠️ Not found: {source}")
    
    return archived_count

def apply_retention_policy():
    """Apply retention policy to remove old archives"""
    print(f"\n🗑️ Applying retention policy (keeping last {MAX_ARCHIVES} archives)...")
    
    archive_files = sorted(glob.glob(str(ARCHIVE_DIR / "*.json")))
    
    if len(archive_files) > MAX_ARCHIVES:
        files_to_remove = archive_files[:-MAX_ARCHIVES]
        print(f"  📊 Found {len(archive_files)} archives, removing {len(files_to_remove)} old files")
        
        for filepath in files_to_remove:
            try:
                os.remove(filepath)
                print(f"  ✅ Removed: {Path(filepath).name}")
            except Exception as e:
                print(f"  ❌ Error removing {filepath}: {e}")
    else:
        print(f"  ✅ Archive count within limits ({len(archive_files)}/{MAX_ARCHIVES})")

def apply_age_based_retention():
    """Remove archives older than retention period"""
    print(f"\n⏰ Checking for archives older than {RETENTION_DAYS} days...")
    
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    archive_files = glob.glob(str(ARCHIVE_DIR / "*.json"))
    
    removed_count = 0
    for filepath in archive_files:
        file_path = Path(filepath)
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        
        if modified_time < cutoff_date:
            try:
                os.remove(filepath)
                print(f"  ✅ Removed old archive: {file_path.name}")
                removed_count += 1
            except Exception as e:
                print(f"  ❌ Error removing {filepath}: {e}")
    
    if removed_count == 0:
        print(f"  ✅ No archives exceed retention period")
    else:
        print(f"  📊 Removed {removed_count} old archives")

def generate_archive_index():
    """Generate an index of all archived files"""
    print(f"\n📋 Generating archive index...")
    
    archive_files = sorted(glob.glob(str(ARCHIVE_DIR / "*.json")))
    
    index_entries = []
    for filepath in archive_files:
        file_path = Path(filepath)
        file_size = file_path.stat().st_size
        modified_time = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        
        index_entries.append({
            "filename": file_path.name,
            "size_bytes": file_size,
            "modified": modified_time.isoformat(),
            "path": str(file_path)
        })
    
    index_data = {
        "bot_name": BOT_NAME,
        "bot_role": BOT_ROLE,
        "bot_department": BOT_DEPARTMENT,
        "bot_version": BOT_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_archives": len(index_entries),
        "total_size_bytes": sum(entry["size_bytes"] for entry in index_entries),
        "retention_policy": {
            "max_archives": MAX_ARCHIVES,
            "retention_days": RETENTION_DAYS
        },
        "archives": index_entries
    }
    
    index_file = ARCHIVE_DIR / "archive_index.json"
    with open(index_file, "w") as f:
        json.dump(index_data, f, indent=2)
    
    print(f"  ✅ Index generated: {index_file}")
    print(f"  📊 Total archives: {len(index_entries)}")
    print(f"  💾 Total size: {index_data['total_size_bytes'] / 1024:.2f} KB")
    
    return index_data

def create_archive_report():
    """Create comprehensive archive management report"""
    archive_files = glob.glob(str(ARCHIVE_DIR / "*.json"))
    
    report = {
        "bot_name": BOT_NAME,
        "bot_role": BOT_ROLE,
        "bot_department": BOT_DEPARTMENT,
        "bot_version": BOT_VERSION,
        "report_timestamp": datetime.now(timezone.utc).isoformat(),
        "archive_statistics": {
            "total_files": len(archive_files),
            "total_size_mb": sum(Path(f).stat().st_size for f in archive_files) / (1024 * 1024),
            "oldest_archive": min((Path(f).stat().st_mtime for f in archive_files), default=0),
            "newest_archive": max((Path(f).stat().st_mtime for f in archive_files), default=0)
        },
        "retention_policy": {
            "max_archives": MAX_ARCHIVES,
            "retention_days": RETENTION_DAYS
        },
        "status": "operational"
    }
    
    output_file = OUTPUT_DIR / "archive_management_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Archive management report saved to {output_file}")
    
    return report

if __name__ == "__main__":
    print("=" * 70)
    print(f"🤖 {BOT_NAME}")
    print(f"⚡ Automated archive management and retention system")
    print("=" * 70 + "\n")
    
    print(f"👤 Role: {BOT_ROLE}")
    print(f"🏢 Department: {BOT_DEPARTMENT}")
    print(f"📋 Version: {BOT_VERSION}")
    print(f"⏰ Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    # Ensure directories exist
    ensure_directories()
    
    # Archive current results
    archived_count = archive_current_results()
    
    # Apply retention policies
    apply_retention_policy()
    apply_age_based_retention()
    
    # Generate index
    index_data = generate_archive_index()
    
    # Create report
    report = create_archive_report()
    
    print("\n" + "=" * 70)
    print(f"✅ {BOT_NAME} operations complete")
    print(f"📊 Archived {archived_count} files")
    print("=" * 70)
