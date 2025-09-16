import requests, xml.etree.ElementTree as ET
from datetime import datetime
import hashlib, yaml

try:
    # Load aliases
    with open("identifiers.yaml", "r") as f:
        aliases = yaml.safe_load(f)["trust_aliases"]

    # Pull GLEIF data with error handling
    gleif_url = "https://api.gleif.org/api/v1/lei-records?page[size]=1000"
    try:
        response = requests.get(gleif_url, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"⚠️ GLEIF API request failed: {e}")
        data = {"data": []}
    except Exception as e:
        print(f"⚠️ Failed to parse GLEIF data: {e}")
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
    print(f"✅ GLEIF scan complete. Found {len(matches_found)} matches.")

    # Inject overlay hash
    try:
        with open("trust_overlay.xml", "rb") as f:
            overlay = f.read()
        hash_value = hashlib.sha256(overlay).hexdigest()
        tree = ET.parse("trust_overlay.xml")
        root = tree.getroot()
        
        # Check if TechnicalTrace and OverlayHash elements exist
        tech_trace = root.find("TechnicalTrace")
        if tech_trace is None:
            tech_trace = ET.SubElement(root, "TechnicalTrace")
        
        overlay_hash = tech_trace.find("OverlayHash")
        if overlay_hash is None:
            overlay_hash = ET.SubElement(tech_trace, "OverlayHash")
        
        overlay_hash.text = hash_value
        root.set("timestamp", datetime.now().isoformat())
        tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
        print("✅ Overlay updated.")
    except FileNotFoundError:
        print("⚠️ trust_overlay.xml not found, creating basic structure")
        # Create basic overlay structure if file doesn't exist
        root = ET.Element("TrustOverlay", timestamp=datetime.now().isoformat())
        tech_trace = ET.SubElement(root, "TechnicalTrace")
        ET.SubElement(tech_trace, "OverlayHash").text = "placeholder"
        tree = ET.ElementTree(root)
        tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
        print("✅ Basic overlay structure created.")
    except Exception as e:
        print(f"⚠️ Overlay injection skipped: {e}")

except FileNotFoundError as e:
    print(f"❌ Required file not found: {e}")
    exit(1)
except Exception as e:
    print(f"❌ GLEIF scan failed: {e}")
    exit(1)
