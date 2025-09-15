import requests, xml.etree.ElementTree as ET
from datetime import datetime

def fetch_gleif_data():
    """Fetch GLEIF data with error handling"""
    try:
        print("🔧 Starting GLEIF echo test...")
        gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=5"
        response = requests.get(gleif_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Failed to fetch GLEIF data: {e}")
        return {"data": []}

def main():
    data = fetch_gleif_data()
    
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

if __name__ == "__main__":
    main()
