import requests, xml.etree.ElementTree as ET
from datetime import datetime
import sys

print("🔧 Starting GLEIF echo test...")

NAME_KEYS = ("name", "legalName", "label")

def stringify_gleif_field(value, default="N/A", max_depth=3):
    """
    Convert GLEIF fields to plain strings for XML output.
    
    Args:
        value: Field value from the GLEIF response (may be str, dict, or None).
        default: Fallback string when value is missing.
        max_depth: Remaining recursion depth for nested dictionaries to prevent excessive traversal.
    
    Returns:
        A string suitable for XML serialization, extracting common name-related keys from
        dicts (checked in the order: name, legalName, label, matching GLEIF API shape)
        and falling back to the provided default when necessary.
    """
    if value is None:
        return default
    if max_depth <= 0:
        return default
    if isinstance(value, dict):
        # Prefer common name-like keys if present
        for key in NAME_KEYS:
            field = value.get(key)
            if field is not None:
                if isinstance(field, dict):
                    return stringify_gleif_field(field, default=default, max_depth=max_depth-1)
                return str(field)
        # Fallback to default for empty dicts or stringified dict when populated
        return default if not value else str(value)
    return str(value)

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
    ET.SubElement(item, "LegalName").text = stringify_gleif_field(entity.get("legalName"))
    country_val = entity.get("legalAddress", {}).get("country")
    ET.SubElement(item, "Country").text = stringify_gleif_field(country_val)
    ET.SubElement(item, "LEI").text = stringify_gleif_field(record.get("id"))

tree = ET.ElementTree(root)
tree.write("gleif_echo.xml", encoding="utf-8", xml_declaration=True)
print("✅ Echo file saved as gleif_echo.xml")
