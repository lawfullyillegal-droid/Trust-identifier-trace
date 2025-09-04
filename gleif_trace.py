import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import hashlib
import os
import traceback

print("📡 Modules imported successfully")

# Trust name to search
trust_name = "THE TRAVIS RYLE PRIVATE BANK–ESTATE & TRUST"
gleif_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={trust_name}"

# Identifier payload
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

# Create output directory if needed
os.makedirs("output", exist_ok=True)
log_path = "output/scan_log.txt"

with open(log_path, "w") as log:
    for identifier in IDENTIFIER_PAYLOAD:
        print(f"🔍 Scanning external sources for: {identifier}")
        log.write(f"[{datetime.now(timezone.utc)}] Scanning: {identifier}\n")

        try:
            query_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={identifier}"
            response = requests.get(query_url, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("data"):
                print(f"✅ Match found for {identifier}")
                log.write(f"[MATCH] {identifier}\n")
            else:
                print(f"❌ No match for {identifier}")
                log.write(f"[NO MATCH] {identifier}\n")

        except Exception as e:
            print(f"⚠️ Error scanning {identifier}: {e}")
            log.write(f"[ERROR] {identifier}: {traceback.format_exc()}\n")

print(f"📄 Scan complete. Log saved to {log_path}")
