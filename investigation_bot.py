#!/usr/bin/env python3
"""
Investigation Record Bot
========================
Manages the Trust Identifier Trace investigation ledger (investigations/events.json).

Capabilities:
  - add_event()            : Append a new investigation event with UUID, timestamp, and SHA-256 hash anchor
  - validate_chain()       : Verify SHA-256 hashes of all referenced evidence files
  - query_by_identifier()  : Return all events involving a given identifier string
  - query_by_defendant()   : Return all events involving a given defendant ID
  - query_by_claim()       : Filter events by legal statute
  - generate_timeline()    : Emit sorted chronological timeline as JSON + Markdown
  - export_complaint_summary() : Generate structured complaint summary for a defendant

Usage:
  python3 investigation_bot.py --timeline
  python3 investigation_bot.py --query-identifier "SSN-602-05-7209"
  python3 investigation_bot.py --query-defendant LEXISNEXIS
  python3 investigation_bot.py --query-claim FCRA
  python3 investigation_bot.py --validate
  python3 investigation_bot.py --export-complaint LEXISNEXIS
  python3 investigation_bot.py --add-event  (interactive prompt)
"""

import argparse
import hashlib
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent
INVESTIGATIONS_DIR = REPO_ROOT / "investigations"
EVENTS_FILE = INVESTIGATIONS_DIR / "events.json"
DEFENDANTS_FILE = INVESTIGATIONS_DIR / "defendants.json"
OUTPUT_DIR = REPO_ROOT / "output"
TIMELINE_MD = OUTPUT_DIR / "investigation_timeline.md"
TIMELINE_JSON = OUTPUT_DIR / "investigation_timeline.json"


# ── Helpers ────────────────────────────────────────────────────────────────────

def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(path: Path) -> Optional[str]:
    """Return SHA-256 hex digest for a local file, or None if file not found."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _sha256_string(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _load_json(path: Path) -> Any:
    if not path.exists():
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def _load_events() -> List[Dict]:
    data = _load_json(EVENTS_FILE)
    return data if isinstance(data, list) else []


def _save_events(events: List[Dict]) -> None:
    _save_json(EVENTS_FILE, events)


def _load_defendants() -> List[Dict]:
    data = _load_json(DEFENDANTS_FILE)
    return data if isinstance(data, list) else []


def _defendant_by_id(defendant_id: str) -> Optional[Dict]:
    for d in _load_defendants():
        if d.get("defendant_id") == defendant_id:
            return d
    return None


# ── Core Functions ─────────────────────────────────────────────────────────────

def add_event(
    event_date: str,
    event_type: str,
    summary: str,
    defendant: str,
    identifiers_involved: List[str],
    legal_claims: List[Dict],
    evidence_files: List[Dict],
    notes: str = "",
    status: str = "open",
    linked_event_ids: Optional[List[str]] = None,
) -> Dict:
    """
    Append a new investigation event to events.json.
    Returns the newly created event dict.
    """
    valid_types = {
        "disclosure_received", "filing_made", "violation_observed",
        "correspondence_sent", "court_action", "surveillance_detected",
        "data_breach", "legal_threat", "remedy_action",
    }
    valid_statuses = {"open", "pending", "resolved", "escalated"}

    if event_type not in valid_types:
        raise ValueError(f"Invalid event_type '{event_type}'. Must be one of: {valid_types}")
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")

    # Hash any local evidence files for chain-of-custody
    hashed_evidence = []
    for ef in evidence_files:
        entry = dict(ef)
        path_or_url = ef.get("path_or_url", "")
        # Only hash local paths (not http/https URLs)
        if path_or_url and not path_or_url.startswith("http"):
            local_path = REPO_ROOT / path_or_url
            digest = _sha256_file(local_path)
            entry["sha256_hash"] = digest
            entry["verified_at"] = _now_utc() if digest else None
        else:
            entry.setdefault("sha256_hash", None)
            entry.setdefault("verified_at", None)
        hashed_evidence.append(entry)

    event = {
        "event_id": str(uuid.uuid4()),
        "event_date": event_date,
        "recorded_at": _now_utc(),
        "event_type": event_type,
        "identifiers_involved": identifiers_involved,
        "defendant": defendant,
        "legal_claims": legal_claims,
        "evidence_files": hashed_evidence,
        "summary": summary,
        "notes": notes,
        "status": status,
        "linked_event_ids": linked_event_ids or [],
    }

    events = _load_events()
    events.append(event)
    _save_events(events)
    print(f"✅ Event added: {event['event_id']} ({event_type} — {defendant})")
    return event


def validate_chain() -> Dict[str, Any]:
    """
    Verify SHA-256 hashes of all locally referenced evidence files in events.json.
    Returns a validation report dict.
    """
    events = _load_events()
    report = {
        "validated_at": _now_utc(),
        "total_events": len(events),
        "total_evidence_files": 0,
        "passed": [],
        "failed": [],
        "missing": [],
        "url_only": [],
    }

    for event in events:
        eid = event.get("event_id", "unknown")
        for ef in event.get("evidence_files", []):
            report["total_evidence_files"] += 1
            path_or_url = ef.get("path_or_url", "")
            label = ef.get("label", path_or_url)

            if path_or_url.startswith("http"):
                report["url_only"].append({"event_id": eid, "label": label, "url": path_or_url})
                continue

            local_path = REPO_ROOT / path_or_url
            stored_hash = ef.get("sha256_hash")
            actual_hash = _sha256_file(local_path)

            entry = {"event_id": eid, "label": label, "path": path_or_url}

            if actual_hash is None:
                entry["reason"] = "File not found"
                report["missing"].append(entry)
            elif stored_hash is None:
                # Hash not yet recorded — update it
                entry["actual_hash"] = actual_hash
                entry["reason"] = "Hash not yet recorded (needs update)"
                report["missing"].append(entry)
            elif actual_hash == stored_hash:
                entry["hash"] = actual_hash
                report["passed"].append(entry)
            else:
                entry["stored_hash"] = stored_hash
                entry["actual_hash"] = actual_hash
                entry["reason"] = "Hash mismatch — file may have been modified"
                report["failed"].append(entry)

    integrity_ok = len(report["failed"]) == 0
    report["integrity_ok"] = integrity_ok

    print(f"\n🔐 Chain-of-Custody Validation Report — {report['validated_at']}")
    print(f"   Total events:         {report['total_events']}")
    print(f"   Total evidence files: {report['total_evidence_files']}")
    print(f"   ✅ Passed:            {len(report['passed'])}")
    print(f"   ❌ Failed (tampered): {len(report['failed'])}")
    print(f"   ⚠️  Missing/unrecorded:{len(report['missing'])}")
    print(f"   🌐 URL-only (skip):   {len(report['url_only'])}")
    print(f"   {'✅ INTEGRITY OK' if integrity_ok else '❌ INTEGRITY COMPROMISED'}")

    if report["failed"]:
        print("\n❌ TAMPERING DETECTED:")
        for f in report["failed"]:
            print(f"   [{f['event_id']}] {f['label']}")
            print(f"      stored:  {f['stored_hash']}")
            print(f"      actual:  {f['actual_hash']}")

    return report


def query_by_identifier(identifier: str) -> List[Dict]:
    """Return all events that reference the given identifier string."""
    events = _load_events()
    return [e for e in events if identifier in e.get("identifiers_involved", [])]


def query_by_defendant(defendant_id: str) -> List[Dict]:
    """Return all events tied to the given defendant_id."""
    events = _load_events()
    return [e for e in events if e.get("defendant") == defendant_id]


def query_by_claim(statute: str) -> List[Dict]:
    """Return all events that include a legal claim matching the given statute (case-insensitive)."""
    statute_upper = statute.upper()
    events = _load_events()
    results = []
    for e in events:
        for claim in e.get("legal_claims", []):
            if statute_upper in claim.get("statute", "").upper():
                results.append(e)
                break
    return results


def generate_timeline() -> Dict[str, Any]:
    """
    Sort all events chronologically and write:
      output/investigation_timeline.json
      output/investigation_timeline.md
    Returns the timeline dict.
    """
    events = _load_events()
    defendants = {d["defendant_id"]: d for d in _load_defendants()}

    sorted_events = sorted(events, key=lambda e: e.get("event_date", ""))

    timeline = {
        "generated_at": _now_utc(),
        "total_events": len(sorted_events),
        "events": sorted_events,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _save_json(TIMELINE_JSON, timeline)

    # Generate Markdown report
    lines = [
        "# Trust Identifier Trace — Investigation Timeline",
        f"*Generated: {timeline['generated_at']}*",
        f"*Total events: {timeline['total_events']}*",
        "",
        "---",
        "",
    ]

    status_emoji = {
        "open": "🔵",
        "pending": "🟡",
        "resolved": "✅",
        "escalated": "🔴",
    }
    type_emoji = {
        "disclosure_received": "📋",
        "filing_made": "📄",
        "violation_observed": "⚠️",
        "correspondence_sent": "📬",
        "court_action": "⚖️",
        "surveillance_detected": "👁️",
        "data_breach": "💥",
        "legal_threat": "🚨",
        "remedy_action": "🛡️",
    }

    for evt in sorted_events:
        date = evt.get("event_date", "Unknown date")[:10]
        etype = evt.get("event_type", "unknown")
        defendant_id = evt.get("defendant", "")
        defendant_name = defendants.get(defendant_id, {}).get("full_name", defendant_id)
        st = evt.get("status", "open")
        eid = evt.get("event_id", "")

        lines.append(
            f"## {type_emoji.get(etype, '📌')} {date} — {etype.replace('_', ' ').title()}"
        )
        lines.append(f"**Status:** {status_emoji.get(st, '⚪')} {st.upper()}  ")
        lines.append(f"**Event ID:** `{eid}`  ")
        lines.append(f"**Defendant:** {defendant_name}  ")

        identifiers = evt.get("identifiers_involved", [])
        if identifiers:
            lines.append(f"**Identifiers:** {', '.join(f'`{i}`' for i in identifiers)}  ")

        claims = evt.get("legal_claims", [])
        if claims:
            claim_strs = [f"{c['statute']} §{c['section']}" for c in claims]
            lines.append(f"**Claims:** {' | '.join(claim_strs)}  ")

        lines.append("")
        lines.append(evt.get("summary", ""))

        notes = evt.get("notes", "")
        if notes:
            lines.append("")
            lines.append(f"> **Notes:** {notes}")

        evidence = evt.get("evidence_files", [])
        if evidence:
            lines.append("")
            lines.append("**Evidence:**")
            for ef in evidence:
                h = ef.get("sha256_hash")
                hash_str = f" `sha256:{h[:16]}…`" if h else ""
                lines.append(f"- [{ef['label']}]({ef['path_or_url']}){hash_str}")

        linked = evt.get("linked_event_ids", [])
        if linked:
            lines.append("")
            lines.append(f"**Linked events:** {', '.join(f'`{l}`' for l in linked)}")

        lines.append("")
        lines.append("---")
        lines.append("")

    with open(TIMELINE_MD, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Timeline written to:")
    print(f"   {TIMELINE_JSON}")
    print(f"   {TIMELINE_MD}")
    return timeline


def export_complaint_summary(defendant_id: str) -> Dict[str, Any]:
    """
    Generate a structured complaint summary for a given defendant.
    Suitable for CFPB complaint, FCRA dispute letter, or attorney packet.
    Writes to output/complaint_<defendant_id>.md and .json
    """
    defendant = _defendant_by_id(defendant_id)
    if not defendant:
        print(f"❌ Defendant '{defendant_id}' not found in defendants.json")
        sys.exit(1)

    events = query_by_defendant(defendant_id)
    events_sorted = sorted(events, key=lambda e: e.get("event_date", ""))

    all_claims = {}
    all_identifiers = set()
    for evt in events_sorted:
        for c in evt.get("legal_claims", []):
            key = f"{c['statute']} §{c['section']}"
            all_claims[key] = c.get("description", "")
        for ident in evt.get("identifiers_involved", []):
            all_identifiers.add(ident)

    summary = {
        "generated_at": _now_utc(),
        "defendant": defendant,
        "total_events": len(events_sorted),
        "identifiers_affected": sorted(all_identifiers),
        "legal_claims": [{"claim": k, "description": v} for k, v in all_claims.items()],
        "events": events_sorted,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"complaint_{defendant_id}.json"
    md_path = OUTPUT_DIR / f"complaint_{defendant_id}.md"

    _save_json(json_path, summary)

    # Build Markdown complaint packet
    lines = [
        f"# Complaint Summary: {defendant['full_name']}",
        f"*Generated: {summary['generated_at']}*",
        "",
        "## Defendant Information",
        f"- **Full Name:** {defendant['full_name']}",
        f"- **Type:** {defendant.get('type', 'N/A')}",
        f"- **Jurisdiction:** {defendant.get('jurisdiction', 'N/A')}",
        f"- **Status:** {defendant.get('status', 'N/A').upper()}",
        "",
        "## Affected Identifiers",
    ]
    for ident in sorted(all_identifiers):
        lines.append(f"- `{ident}`")

    lines += [
        "",
        "## Legal Claims",
    ]
    for claim_key, desc in all_claims.items():
        lines.append(f"- **{claim_key}**: {desc}")

    lines += [
        "",
        "## Chronological Event Log",
        "",
    ]

    for evt in events_sorted:
        date = evt.get("event_date", "")[:10]
        etype = evt.get("event_type", "").replace("_", " ").title()
        st = evt.get("status", "open").upper()
        lines.append(f"### {date} — {etype} [{st}]")
        lines.append(f"**Event ID:** `{evt.get('event_id')}`")
        lines.append("")
        lines.append(evt.get("summary", ""))
        notes = evt.get("notes", "")
        if notes:
            lines.append("")
            lines.append(f"> {notes}")
        claims = evt.get("legal_claims", [])
        if claims:
            lines.append("")
            for c in claims:
                lines.append(f"- **{c['statute']} §{c['section']}**: {c.get('description', '')}")
        evidence = evt.get("evidence_files", [])
        if evidence:
            lines.append("")
            lines.append("**Evidence:**")
            for ef in evidence:
                lines.append(f"  - [{ef['label']}]({ef['path_or_url']})")
        lines.append("")

    lines += [
        "---",
        "",
        "## Remedy Demanded",
        "",
        "1. Immediate cessation of all unauthorized data access and dissemination",
        "2. Deletion of all inaccurate or unauthorized consumer records",
        "3. Provision of complete disclosure of all data held and all entities data was shared with",
        "4. Statutory damages pursuant to applicable federal and state statutes",
        "5. Actual damages for harm caused by inaccurate or unauthorized data use",
        "6. Punitive damages for willful violations",
        "7. Attorney's fees and costs",
        "",
        "*This document was generated by the Trust Identifier Trace Investigation Bot.*",
        "*All rights reserved. Ryle Family Nation / The Travis Ryle Private Bank Estate & Trust.*",
    ]

    with open(md_path, "w") as f:
        f.write("\n".join(lines))

    print(f"✅ Complaint summary exported:")
    print(f"   {json_path}")
    print(f"   {md_path}")
    return summary


def _interactive_add_event() -> None:
    """Interactive CLI prompt for adding a new investigation event."""
    print("\n📋 ADD NEW INVESTIGATION EVENT")
    print("=" * 40)

    valid_types = [
        "disclosure_received", "filing_made", "violation_observed",
        "correspondence_sent", "court_action", "surveillance_detected",
        "data_breach", "legal_threat", "remedy_action",
    ]

    event_date = input("Event date (YYYY-MM-DD or ISO 8601): ").strip()
    if len(event_date) == 10:
        event_date += "T00:00:00Z"

    print(f"Event types: {', '.join(valid_types)}")
    event_type = input("Event type: ").strip()

    summary = input("Summary (one line): ").strip()
    notes = input("Notes (optional): ").strip()

    # Load defendants for reference
    defendants = _load_defendants()
    print("Defendant IDs: " + ", ".join(d["defendant_id"] for d in defendants))
    defendant = input("Defendant ID: ").strip()

    identifiers_raw = input("Identifiers involved (comma-separated): ").strip()
    identifiers = [i.strip() for i in identifiers_raw.split(",") if i.strip()]

    claims = []
    while True:
        statute = input("Legal claim statute (or blank to stop): ").strip()
        if not statute:
            break
        section = input("  Section: ").strip()
        description = input("  Description: ").strip()
        claims.append({"statute": statute, "section": section, "description": description})

    evidence = []
    while True:
        label = input("Evidence label (or blank to stop): ").strip()
        if not label:
            break
        path_or_url = input("  Path or URL: ").strip()
        evidence.append({"label": label, "path_or_url": path_or_url})

    valid_statuses = ["open", "pending", "resolved", "escalated"]
    print(f"Status options: {', '.join(valid_statuses)}")
    status = input("Status [open]: ").strip() or "open"

    add_event(
        event_date=event_date,
        event_type=event_type,
        summary=summary,
        defendant=defendant,
        identifiers_involved=identifiers,
        legal_claims=claims,
        evidence_files=evidence,
        notes=notes,
        status=status,
    )


def _print_events(events: List[Dict], title: str = "Results") -> None:
    print(f"\n📋 {title} ({len(events)} event(s))")
    print("=" * 50)
    for evt in sorted(events, key=lambda e: e.get("event_date", "")):
        date = evt.get("event_date", "")[:10]
        etype = evt.get("event_type", "unknown")
        defendant = evt.get("defendant", "")
        status = evt.get("status", "open").upper()
        eid = evt.get("event_id", "")[:8]
        print(f"  [{eid}…] {date} | {etype:<25} | {defendant:<25} | {status}")
        print(f"         {evt.get('summary', '')[:90]}")
        print()


# ── CLI Entry Point ────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Trust Identifier Trace — Investigation Record Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--timeline", action="store_true", help="Generate chronological timeline")
    parser.add_argument("--validate", action="store_true", help="Validate chain-of-custody hashes")
    parser.add_argument("--query-identifier", metavar="ID", help="Query events by identifier string")
    parser.add_argument("--query-defendant", metavar="DEFENDANT_ID", help="Query events by defendant ID")
    parser.add_argument("--query-claim", metavar="STATUTE", help="Query events by legal statute (e.g. FCRA)")
    parser.add_argument("--export-complaint", metavar="DEFENDANT_ID", help="Export complaint summary for defendant")
    parser.add_argument("--add-event", action="store_true", help="Add a new investigation event interactively")
    parser.add_argument("--list-defendants", action="store_true", help="List all registered defendants")
    parser.add_argument("--summary", action="store_true", help="Print summary stats of the ledger")

    args = parser.parse_args()

    if args.timeline:
        generate_timeline()

    elif args.validate:
        validate_chain()

    elif args.query_identifier:
        results = query_by_identifier(args.query_identifier)
        _print_events(results, f"Events involving '{args.query_identifier}'")

    elif args.query_defendant:
        results = query_by_defendant(args.query_defendant)
        _print_events(results, f"Events for defendant '{args.query_defendant}'")

    elif args.query_claim:
        results = query_by_claim(args.query_claim)
        _print_events(results, f"Events with '{args.query_claim}' claims")

    elif args.export_complaint:
        export_complaint_summary(args.export_complaint)

    elif args.add_event:
        _interactive_add_event()

    elif args.list_defendants:
        defendants = _load_defendants()
        print(f"\n👥 Registered Defendants ({len(defendants)})")
        print("=" * 50)
        for d in defendants:
            print(f"  {d['defendant_id']:<25} {d['full_name']}")

    elif args.summary:
        events = _load_events()
        defendants_map = {d["defendant_id"]: d["full_name"] for d in _load_defendants()}
        statuses: Dict[str, int] = {}
        types: Dict[str, int] = {}
        by_defendant: Dict[str, int] = {}
        for e in events:
            statuses[e.get("status", "unknown")] = statuses.get(e.get("status", "unknown"), 0) + 1
            types[e.get("event_type", "unknown")] = types.get(e.get("event_type", "unknown"), 0) + 1
            d = e.get("defendant", "unknown")
            by_defendant[d] = by_defendant.get(d, 0) + 1

        print(f"\n📊 Investigation Ledger Summary")
        print(f"   Total events: {len(events)}")
        print(f"\n   By status:")
        for k, v in sorted(statuses.items()):
            print(f"     {k:<12}: {v}")
        print(f"\n   By type:")
        for k, v in sorted(types.items()):
            print(f"     {k:<30}: {v}")
        print(f"\n   By defendant:")
        for k, v in sorted(by_defendant.items()):
            name = defendants_map.get(k, k)
            print(f"     {name:<40}: {v}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
