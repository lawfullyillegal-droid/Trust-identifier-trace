import yaml
import os
import sys
from datetime import datetime

def log(msg):
    print(f"🔹 {msg}")

def main():
    try:
        # Load identifiers
        if not os.path.exists("identifiers.yaml"):
            log("❌ identifiers.yaml not found.")
            sys.exit(1)
        with open("identifiers.yaml", "r") as f:
            identifiers = yaml.safe_load(f)
        log(f"✅ Identifiers loaded: {identifiers}")

        # Load identity profile
        if not os.path.exists("identity_profile.yaml"):
            log("❌ identity_profile.yaml not found.")
            sys.exit(1)
        with open("identity_profile.yaml", "r") as f:
            profile = yaml.safe_load(f)
        log(f"✅ Identity profile loaded: {profile}")

        # Confirm overlay presence
        if not os.path.exists("trust_overlay.xml"):
            log("❌ trust_overlay.xml missing.")
            sys.exit(1)
        log("✅ Overlay file found: trust_overlay.xml")

        # Write output artifact
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
        output_path = f"output/scan_log_{timestamp}.txt"
        os.makedirs("output", exist_ok=True)
        with open(output_path, "w") as out:
            out.write("Trust Bot Scan Log\n")
            out.write(f"Timestamp: {timestamp}\n\n")
            out.write("Identifiers:\n")
            out.write(yaml.dump(identifiers))
            out.write("\nIdentity Profile:\n")
            out.write(yaml.dump(profile))
            out.write("\nOverlay: trust_overlay.xml confirmed\n")
        log(f"📁 Output written to {output_path}")

    except Exception as e:
        log(f"❌ BOT ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
