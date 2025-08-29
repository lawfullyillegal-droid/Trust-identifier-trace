import yaml
import os
import sys
from datetime import datetime

def log(msg):
    print(f"🔹 {msg}")

def main():
    try:
        log("🚨 BOT STARTED")
        log(f"📂 Current directory: {os.getcwd()}")
        log(f"📄 Files in repo: {os.listdir()}")

        # Load identifiers
        with open("identifiers.yaml", "r") as f:
            identifiers = yaml.safe_load(f)
        log(f"✅ Identifiers loaded: {identifiers}")

        # Load identity profile
        with open("identity_profile.yaml", "r") as f:
            profile = yaml.safe_load(f)
        log(f"✅ Identity profile loaded: {profile}")

        # Scan ADOT identifiers
        adot_ids = identifiers.get("adot_numbers", [])
        if not adot_ids:
            log("⚠️ No ADOT identifiers found.")
        else:
            log(f"🔍 Scanning {len(adot_ids)} ADOT identifiers...")
            for aid in adot_ids:
                if isinstance(aid, str) and aid.isdigit():
                    log(f"✅ Valid ADOT ID: {aid}")
                else:
                    log(f"❌ Invalid ADOT ID format: {aid}")

        # Confirm overlay presence
        if os.path.exists("trust_overlay.xml"):
            log("✅ Overlay file found: trust_overlay.xml")
        else:
            log("❌ Overlay file missing.")
            sys.exit(1)

        # Convert overlay to HTML for GitHub Pages
        with open("trust_overlay.xml", "r") as xml_file:
            overlay_content = xml_file.read()
        html_overlay = f"<html><body><pre>{overlay_content}</pre></body></html>"
        docs_path = "docs/overlay.html"
        os.makedirs("docs", exist_ok=True)
        with open(docs_path, "w") as html_file:
            html_file.write(html_overlay)
        log(f"🌐 Overlay HTML written to {docs_path}")

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
