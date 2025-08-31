print("🚀 gleif_trace.py started")
IDENTIFIER_PAYLOAD = [
    "BRN-CA-1983-104",
    "CERT-CA-003558",
    "DOB-1983-01-20-0815",
    "SSN-602-05-7209",
    "EIN-92-6319308",
    "ENTITY-THE-TRAVIS-RYLE-PRIVATE-BANK",
    "ADDR-5570-W-TONTO-PL-GOLDEN-VALLEY-AZ-86413",
    "CSE-PARTICIPANT-30000000646889",
    "ADOT-CUST-16088582",
    "LN-NAME-RYLE-TRAVIS-STEVEN",
    "CORP-NUM-C2362627",
    "IRS-TRACK-108541264370",
    "ACCT-433187894832",
    "PROP-SS-GUARANTEE-104-0190-003558"
]

    "BRN-CA-1983-104",
    "CERT-CA-003558",
    "DOB-1983-01-20-0815",
    "SSN-602-05-7209",
    "EIN-92-6319308",
    "ENTITY-THE-TRAVIS-RYLE-PRIVATE-BANK",
    "ADDR-5570-W-TONTO-PL-GOLDEN-VALLEY-AZ-86413",
    "CSE-PARTICIPANT-30000000646889",
    "ADOT-CUST-16088582",
    "LN-NAME-RYLE-TRAVIS-STEVEN",
    "CORP-NUM-C2362627",
    "IRS-TRACK-108541264370",
    "ACCT-433187894832",
    "PROP-SS-GUARANTEE-104-0190-003558"
for identifier in IDENTIFIER_PAYLOAD:
    print(f"🔍 Scanning external sources for: {identifier}")
    # Example: build a query URL using the identifier
    query_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={identifier}"
    response = requests.get(query_url)
    data = response.json()

    # Log result if match found
    if data.get("data"):
        print(f"✅ Match found for {identifier}")
        # You can log to XML or TrustScanLog.txt here
    else:
        print(f"❌ No match for {identifier}")

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
       for identifier in IDENTIFIER_PAYLOAD:
    print(f"🔍 Scanning external sources for: {identifier}")
    query_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={identifier}"
    response = requests.get(query_url)
    data = response.json()

    if data.get("data"):
        print(f"✅ Match found for {identifier}")
    else:
        print(f"❌ No match for {identifier}")
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
