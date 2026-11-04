#!/usr/bin/env python3
"""Build a public, provenance-aware index without publishing source files."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

STATES = {"allegation", "documented", "disputed", "withdrawn"}
SHA256 = re.compile(r"^[a-f0-9]{64}$")
PRIVATE_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\b(?:\+?1[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b")


def clean(value, what):
    if not isinstance(value, str) or not value.strip() or PRIVATE_PATTERN.search(value):
        raise ValueError(f"{what} is empty or may contain private identifiers")
    return value.strip()


def build(source_path):
    data = json.loads(Path(source_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Input must be an object")
    # A manifest checked into a public repo must not hold hidden/private entries.
    # The public flag only controls the generated index, not GitHub file access.
    if Path(source_path).name == "intake.json" and Path(source_path).parent.name == "public_records":
        for group in ("sources", "claims", "links"):
            for item in data.get(group, []):
                if not item.get("public", False) or "local_path" in item:
                    raise ValueError("Committed public_records/intake.json must contain approved public entries only")
    sources, claims, links = [], [], []
    ids = set()
    for item in data.get("sources", []):
        if not item.get("public", False):
            continue
        key = clean(item.get("id"), "source id")
        if key in ids:
            raise ValueError(f"duplicate source id: {key}")
        ids.add(key)
        url = clean(item.get("url"), "source url")
        parts = urlsplit(url)
        if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
            raise ValueError("Public source must have an HTTPS URL")
        digest = item.get("sha256")
        if digest is not None and not SHA256.fullmatch(digest):
            raise ValueError("Invalid SHA-256 digest")
        verification = "reference_only"
        if item.get("local_path"):
            file_path = (Path(source_path).parent / item["local_path"]).resolve()
            if not file_path.is_file():
                raise ValueError(f"Missing local source for {key}")
            with file_path.open("rb") as handle:
                computed = hashlib.file_digest(handle, "sha256").hexdigest()
            if digest and digest != computed:
                raise ValueError(f"SHA-256 mismatch for {key}")
            digest = computed
            verification = "local_bytes_hashed"
        sources.append({"id": key, "title": clean(item.get("title"), "source title"),
                        "url": url, "sha256": digest, "verification": verification})
    claim_ids = set()
    for item in data.get("claims", []):
        if not item.get("public", False):
            continue
        key = clean(item.get("id"), "claim id")
        if key in claim_ids:
            raise ValueError(f"duplicate claim id: {key}")
        claim_ids.add(key)
        state = item.get("status", "allegation")
        if state not in STATES:
            raise ValueError(f"unsupported claim status: {state}")
        refs = item.get("source_ids", [])
        if not isinstance(refs, list) or any(r not in ids for r in refs) or (state == "documented" and not refs):
            raise ValueError(f"claim {key} refers to a missing/nonpublic source")
        # Status is supplied by the researcher, not independently adjudicated.
        claims.append({"id": key, "statement": clean(item.get("statement"), "claim text"),
                       "status": state, "source_ids": refs})
    for item in data.get("links", []):
        if not item.get("public", False):
            continue
        left, right = item.get("from"), item.get("to")
        refs = item.get("source_ids", [])
        if left not in claim_ids or right not in claim_ids or not refs or any(r not in ids for r in refs):
            raise ValueError("Link needs two public claims and public supporting source IDs")
        links.append({"from": left, "to": right, "relationship": clean(item.get("relationship"), "relationship"),
                      "source_ids": refs})
    return {"schema_version": 1, "notice": "Research index; claims are not judicial findings. Hashes identify bytes, not truth.",
            "counts": {"sources": len(sources), "claims": len(claims), "links": len(links)},
            "sources": sources, "claims": claims, "links": links}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="public_records/intake.json")
    parser.add_argument("--output", default="public_records/records.json")
    args = parser.parse_args()
    report = build(args.input)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Public index: {report['counts']} (no scraping or automatic publication of private files)")


if __name__ == "__main__":
    main()
