import requests, xml.etree.ElementTree as ET
from datetime import datetime, timezone
import hashlib, yaml
import sys

# Load aliases
with open("identifiers.yaml", "r") as f:
    aliases = yaml.safe_load(f)["trust_aliases"]

# Pull GLEIF data
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=1000"
response = requests.get(gleif_url)
data = response.json()

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
timestamp.text = datetime.now(timezone.utc).isoformat()
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
    with open("trust_overlay.xml", "rb") as f:
        overlay = f.read()
    hash_value = hashlib.sha256(overlay).hexdigest()
    tree = ET.parse("trust_overlay.xml")
    root = tree.getroot()
    root.find("TechnicalTrace").find("OverlayHash").text = hash_value
    root.set("timestamp", datetime.now(timezone.utc).isoformat())
    tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
    print("Overlay updated successfully.")
except Exception as e:
    # Avoid Unicode issues on Windows by using ASCII-only characters
    print(f"Overlay injection skipped: {str(e)}")
    # Write error to file to avoid console encoding issues
    with open("gleif_scan_error.log", "w", encoding="utf-8") as error_file:
        error_file.write(f"Error: {str(e)}\n")
