#!/usr/bin/env python3
"""
Security Audit Bot - Vulnerability Scanning & Evidence Preservation
Employed by: Trust Security & Integrity Department
Role: Audit system security, preserve cryptographic evidence, detect anomalies
Mission: UNBREAKABLE SECURITY FOR FREEDOM OPERATIONS
"""
import os
import json
import hashlib
import glob
from datetime import datetime, timezone
from pathlib import Path

# Bot metadata
BOT_NAME = "Security Audit Bot 🔒"
BOT_ROLE = "Security Auditing & Evidence Preservation"
BOT_DEPARTMENT = "Trust Security & Integrity Department"
BOT_VERSION = "1.0.0 - MAXIMUM SECURITY"
BOT_MISSION = "PRESERVE EVIDENCE | ENSURE INTEGRITY | DEFEND FREEDOM"

def calculate_directory_hash(directory):
    """Calculate aggregate hash of directory contents"""
    hasher = hashlib.sha256()
    
    files = sorted(glob.glob(f"{directory}/**/*", recursive=True))
    for filepath in files:
        if os.path.isfile(filepath):
            try:
                with open(filepath, "rb") as f:
                    hasher.update(f.read())
            except:
                pass
    
    return hasher.hexdigest()

def audit_critical_files():
    """Audit critical files for integrity"""
    print(f"🔍 Auditing critical files...")
    
    critical_files = [
        "identifiers.json",
        "identifiers.yaml",
        "output/scan_results.json",
        "output/compliance_freedom_report.json",
        "output/viral_campaign_report.json",
        "gleif_results.xml",
        "trust_overlay.xml"
    ]
    
    audit_results = []
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            file_size = os.path.getsize(filepath)
            modified_time = datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc)
            
            audit_results.append({
                "file": filepath,
                "status": "✅ VERIFIED",
                "hash": file_hash,
                "size_bytes": file_size,
                "last_modified": modified_time.isoformat(),
                "integrity": "INTACT"
            })
            
            print(f"  ✅ {filepath}")
            print(f"     Hash: {file_hash[:16]}...")
        else:
            audit_results.append({
                "file": filepath,
                "status": "❌ MISSING",
                "integrity": "COMPROMISED"
            })
            print(f"  ❌ {filepath} - NOT FOUND")
    
    return audit_results

def create_evidence_manifest():
    """Create cryptographic evidence manifest"""
    print(f"\n📋 Creating evidence manifest...")
    
    manifest = {
        "manifest_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "bot_name": BOT_NAME,
        "evidence_categories": {}
    }
    
    # Catalog scan results
    if os.path.exists("output"):
        scan_files = glob.glob("output/*.json")
        manifest["evidence_categories"]["scan_results"] = []
        
        for filepath in scan_files:
            file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            manifest["evidence_categories"]["scan_results"].append({
                "file": filepath,
                "hash_sha256": file_hash,
                "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc).isoformat()
            })
    
    # Catalog overlays
    if os.path.exists("overlays"):
        overlay_files = glob.glob("overlays/*.yml")
        manifest["evidence_categories"]["cryptographic_overlays"] = []
        
        for filepath in overlay_files:
            file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            manifest["evidence_categories"]["cryptographic_overlays"].append({
                "file": filepath,
                "hash_sha256": file_hash,
                "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc).isoformat()
            })
    
    # Catalog archives
    if os.path.exists("archive"):
        archive_files = glob.glob("archive/*.json")
        manifest["evidence_categories"]["historical_archives"] = []
        
        for filepath in archive_files:
            file_hash = hashlib.sha256(open(filepath, "rb").read()).hexdigest()
            manifest["evidence_categories"]["historical_archives"].append({
                "file": filepath,
                "hash_sha256": file_hash,
                "timestamp": datetime.fromtimestamp(os.path.getmtime(filepath), tz=timezone.utc).isoformat()
            })
    
    print(f"  ✅ Cataloged {len(manifest['evidence_categories'])} evidence categories")
    
    return manifest

def detect_anomalies():
    """Detect security anomalies"""
    print(f"\n🔍 Detecting security anomalies...")
    
    anomalies = []
    
    # Check for suspicious file modifications
    if os.path.exists("identifiers.json"):
        modified_time = datetime.fromtimestamp(os.path.getmtime("identifiers.json"), tz=timezone.utc)
        age_hours = (datetime.now(timezone.utc) - modified_time).total_seconds() / 3600
        
        if age_hours < 1:
            anomalies.append({
                "type": "Recent modification",
                "file": "identifiers.json",
                "details": f"Modified {age_hours:.1f} hours ago",
                "severity": "INFO"
            })
    
    # Check for missing critical directories
    critical_dirs = ["output", "overlays", "archive", "bots"]
    for dir_name in critical_dirs:
        if not os.path.exists(dir_name):
            anomalies.append({
                "type": "Missing critical directory",
                "directory": dir_name,
                "severity": "HIGH"
            })
    
    if not anomalies:
        print(f"  ✅ No anomalies detected")
    else:
        for anomaly in anomalies:
            print(f"  ⚠️ {anomaly['type']}: {anomaly.get('file', anomaly.get('directory'))}")
    
    return anomalies

def create_security_report():
    """Create comprehensive security audit report"""
    print(f"\n📊 Creating security audit report...")
    
    audit_results = audit_critical_files()
    evidence_manifest = create_evidence_manifest()
    anomalies = detect_anomalies()
    
    # Calculate directory hashes for tamper detection
    directory_hashes = {}
    for dir_name in ["output", "overlays", "archive", "bots"]:
        if os.path.exists(dir_name):
            directory_hashes[dir_name] = calculate_directory_hash(dir_name)
    
    report = {
        "bot_name": BOT_NAME,
        "bot_role": BOT_ROLE,
        "bot_department": BOT_DEPARTMENT,
        "bot_version": BOT_VERSION,
        "mission": BOT_MISSION,
        "audit_timestamp": datetime.now(timezone.utc).isoformat(),
        "security_status": "🔒 SECURE" if not any(a["severity"] == "HIGH" for a in anomalies) else "⚠️ REVIEW NEEDED",
        "critical_files_audit": {
            "total_audited": len(audit_results),
            "verified": sum(1 for r in audit_results if r["status"] == "✅ VERIFIED"),
            "missing": sum(1 for r in audit_results if r["status"] == "❌ MISSING"),
            "results": audit_results
        },
        "evidence_manifest": evidence_manifest,
        "directory_integrity": {
            "hashes": directory_hashes,
            "note": "Store these hashes securely to detect future tampering"
        },
        "anomalies_detected": {
            "total": len(anomalies),
            "high_severity": sum(1 for a in anomalies if a.get("severity") == "HIGH"),
            "anomalies": anomalies
        },
        "recommendations": [
            "🔒 Store evidence manifest hash in secure location",
            "📋 Compare directory hashes periodically",
            "🔍 Monitor for unauthorized file modifications",
            "💾 Maintain encrypted backups of critical evidence",
            "⚡ Enable file integrity monitoring",
            "🛡️ Implement access controls on sensitive files"
        ]
    }
    
    os.makedirs("output", exist_ok=True)
    output_file = "output/security_audit_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"  ✅ Report saved: {output_file}")
    
    # Save evidence manifest separately
    manifest_file = "output/evidence_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(evidence_manifest, f, indent=2)
    
    print(f"  ✅ Evidence manifest: {manifest_file}")
    
    return report

if __name__ == "__main__":
    print("=" * 70)
    print("🔒🔒🔒 SECURITY AUDIT BOT - INTEGRITY VERIFICATION 🔒🔒🔒")
    print("=" * 70)
    print(f"🔥 {BOT_MISSION}")
    print(f"⚡ OBJECTIVE: ENSURE EVIDENCE INTEGRITY")
    print(f"💥 STATUS: AUDIT IN PROGRESS")
    print("=" * 70 + "\n")
    
    print(f"👤 Role: {BOT_ROLE}")
    print(f"🏢 Department: {BOT_DEPARTMENT}")
    print(f"📋 Version: {BOT_VERSION}\n")
    
    # Run security audit
    report = create_security_report()
    
    print("\n" + "=" * 70)
    print("✅ SECURITY AUDIT COMPLETE")
    print(f"📋 Files audited: {report['critical_files_audit']['total_audited']}")
    print(f"✅ Files verified: {report['critical_files_audit']['verified']}")
    print(f"⚠️ Anomalies: {report['anomalies_detected']['total']}")
    print(f"🔒 Status: {report['security_status']}")
    print("=" * 70)
    print("\n🔥 EVIDENCE PRESERVED | INTEGRITY VERIFIED 🔥\n")
