import requests, xml.etree.ElementTree as ET
from datetime import datetime, timezone

print("🔧 Starting GLEIF echo test...")

# Pull GLEIF data
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=5"
try:
    response = requests.get(gleif_url, timeout=30)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"Warning: Could not fetch GLEIF data: {e}")
    data = {"data": []}

# Log to XML
root = ET.Element("GLEIFEcho")
timestamp = ET.SubElement(root, "Timestamp")
timestamp.text = datetime.now(timezone.utc).isoformat()
entities = ET.SubElement(root, "Entities")

for record in data.get("data", []):
    entity = record.get("attributes", {}).get("entity", {})
    item = ET.SubElement(entities, "Entity")
    ET.SubElement(item, "LegalName").text = entity.get("legalName", "N/A")
    ET.SubElement(item, "Country").text = entity.get("legalAddress", {}).get("country", "N/A")
    ET.SubElement(item, "LEI").text = record.get("id", "N/A")

tree = ET.ElementTree(root)
tree.write("gleif_echo.xml", encoding="utf-8", xml_declaration=True)
print("✅ Echo file saved as gleif_echo.xml")
