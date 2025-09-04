import requests, xml.etree.ElementTree as ET
from datetime import datetime
import hashlib, yaml

# Load aliases
with open("identifiers.yaml", "r") as f:
    aliases = yaml.safe_load(f)["trust_aliases"]

# Pull GLEIF data
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=1000"
try:
    response = requests.get(gleif_url)
    data = response.json()
except Exception as e:
    print(f"⚠️ Network error querying GLEIF API: {e}")
    # Create empty data structure to allow script to continue
    data = {"data": []}

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
print(f"✅ GLEIF results saved with {len(matches_found)} matches found")

# Inject overlay hash
try:
    with open("trust_overlay.xml", "rb") as f:
        overlay = f.read()
    hash_value = hashlib.sha256(overlay).hexdigest()
    tree = ET.parse("trust_overlay.xml")
    root = tree.getroot()
    root.find("TechnicalTrace").find("OverlayHash").text = hash_value
    root.set("timestamp", datetime.now().isoformat())
    tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
    print("✅ Overlay updated.")
except Exception as e:
    print(f"⚠️ Overlay injection skipped: {e}")
