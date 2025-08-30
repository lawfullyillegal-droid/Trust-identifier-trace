 HEAD
import json, os, re, yaml

def load_identifiers():
    with open("identifiers.json") as f:
        return json.load(f)

def load_overlays():
    overlays = []
    for file in os.listdir("overlays"):
        if file.endswith(".yml") or file.endswith(".yaml"):
            with open(os.path.join("overlays", file)) as f:
                overlays.append(yaml.safe_load(f))
    return overlays

def match_identifier(identifier):
    patterns = [
        r"TR-[A-Z0-9]{6}",
        r"CA-UCC-[0-9]{8}",
        r"STATE-[A-Z]{2}-[0-9]{4}",
        r"NS-[A-Z0-9]{4,8}"
    ]
    return any(re.match(p, identifier) for p in patterns)

def scan(identifiers, overlays):
    results = []
    for identifier in identifiers:
        status, reason = "unmatched", "No pattern match"
        if match_identifier(identifier):
            status, reason = "flagged", "Pattern match"
        for overlay in overlays:
            if identifier in str(overlay):
                status, reason = "verified", "Found in overlay"
        results.append({"identifier": identifier, "status": status, "reason": reason})
    return results

def save_results(results):
    os.makedirs("output", exist_ok=True)
    with open("output/scan_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    save_results(scan(load_identifiers(), load_overlays()))

def main():
    try:
        print("🔥 BOT STARTED")

        print("✅ Loading identifiers.yaml...")
        with open("identifiers.yaml", "r") as f:
            identifiers = yaml.safe_load(f)

        print("✅ Loading identity_profile.yaml...")
        with open("identity_profile.yaml", "r") as f:
            profile = yaml.safe_load(f)

        print("✅ Loading trust_overlay.xml...")
        with open("docs/trust_overlay.xml", "r") as f:
            overlay = f.read()

        print("✅ Writing output file...")
        os.makedirs("output", exist_ok=True)
        output_path = f"output/scan_log_{datetime.utcnow().isoformat()}Z.txt"
        with open(output_path, "w") as f:
            f.write("Scan complete.\n")
            f.write(f"Identifiers: {identifiers}\n")
            f.write(f"Profile: {profile}\n")
            f.write("Overlay loaded.\n")

        print("🔄 Committing output and overlay to GitHub...")
        os.system("git config --global user.name 'TrustBot'")
        os.system("git config --global user.email 'trustbot@localhost'")
        os.system("git add output/*.txt docs/overlay.html")
        os.system("git commit -m 'Auto-commit scan results'")
        os.system("git push https://x-access-token:${{ secrets.GH_TOKEN }}@github.com/${{ github.repository }} HEAD:main")

        print("✅ BOT COMPLETED")

    except Exception as e:
        print(f"❌ BOT FAILED: {e}")
 6630a7a465a9099f0f6e596ef7aa3c3b73c4beba
