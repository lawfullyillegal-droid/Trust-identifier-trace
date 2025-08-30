print("🚀 gleif_trace.py started")
import traceback
try:
    
    import requests
    import xml.etree.ElementTree as ET
    from datetime import datetime
    import hashlib
    import os

    print("📡 Modules imported successfully")

    # Trust name to search
    trust_name = "THE TRAVIS RYLE PRIVATE BANK–ESTATE & TRUST"
    gleif_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={trust_name}"

    print(f"🔍 Fetching GLEIF data for: {trust_name}")
    response = requests.get(gleif_url)
    data = response.json()
    print("📦 GLEIF data received")

    # Save results
    root = ET.Element("GLEIFResults")
    timestamp = ET.SubElement(root, "Timestamp")
    timestamp.text = datetime.now().isoformat()
    matches = ET.SubElement(root, "Matches")

    for record in data.get("data", []):
        entity = record.get("attributes", {}).get("entity", {})
        match = ET.SubElement(matches, "Match")
        ET.SubElement(match, "LegalName").text = entity.get("legalName", "N/A")
        ET.SubElement(match, "Country").text = entity.get("legalAddress", {}).get("country", "N/A")
        ET.SubElement(match, "LEI").text = record.get("id", "N/A")

    tree = ET.ElementTree(root)
    tree.write("gleif_results.xml", encoding="utf-8", xml_declaration=True)
    print("📄 gleif_results.xml written")

    # Trigger overlay injection if match found
    if data.get("data"):
        with open("trust_overlay.xml", "rb") as f:
            overlay = f.read()
        hash_value = hashlib.sha256(overlay).hexdigest()
        tree = ET.parse("trust_overlay.xml")
        root = tree.getroot()
        root.find("TechnicalTrace").find("OverlayHash").text = hash_value
        root.set("timestamp", datetime.now().isoformat())
        tree.write("trust_overlay.xml", encoding="utf-8", xml_declaration=True)
        print("✅ Overlay updated with live hash and timestamp.")
    else:
        print("⚠️ No GLEIF match found. Overlay not triggered.")

    # Write scan log
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "scan_log.txt"), "w") as f:
        f.write("✅ Trust scan executed\n")
        f.write("Identifiers traced: [GLEIF match logic executed]\n")
    print("🔥 scan_log.txt written")

except Exception as e:
    print("❌ Script failed with error:")
    traceback.print_exc()
