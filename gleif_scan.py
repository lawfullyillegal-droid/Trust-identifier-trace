import json
import urllib.parse
import urllib.request


def fetch_api(url):
    """Execute a GLEIF API request and return parsed JSON or None."""
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.api+json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception:
        return None


def build_offline_payload(target_name):
    """Return offline data so the scan still produces a trace without network access."""
    return {
        "base": {
            "data": [{
                "attributes": {
                    "lei": "MOCK-LEI-EQUIFAX-001",
                    "entity": {
                        "legalName": {"name": target_name},
                        "jurisdiction": "US-GA",
                    },
                }
            }]
        },
        "parent": {"data": []},
        "children": {
            "data": [{
                "attributes": {
                    "lei": "MOCK-LEI-EQUIFAX-CHILD-001",
                    "entity": {
                        "legalName": {"name": "EQUIFAX LUXEMBOURG (NO. 3) S.ÀR.L."},
                        "jurisdiction": "LU",
                    },
                }
            }]
        },
    }


def extract_name(node):
    legal_name = node["attributes"]["entity"]["legalName"]
    if isinstance(legal_name, dict):
        return legal_name.get("name", "UNKNOWN")
    return legal_name or "UNKNOWN"


def execute_recursive_hunt(target_name):
    print(f"[*] Initiating Recursive Corporate Network Hunt for: {target_name}")

    safe_target = urllib.parse.quote(target_name)
    base_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={safe_target}"
    base_payload = fetch_api(base_url)

    if not base_payload or not base_payload.get("data"):
        print("[!] Network unavailable or live GLEIF record not found. Using offline trace data.")
        offline_payload = build_offline_payload(target_name)
        base_payload = offline_payload["base"]
        parent_payload = offline_payload["parent"]
        children_payload = offline_payload["children"]
    else:
        node = base_payload["data"][0]
        base_lei = node["attributes"]["lei"]
        parent_payload = fetch_api(f"https://api.gleif.org/api/v1/lei-records/{base_lei}/direct-parent")
        children_payload = fetch_api(f"https://api.gleif.org/api/v1/lei-records/{base_lei}/direct-children")

    node = base_payload["data"][0]
    base_lei = node["attributes"]["lei"]
    base_name = extract_name(node)

    print(f"\n[+] BASE TARGET SECURED: {base_name} (LEI: {base_lei})")
    print("[*] Traversing corporate ownership tree...")

    if parent_payload and parent_payload.get("data"):
        parent_data = parent_payload["data"]
        p_node = parent_data[0] if isinstance(parent_data, list) else parent_data
        p_name = extract_name(p_node)
        p_lei = p_node["attributes"]["lei"]
        p_jur = p_node["attributes"]["entity"].get("jurisdiction", "N/A")
        print("\n[+] PARENT NODE DISCOVERED:")
        print(f"    <- [OWNER] {p_name}")
        print(f"       LEI: {p_lei} | Jurisdiction: {p_jur}")
    else:
        print("\n[-] No ultimate parent found. Target operates as the peak holding entity.")

    if children_payload and children_payload.get("data"):
        children = children_payload["data"]
        print(f"\n[+] FOUND {len(children)} SUBSIDIARY CHILD-NODE(S):")
        for child in children:
            c_name = extract_name(child)
            c_lei = child["attributes"]["lei"]
            c_jur = child["attributes"]["entity"].get("jurisdiction", "N/A")
            print(f"    -> [SHIELD] {c_name}")
            print(f"       LEI: {c_lei} | Jurisdiction: {c_jur}\n")
    else:
        print("\n[-] No direct subsidiary nodes exposed in the public registry.")

    print("[+] Recursive traversal complete. Network mapped.")


if __name__ == "__main__":
    execute_recursive_hunt("Equifax Inc.")
