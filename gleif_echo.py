import requests, xml.etree.ElementTree as ET
from datetime import datetime

print("🔧 Starting GLEIF echo test...")

# Pull GLEIF data with offline fallback
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=5"
try:
    response = requests.get(gleif_url, timeout=10)
    data = response.json()
    print("✅ Connected to GLEIF API successfully")
except Exception as e:
    print(f"⚠️ Network connection failed, using offline mode: {e}")
    # Fallback sample data for testing
    data = {
        "data": [
            {
                "id": "254900SAMPLE1234567890",
                "attributes": {
                    "entity": {
                        "legalName": "Sample Trust Entity One",
                        "legalAddress": {"country": "US"}
                    }
                }
            },
            {
                "id": "254900SAMPLE1234567891", 
                "attributes": {
                    "entity": {
                        "legalName": "Sample Trust Entity Two",
                        "legalAddress": {"country": "CA"}
                    }
                }
            },
            {
                "id": "254900SAMPLE1234567892",
                "attributes": {
                    "entity": {
                        "legalName": "The Travis Ryle Private Bank Sample",
                        "legalAddress": {"country": "US"}
                    }
                }
            }
        ]
    }

# Log to XML
root = ET.Element("GLEIFEcho")
timestamp = ET.SubElement(root, "Timestamp")
timestamp.text = datetime.now().isoformat()
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
