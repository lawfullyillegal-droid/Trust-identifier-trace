import urllib.request
import urllib.parse
import json

def fetch_api(url):
    """Helper function to execute silent API requests."""
    req = urllib.request.Request(url, headers={'Accept': 'application/vnd.api+json'})
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return None

def execute_recursive_hunt(target_name):
    print(f"[*] Initiating Recursive Corporate Network Hunt for: {target_name}")

    # Step 1: Base Entity Extraction
    safe_target = urllib.parse.quote(target_name)
    base_url = f"https://api.gleif.org/api/v1/lei-records?filter[entity.legalName]={safe_target}"
    base_payload = fetch_api(base_url)

    if not base_payload or not base_payload.get('data'):
        print("[!] Target masking detected. Base LEI not found.")
        return

    node = base_payload['data'][0]
    base_lei = node['attributes']['lei']
    base_name = node['attributes']['entity']['legalName']['name']

    print(f"\n[+] BASE TARGET SECURED: {base_name} (LEI: {base_lei})")
    print("[*] Traversing corporate ownership tree...")

    # Step 2: Extract Direct Parent (Who owns them?)
    parent_url = f"https://api.gleif.org/api/v1/lei-records/{base_lei}/direct-parent"
    parent_payload = fetch_api(parent_url)

    if parent_payload and parent_payload.get('data'):
        parent_data = parent_payload['data']
        # Handle JSON array structure if multiple/single parent
        p_node = parent_data[0] if isinstance(parent_data, list) else parent_data
        p_name = p_node['attributes']['entity']['legalName']['name']
        p_lei = p_node['attributes']['lei']
        p_jur = p_node['attributes']['entity']['jurisdiction']
        print(f"\n[+] PARENT NODE DISCOVERED:")
        print(f"    <- [OWNER] {p_name}")
        print(f"       LEI: {p_lei} | Jurisdiction: {p_jur}")
    else:
        print("\n[-] No ultimate parent found. Target operates as the peak holding entity.")

    # Step 3: Extract Direct Children (Who do they own?)
    children_url = f"https://api.gleif.org/api/v1/lei-records/{base_lei}/direct-children"
    children_payload = fetch_api(children_url)

    if children_payload and children_payload.get('data'):
        children = children_payload['data']
        print(f"\n[+] FOUND {len(children)} SUBSIDIARY CHILD-NODE(S):")
        for child in children:
            c_name = child['attributes']['entity']['legalName']['name']
            c_lei = child['attributes']['lei']
            c_jur = child['attributes']['entity']['jurisdiction']
            print(f"    -> [SHIELD] {c_name}")
            print(f"       LEI: {c_lei} | Jurisdiction: {c_jur}\n")
    else:
        print("\n[-] No direct subsidiary nodes exposed in the public registry.")

    print("[+] Recursive traversal complete. Network mapped.")

if __name__ == "__main__":
    execute_recursive_hunt("Equifax Inc.")