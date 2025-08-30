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
