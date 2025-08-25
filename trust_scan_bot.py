import requests
from datetime import datetime

targets = [
    "https://www.azcc.gov",
    "https://www.sec.gov",
    "https://opencorporates.com",
    "https://www.lexisnexis.com",
    "https://www.azdor.gov",
    "https://www.azdes.gov",
    "https://www.azdot.gov"
]

identifiers = [
    "TRAVIS RYLE", "TRAVIS STEVEN RYLE",
    "LexID 11133734", "Case Number 31568224", "PIN SMMT4WP",
    "Birth Certificate Number 104-0190 003558", "SSN 602-05-7209",
    "EIN 92-6319308", "ADOT Customer Number 31568224",
    "Namespace ID SMMT4WP", "Child Support Participant ID 11133734",
    "Withdrawal Reference 6789-RYLE", "Aztec Constructors", "INBC", "Edward Duarte"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

for url in targets:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        content = response.text
        for id in identifiers:
            if id in content:
                print(f"MATCH FOUND: '{id}' on {url}")
                with open("TrustScanLog.txt", "a") as log:
                    log.write(f"MATCH FOUND: '{id}' on {url} at {datetime.now()}\n")
    except Exception as e:
        print(f"ERROR scanning {url}: {e}")
