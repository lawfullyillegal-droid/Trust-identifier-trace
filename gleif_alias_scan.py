import requests, xml.etree.ElementTree as ET
from datetime import datetime
import hashlib, yaml

def load_aliases():
    """Load aliases with error handling"""
    try:
        with open("identifiers.yaml", "r") as f:
            return yaml.safe_load(f)["trust_aliases"]
    except Exception as e:
        print(f"⚠️ Failed to load aliases: {e}")
        return []

def fetch_gleif_data():
    """Fetch GLEIF data with error handling"""
    try:
        gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=1000"
        response = requests.get(gleif_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Failed to fetch GLEIF data: {e}")
        return {"data": []}

def main():
    # Load aliases
    aliases = load_aliases()
    
    # Pull GLEIF data
    data = fetch_gleif_data()
    
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

if __name__ == "__main__":
    main()
