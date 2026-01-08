import os
import json
import requests
from datetime import datetime, timezone
from pathlib import Path
from reddit_trace import query_reddit_threads

BASE_URL = "https://raw.githubusercontent.com/lawfullyillegal-droid/Trust-identifier-trace/main/overlays/"
IDENTIFIERS_FILE = Path(__file__).parent / "identifiers.json"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_FILE = OUTPUT_DIR / "scan_results.json"
OVERLAYS_DIR = Path(__file__).parent / "overlays"

# Ensure directories exist
OVERLAYS_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

def load_identifiers():
    with open(IDENTIFIERS_FILE, "r") as f:
        return json.load(f)

def ensure_overlays(overlay_files):
    for filename, desc in overlay_files.items():
        overlay_path = OVERLAYS_DIR / filename
        if not overlay_path.exists():
            with open(overlay_path, "w") as f:
                f.write(f"# Overlay for {desc}\nidentifier: {filename.replace('_overlay.yml', '')}\ndescription: {desc}\nstatus: verified\ntimestamp: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

def scan_identifier(identifier):
    value = identifier["identifier"]
    reddit_hits = query_reddit_threads(value)
    if reddit_hits:
        identifier["reddit_hits"] = reddit_hits
        return "matched"
    return "verified"

def run_scan():
    identifiers = load_identifiers()
    results = []

    overlay_files = {}
    for ident in identifiers:
        overlay_name = f"{ident['source'].lower()}_overlay.yml"
        overlay_files[overlay_name] = ident["source"]

        status = scan_identifier(ident)
        result_block = {
            "identifier": ident["identifier"],
            "status": status,
            "source": ident["source"],
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "overlay": BASE_URL + overlay_name
        }
        if "reddit_hits" in ident:
            result_block["reddit_hits"] = ident["reddit_hits"]
        results.append(result_block)

    ensure_overlays(overlay_files)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    run_scan()
