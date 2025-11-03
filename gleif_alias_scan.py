import requests, xml.etree.ElementTree as ET
from datetime import datetime
import hashlib, yaml
import os
from network_utils import make_request_with_retry, NetworkError

# Load aliases
try:
    with open("identifiers.yaml", "r") as f:
        aliases = yaml.safe_load(f)["trust_aliases"]
except FileNotFoundError:
    print("⚠️ identifiers.yaml not found, using default aliases")
    aliases = ["TRAVIS RYLE", "RYLE PRIVATE BANK", "TRAVIS RYLE TRUST"]

# Pull GLEIF data with enhanced error handling and retry logic
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=1000"
try:
    # Use network_utils for robust request with retry logic
    response = make_request_with_retry(
        url=gleif_url,
        max_retries=3,
        timeout=15,
        backoff_factor=1.5
    )
    data = response.json()
    print("✅ Successfully fetched GLEIF data")
except NetworkError as e:
    print(f"⚠️ Network error: {e}")
    print("🔄 Running in offline mode with mock data...")
    # Create mock data for offline mode
    data = {
        "data": [
            {
                "id": "MOCK-LEI-RYLE-001",
                "attributes": {
                    "entity": {
                        "legalName": "Travis Ryle Private Bank Holdings LLC (Mock)",
                        "legalAddress": {
                            "country": "US"
                        }
                    }
                }
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
        tree = ET.parse("trust_overlay.xml")
        root = tree.getroot()
        
        # Find or create TechnicalTrace element
        tech_trace = root.find("TechnicalTrace")
        if tech_trace is None:
            tech_trace = ET.SubElement(root, "TechnicalTrace")
        
        # Find or create OverlayHash element
        overlay_hash = tech_trace.find("OverlayHash")
        if overlay_hash is None:
            overlay_hash = ET.SubElement(tech_trace, "OverlayHash")
        
        overlay_hash.text = hash_value
        root.set("timestamp", datetime.now().isoformat())
        tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
        print("✅ Overlay updated.")
    else:
        print("⚠️ trust_overlay.xml not found, skipping overlay injection")
except Exception as e:
    print(f"⚠️ Overlay injection skipped: {e}")
