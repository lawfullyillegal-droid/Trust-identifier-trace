identifiers = [
    "TRAVIS RYLE",
    "TRAVIS STEVEN RYLE",
    "Ryle, Travis",
    "Travis S. Ryle",
    "T. Ryle",
    "LexID 11133734",
    "LexID",
    "Case Number 31568224",
    "PIN SMMT4WP",
    "Namespace ID SMMT4WP",
    "Birth Certificate Number 104-0190 003558",
    "SSN 602-05-7209",
    "Social Security Number",
    "EIN 92-6319308",
    "ADOT Customer Number 31568224",
    "ADOT ID",
    "Customer ID 31568224",
    "Child Support Participant ID 11133734",
    "Withdrawal Reference 6789-RYLE",
    "Aztec Constructors",
    "INBC",
    "Edward Duarte",
    "THE TRAVIS RYLE PRIVATE BANK ESTATE",
    "Affidavit of Intent to Homeschool",
    "Rural Route H049-70",
    "Trust Identifier",
    "Trust Overlay",
    "GLEIF",
    "Global Legal Entity Identifier",
    "DUNS",
    "NCES"
]
import requests
from datetime import datetime

targets = [
    "https://raw.githubusercontent.com/lawfullyillegal-droid/Trust-identifier-trace/main/test_match_page.html",
    "https://www.azcc.gov",
    "https://www.sec.gov",
    "https://opencorporates.com",
    "https://www.lexisnexis.com",
    "https://www.azdor.gov",
    "https://www.azdes.gov",
    "https://www.azdot.gov"
]

headers = {
    "User-Agent": "TrustScanBot/1.0"
}

with open("TrustScanLog.txt", "a", encoding="utf-8") as log:
    log.write(f"\n--- Scan started at {datetime.now()} ---\n")

    for url in targets:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            content = response.text

            for line in content.splitlines():
                for id in identifiers:
                    if id.lower() in line.lower():
                        log.write(f"MATCH FOUND: '{id}' on {url} → {line.strip()} at {datetime.now()}\n")

                        overlay_filename = f"Overlay_{id.replace(' ', '_')}.xml"
                        with open(overlay_filename, "w", encoding="utf-8") as overlay:
                            overlay.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<TrustOverlay>
  <Identifier>{id}</Identifier>
  <Source>{url}</Source>
  <Timestamp>{datetime.now()}</Timestamp>
  <TrustReference>THE TRAVIS RYLE PRIVATE BANK ESTATE</TrustReference>
  <Assertion>Match detected in public registry content</Assertion>
</TrustOverlay>
""")

        except Exception as e:
            log.write(f"ERROR scanning {url}: {e} at {datetime.now()}\n")
