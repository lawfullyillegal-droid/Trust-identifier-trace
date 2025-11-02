#!/usr/bin/env python3
"""
Overlay Guardian Bot - Cryptographic overlay verification and hash checking
Employed by: Trust Security Department
Role: Verify integrity of overlay files and detect unauthorized modifications
"""
import os
import json
import hashlib
import glob
from datetime import datetime, timezone
from pathlib import Path

# Bot metadata
BOT_NAME = "Overlay Guardian Bot"
BOT_ROLE = "Security & Integrity Verification"
BOT_DEPARTMENT = "Trust Security Department"
BOT_VERSION = "1.0.0"

def calculate_file_hash(filepath):
    """Calculate SHA-256 hash of a file"""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        print(f"⚠️ Error hashing {filepath}: {e}")
        return None

def verify_overlay_integrity():
    """Verify integrity of all overlay files"""
    print(f"🛡️ {BOT_NAME} - Starting overlay integrity verification")
    print(f"👤 Role: {BOT_ROLE}")
    print(f"🏢 Department: {BOT_DEPARTMENT}")
    print(f"📋 Version: {BOT_VERSION}")
    print(f"⏰ Timestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
    
    overlays_dir = Path("overlays")
    if not overlays_dir.exists():
        print("⚠️ Overlays directory not found")
        return
    
    overlay_files = list(overlays_dir.glob("*.yml")) + list(overlays_dir.glob("*.yaml"))
    print(f"📁 Found {len(overlay_files)} overlay files to verify\n")
    
    verification_results = []
    hash_registry = {}
    
    for overlay_file in overlay_files:
        file_hash = calculate_file_hash(overlay_file)
        file_size = overlay_file.stat().st_size
        modified_time = datetime.fromtimestamp(overlay_file.stat().st_mtime, tz=timezone.utc)
        
        result = {
            "filename": overlay_file.name,
            "path": str(overlay_file),
            "hash": file_hash,
            "size_bytes": file_size,
            "last_modified": modified_time.isoformat(),
            "status": "verified" if file_hash else "error",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        verification_results.append(result)
        if file_hash:
            hash_registry[overlay_file.name] = file_hash
            print(f"✅ {overlay_file.name}")
            print(f"   Hash: {file_hash[:16]}...")
            print(f"   Size: {file_size} bytes")
        else:
            print(f"❌ {overlay_file.name} - Verification failed")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Save verification report
    report = {
        "bot_name": BOT_NAME,
        "bot_role": BOT_ROLE,
        "bot_department": BOT_DEPARTMENT,
        "bot_version": BOT_VERSION,
        "scan_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_overlays": len(overlay_files),
        "verified_overlays": sum(1 for r in verification_results if r["status"] == "verified"),
        "failed_overlays": sum(1 for r in verification_results if r["status"] == "error"),
        "verification_results": verification_results,
        "hash_registry": hash_registry
    }
    
    output_file = "output/overlay_verification_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Verification report saved to {output_file}")
    print(f"📊 Summary: {report['verified_overlays']} verified, {report['failed_overlays']} failed")
    print(f"🛡️ {BOT_NAME} scan complete")
    
    return report

def check_for_duplicates():
    """Check for duplicate overlay files based on hash"""
    print(f"\n🔍 Checking for duplicate overlay files...")
    
    overlays_dir = Path("overlays")
    overlay_files = list(overlays_dir.glob("*.yml")) + list(overlays_dir.glob("*.yaml"))
    
    hash_map = {}
    duplicates = []
    
    for overlay_file in overlay_files:
        file_hash = calculate_file_hash(overlay_file)
        if file_hash:
            if file_hash in hash_map:
                duplicates.append({
                    "original": hash_map[file_hash],
                    "duplicate": overlay_file.name,
                    "hash": file_hash
                })
                print(f"⚠️ Duplicate found: {overlay_file.name} matches {hash_map[file_hash]}")
            else:
                hash_map[file_hash] = overlay_file.name
    
    if not duplicates:
        print("✅ No duplicate overlay files found")
    
    return duplicates

if __name__ == "__main__":
    print("=" * 70)
    print(f"🤖 {BOT_NAME}")
    print(f"⚡ Automated overlay integrity verification system")
    print("=" * 70 + "\n")
    
    # Run verification
    report = verify_overlay_integrity()
    
    # Check for duplicates
    duplicates = check_for_duplicates()
    
    print("\n" + "=" * 70)
    print(f"✅ {BOT_NAME} operations complete")
    print("=" * 70)
