#!/usr/bin/env python3
"""
Evidence Integrity Check
========================
Hashes all files in legal-documents/, overlays/, output/, and investigations/
to build a chain-of-custody manifest (evidence_manifest.json).

Detects changes since the last manifest run.
Anchors the manifest with UTC timestamp and current Git commit SHA.

Usage:
  python3 integrity_check.py
  python3 integrity_check.py --verify        # Verify against existing manifest
  python3 integrity_check.py --dirs overlays output   # Custom directories
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).parent
MANIFEST_FILE = REPO_ROOT / "evidence_manifest.json"

DEFAULT_DIRS = [
    "legal-documents",
    "overlays",
    "output",
    "investigations",
]

# File extensions to include; skip binary/cache files
INCLUDE_EXTENSIONS = {
    ".json", ".yml", ".yaml", ".md", ".txt", ".xml", ".html", ".py", ".csv"
}

SKIP_PATTERNS = {
    "__pycache__", ".git", ".pyc", "node_modules",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit_sha() -> str:
    """Return the current Git HEAD commit SHA, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _should_include(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_PATTERNS:
            return False
    return path.suffix.lower() in INCLUDE_EXTENSIONS


def collect_hashes(directories: List[str]) -> Dict[str, str]:
    """Collect SHA-256 hashes for all qualifying files in the given directories."""
    hashes = {}
    for d in directories:
        dir_path = REPO_ROOT / d
        if not dir_path.exists():
            continue
        for file_path in sorted(dir_path.rglob("*")):
            if file_path.is_file() and _should_include(file_path):
                rel = str(file_path.relative_to(REPO_ROOT))
                try:
                    hashes[rel] = _sha256_file(file_path)
                except (IOError, OSError) as e:
                    hashes[rel] = f"ERROR: {e}"
    return hashes


def build_manifest(directories: List[str]) -> Dict[str, Any]:
    """Build a fresh evidence manifest."""
    print(f"📋 Building evidence manifest...")
    hashes = collect_hashes(directories)
    manifest = {
        "manifest_version": "1.0",
        "generated_at": _now_utc(),
        "git_commit_sha": _git_commit_sha(),
        "directories_scanned": directories,
        "total_files": len(hashes),
        "files": hashes,
    }
    print(f"   Scanned {len(hashes)} files across {len(directories)} directories")
    return manifest


def save_manifest(manifest: Dict[str, Any]) -> None:
    with open(MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Manifest saved: {MANIFEST_FILE}")


def load_manifest() -> Optional[Dict[str, Any]]:
    if not MANIFEST_FILE.exists():
        return None
    with open(MANIFEST_FILE, "r") as f:
        return json.load(f)


def verify_manifest(directories: List[str]) -> Dict[str, Any]:
    """
    Compare current file hashes against the stored manifest.
    Returns a verification report.
    """
    previous = load_manifest()
    if not previous:
        print("⚠️  No existing manifest found. Run without --verify to create one.")
        sys.exit(1)

    current_hashes = collect_hashes(directories)
    prev_files = previous.get("files", {})

    report = {
        "verified_at": _now_utc(),
        "git_commit_sha": _git_commit_sha(),
        "previous_manifest_at": previous.get("generated_at", "unknown"),
        "previous_git_sha": previous.get("git_commit_sha", "unknown"),
        "passed": [],
        "modified": [],
        "added": [],
        "removed": [],
        "integrity_ok": True,
    }

    all_paths = set(prev_files.keys()) | set(current_hashes.keys())

    for path in sorted(all_paths):
        prev_hash = prev_files.get(path)
        curr_hash = current_hashes.get(path)

        if prev_hash is None:
            report["added"].append({"path": path, "hash": curr_hash})
        elif curr_hash is None:
            report["removed"].append({"path": path, "previous_hash": prev_hash})
            report["integrity_ok"] = False
        elif prev_hash == curr_hash:
            report["passed"].append({"path": path, "hash": curr_hash})
        else:
            report["modified"].append(
                {
                    "path": path,
                    "previous_hash": prev_hash,
                    "current_hash": curr_hash,
                }
            )
            report["integrity_ok"] = False

    print(f"\n🔐 Evidence Integrity Verification Report")
    print(f"   Previous manifest: {report['previous_manifest_at']}")
    print(f"   Previous commit:   {report['previous_git_sha']}")
    print(f"   Current commit:    {report['git_commit_sha']}")
    print(f"   ✅ Unchanged:      {len(report['passed'])}")
    print(f"   🆕 Added:          {len(report['added'])}")
    print(f"   🗑  Removed:        {len(report['removed'])}")
    print(f"   ⚠️  Modified:       {len(report['modified'])}")
    print(f"   {'✅ INTEGRITY OK' if report['integrity_ok'] else '❌ CHANGES DETECTED'}")

    if report["modified"]:
        print("\n⚠️  Modified files (potential tampering):")
        for f in report["modified"]:
            print(f"   {f['path']}")
            print(f"     was: {f['previous_hash']}")
            print(f"     now: {f['current_hash']}")

    if report["removed"]:
        print("\n🗑  Removed files:")
        for f in report["removed"]:
            print(f"   {f['path']} (was: {f['previous_hash'][:16]}…)")

    if report["added"]:
        print(f"\n🆕 Added files ({len(report['added'])}):")
        for f in report["added"][:10]:
            print(f"   {f['path']}")
        if len(report["added"]) > 10:
            print(f"   … and {len(report['added'])-10} more")

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Trust Identifier Trace — Evidence Integrity Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify current files against existing manifest (instead of regenerating)",
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=DEFAULT_DIRS,
        metavar="DIR",
        help=f"Directories to scan (default: {' '.join(DEFAULT_DIRS)})",
    )
    args = parser.parse_args()

    if args.verify:
        report = verify_manifest(args.dirs)
        # Exit 1 if integrity compromised
        sys.exit(0 if report["integrity_ok"] else 1)
    else:
        manifest = build_manifest(args.dirs)
        save_manifest(manifest)
        print(f"   Git commit: {manifest['git_commit_sha']}")


if __name__ == "__main__":
    main()
