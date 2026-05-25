import sys
# Try to ensure stdout can emit UTF-8 on Windows runners; ignore if not supported
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import hashlib
import yaml
import os

# Load aliases
try:
    with open("identifiers.yaml", "r", encoding="utf-8") as f:
        aliases = yaml.safe_load(f).get("trust_aliases", [])
        if not aliases:
            aliases = ["TRAVIS RYLE", "RYLE PRIVATE BANK", "TRAVIS RYLE TRUST"]
except FileNotFoundError:
    print("Warning: identifiers.yaml not found, using default aliases")
    aliases = ["TRAVIS RYLE", "RYLE PRIVATE BANK", "TRAVIS RYLE TRUST"]
except Exception as e:
    print(f"Warning: could not read identifiers.yaml: {e}")
    aliases = ["TRAVIS RYLE", "RYLE PRIVATE BANK", "TRAVIS RYLE TRUST"]

# Pull GLEIF data with error handling
gleif_base = "https://api.gleif.org/api/v1/lei-records"
params = {"page[size]": 1000}
data = None

try:
    response = requests.get(gleif_base, params=params, timeout=10)
    # If status is error, raise to go to exception handling
    response.raise_for_status()
    # Parse JSON safely
    data = response.json()
    print("Successfully fetched GLEIF data")
except requests.exceptions.HTTPError as e:
    # Log status code and body for debugging, then fall back
    try:
        body = response.text
    except Exception:
        body = "<unavailable response body>"
    print(f"Network HTTP error: {response.status_code} - {e}")
    print(f"Response body: {body}")
except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error while fetching GLEIF data: {e}")

# If fetch failed, use mock/offline data
if not data:
    print("Running in offline mode with mock data...")
    data = {
        "data": [
            {
                "id": "MOCK-LEI-RYLE-001",
                "attributes": {
                    "entity": {
                        "legalName": "Travis Ryle Private Bank Holdings LLC (Mock)",
                        "legalAddress": {"country": "US"},
                    }
                },
            }
        ]
    }

# Match aliases
matches_found = []
for record in data.get("data", []):
    legal_name = record.get("attributes", {}).get("entity", {}).get("legalName", "")
    for alias in aliases:
        if alias.lower() in legal_name.lower():
            matches_found.append(record)

# Log to XML
root = ET.Element("GLEIFResults")
timestamp = ET.SubElement(root, "Timestamp")
timestamp.text = datetime.now().isoformat()
matches = ET.SubElement(root, "Matches")

for match in matches_found:
    entity = match.get("attributes", {}).get("entity", {})
    match_el = ET.SubElement(matches, "Match")
    ET.SubElement(match_el, "LegalName").text = entity.get("legalName", "N/A")
    ET.SubElement(match_el, "Country").text = entity.get("legalAddress", {}).get("country", "N/A")
    ET.SubElement(match_el, "LEI").text = match.get("id", "N/A")

tree = ET.ElementTree(root)
tree.write("gleif_results.xml", encoding="utf-8", xml_declaration=True)

# Inject overlay hash
try:
    if os.path.exists("trust_overlay.xml"):
        with open("trust_overlay.xml", "rb") as f:
            overlay = f.read()
        hash_value = hashlib.sha256(overlay).hexdigest()
        tree_overlay = ET.parse("trust_overlay.xml")
        root_overlay = tree_overlay.getroot()

        tech_trace = root_overlay.find("TechnicalTrace")
        if tech_trace is None:
            tech_trace = ET.SubElement(root_overlay, "TechnicalTrace")

        overlay_hash = tech_trace.find("OverlayHash")
        if overlay_hash is None:
            overlay_hash = ET.SubElement(tech_trace, "OverlayHash")

        overlay_hash.text = hash_value
        root_overlay.set("timestamp", datetime.now().isoformat())
        tree_overlay.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
        print("Overlay updated.")
    else:
        print("trust_overlay.xml not found, skipping overlay injection")
except Exception as e:
    print(f"Overlay injection skipped: {e}")
