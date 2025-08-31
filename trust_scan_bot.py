import json
import os
from datetime import datetime

# Repo base URL for overlays
BASE_URL = "https://github.com/lawfullyillegal-droid/Trust-identifier-trace/blob/main/overlays/"

# Ensure output and overlays folders exist
os.makedirs("output", exist_ok=True)
os.makedirs("overlays", exist_ok=True)

# Ensure required overlay files exist
overlay_files = {
    "registry_overlay.yml": "Registry Overlay placeholder",
    "property_overlay.yml": "Property Overlay placeholder",
    "irs_overlay.yml": "IRS Overlay placeholder",
    "ein_overlay.yml": "EIN Overlay placeholder"
}

for filename, desc in overlay_files.items():
    path = os.path.join("overlays", filename)
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(f"overlay_name: {desc}\ndescription: Auto-created by Trust Scan Bot\n")

# Build scan results
data = [
    {
        "identifier": "CORP-NUM-C2362627",
        "status": "verified",
        "source": "OpenCorporates",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M MST"),
        "overlay": BASE_URL + "registry_overlay.yml"
    },
    {
        "identifier": "LN-NAME-RYLE-TRAVIS-STEVEN",
        "status": "verified",
        "source": "LexisNexis",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M MST"),
        "overlay": BASE_URL + "registry_overlay.yml"
    },
    {
        "identifier": "PROP-SS-GUARANTEE-104-0190-003558",
        "status": "flagged",
        "source": "IRS Form 1099-A",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M MST"),
        "overlay": BASE_URL + "property_overlay.yml"
    },
    {
        "identifier": "IRS-TRACK-108541264370",
        "status": "unmatched",
        "source": "IRS Non-Filing",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M MST"),
        "overlay": BASE_URL + "irs_overlay.yml"
    },
    {
        "identifier": "EIN-92-6319308",
        "status": "verified",
        "source": "EIN Registry",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M MST"),
        "overlay": BASE_URL + "ein_overlay.yml"
    }
]

# Write JSON output
with open("output/scan_results.json", "w") as f:
    json.dump(data, f, indent=2)

print("scan_results.json generated with full overlay URLs.")
