import requests, xml.etree.ElementTree as ET
from datetime import datetime
import sys

print("🔧 Starting GLEIF echo test...")

# Pull GLEIF data with error handling
gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=5"
try:
    response = requests.get(gleif_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    print("✅ Successfully fetched GLEIF data")
except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
    print(f"⚠️ Network error: {e}")
    print("🔄 Running in offline mode with mock data...")
    # Create mock data for offline mode
    data = {
        "data": [
            {
                "id": "MOCK-LEI-001",
                "attributes": {
                    "entity": {
                        "legalName": "Mock Entity 1 (Offline Mode)",
                        "legalAddress": {
                            "country": "US"
                        }
                    }
                }
            },
            {
                "id": "MOCK-LEI-002", 
                "attributes": {
                    "entity": {
                        "legalName": "Mock Entity 2 (Offline Mode)",
                        "legalAddress": {
                            "country": "CA"
                        }
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
