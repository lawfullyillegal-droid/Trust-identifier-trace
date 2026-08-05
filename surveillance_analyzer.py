#!/usr/bin/env python3
"""
Surveillance Pattern Analyzer
==============================
Analyzes SURVEILLANCE-* identifiers from identifiers.json to detect:
  - Temporal clustering (multiple inquiries within 30-day windows)
  - Cross-entity correlation (same date across multiple companies)
  - VIN-level tracking (vehicle surveillance linked to address/location data)
  - Insurance score manipulation patterns
  - Unauthorized soft-pull abuse

Output: output/surveillance_analysis.json
         overlays/<id>_surveillance_overlay.yml (updated with legal claims)

Usage:
  python3 surveillance_analyzer.py
  python3 surveillance_analyzer.py -v
"""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


REPO_ROOT = Path(__file__).parent
IDENTIFIERS_FILE = REPO_ROOT / "identifiers.json"
OVERLAYS_DIR = REPO_ROOT / "overlays"
OUTPUT_DIR = REPO_ROOT / "output"
ANALYSIS_FILE = OUTPUT_DIR / "surveillance_analysis.json"

# Known VINs in the identifier set
KNOWN_VINS = {"4T1B11AK1M", "4T1B1R1AKM"}

# Parse structured info from surveillance identifier strings
# Pattern: SURVEILLANCE-<TYPE>-<DETAIL>-<YYYYMMDD>
SURVEILLANCE_PATTERN = re.compile(
    r"SURVEILLANCE-(?P<type>[A-Z0-9_]+?)-(?P<detail>.+?)-(?P<date>\d{8})$"
)

# Legal claim templates per surveillance type
LEGAL_CLAIMS_BY_TYPE = {
    "CLUE": [
        {
            "statute": "FCRA",
            "section": "1681b(a)",
            "description": "C.L.U.E. report access without documented permissible purpose",
        },
        {
            "statute": "DPPA",
            "section": "2721",
            "description": "Driver's Privacy Protection Act — VIN/vehicle data access without authorization",
        },
    ],
    "RISKVIEW": [
        {
            "statute": "FCRA",
            "section": "1681b(a)",
            "description": "RiskView consumer report pull without existing account or application",
        },
        {
            "statute": "FCRA",
            "section": "1681m",
            "description": "Failure to provide adverse action notice based on consumer report",
        },
    ],
    "REVIEW": [
        {
            "statute": "FCRA",
            "section": "1681b(a)",
            "description": "Insurance review pull without active policy or documented permissible purpose",
        },
        {
            "statute": "DPPA",
            "section": "2721",
            "description": "Driver data access without proper statutory purpose",
        },
    ],
    "PREQ": [
        {
            "statute": "FCRA",
            "section": "1681b(c)",
            "description": "Pre-qualification pull — no firm offer, no opt-in, no existing relationship",
        },
        {
            "statute": "CA_CCPA",
            "section": "1798.100",
            "description": "California Consumer Privacy Act — unauthorized use of consumer data",
        },
    ],
}

# Map source entities from identifier to defendant ID
SOURCE_TO_DEFENDANT = {
    "HiRoad Insurance": "HIROAD_INSURANCE",
    "Sentry Insurance": "SENTRY_INSURANCE",
    "American Express": "AMERICAN_EXPRESS",
    "Progressive Insurance": "PROGRESSIVE_INSURANCE",
    "Credit Karma": "CREDIT_KARMA",
    "LexisNexis C.L.U.E.": "LEXISNEXIS",
}


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_identifiers() -> List[Dict]:
    with open(IDENTIFIERS_FILE, "r") as f:
        return json.load(f)


def _parse_surveillance_id(identifier: str) -> Optional[Dict]:
    """
    Parse a SURVEILLANCE-* identifier string into structured components.
    Returns None if the identifier is not a surveillance event.
    """
    m = SURVEILLANCE_PATTERN.match(identifier)
    if not m:
        return None

    date_str = m.group("date")
    try:
        event_date = datetime.strptime(date_str, "%Y%m%d").date()
    except ValueError:
        return None

    surv_type = m.group("type")
    detail = m.group("detail")

    # Detect VINs in the detail field
    vin_found = None
    for vin in KNOWN_VINS:
        if vin in detail:
            vin_found = vin
            break

    return {
        "identifier": identifier,
        "surveillance_type": surv_type,
        "detail": detail,
        "event_date": event_date.isoformat(),
        "vin": vin_found,
        "legal_claims": LEGAL_CLAIMS_BY_TYPE.get(surv_type, []),
    }


def load_surveillance_events(all_identifiers: List[Dict]) -> List[Dict]:
    """Extract and enrich all SURVEILLANCE-* identifiers."""
    events = []
    for item in all_identifiers:
        ident = item["identifier"]
        if not ident.startswith("SURVEILLANCE-"):
            continue
        parsed = _parse_surveillance_id(ident)
        if not parsed:
            continue
        parsed["source"] = item.get("source", "Unknown")
        parsed["defendant_id"] = SOURCE_TO_DEFENDANT.get(item.get("source", ""), None)
        events.append(parsed)
    return events


def detect_temporal_clusters(
    events: List[Dict], window_days: int = 30
) -> List[Dict]:
    """
    Detect groups of surveillance events within a rolling window_days window.
    Returns a list of cluster dicts.
    """
    if not events:
        return []

    sorted_events = sorted(events, key=lambda e: e["event_date"])
    clusters = []
    used = set()

    for i, anchor in enumerate(sorted_events):
        if i in used:
            continue
        anchor_date = datetime.fromisoformat(anchor["event_date"]).date()
        cluster_members = [anchor]
        for j, other in enumerate(sorted_events):
            if j == i or j in used:
                continue
            other_date = datetime.fromisoformat(other["event_date"]).date()
            delta = abs((other_date - anchor_date).days)
            if delta <= window_days:
                cluster_members.append(other)

        if len(cluster_members) >= 2:
            member_ids = {id(m) for m in cluster_members}
            used.update(id(m) for m in cluster_members)
            dates = [m["event_date"] for m in cluster_members]
            sources = [m.get("source", "Unknown") for m in cluster_members]
            clusters.append(
                {
                    "cluster_id": f"cluster_{i+1:03d}",
                    "window_days": window_days,
                    "member_count": len(cluster_members),
                    "date_range": f"{min(dates)} to {max(dates)}",
                    "sources": sources,
                    "identifiers": [m["identifier"] for m in cluster_members],
                    "same_day": len(set(dates)) == 1,
                    "risk_indicator": "HIGH — same-day multi-entity" if len(set(dates)) == 1 else "MEDIUM — temporal cluster",
                }
            )

    return clusters


def detect_cross_entity_correlations(events: List[Dict]) -> List[Dict]:
    """
    Find events from different entities occurring on the exact same date.
    """
    date_map: Dict[str, List[Dict]] = {}
    for evt in events:
        d = evt["event_date"]
        date_map.setdefault(d, []).append(evt)

    correlations = []
    for date, group in date_map.items():
        if len(group) < 2:
            continue
        sources = [e.get("source", "Unknown") for e in group]
        if len(set(sources)) >= 2:
            correlations.append(
                {
                    "date": date,
                    "entity_count": len(set(sources)),
                    "sources": sources,
                    "identifiers": [e["identifier"] for e in group],
                    "risk_indicator": "HIGH — coordinated multi-entity same-day inquiry",
                    "recommended_claim": "FCRA §1681b(a) — permissible purpose absent for all parties; investigate data-sharing agreement",
                }
            )
    return correlations


def detect_vin_tracking(events: List[Dict], all_identifiers: List[Dict]) -> List[Dict]:
    """
    Link VIN-level surveillance events to related address/location identifiers.
    """
    vin_events = [e for e in events if e.get("vin")]
    if not vin_events:
        return []

    # Collect address identifiers
    address_ids = [
        item["identifier"]
        for item in all_identifiers
        if item["identifier"].startswith("ADDR-")
    ]

    vin_links = []
    for evt in vin_events:
        vin = evt["vin"]
        vin_links.append(
            {
                "vin": vin,
                "surveillance_identifier": evt["identifier"],
                "surveillance_date": evt["event_date"],
                "source": evt.get("source", "Unknown"),
                "linked_address_identifiers": address_ids,
                "risk_indicator": "VIN tracked across insurance C.L.U.E. system; VIN-to-address correlation possible via DMV/DPPA records",
                "recommended_claims": [
                    {
                        "statute": "DPPA",
                        "section": "2721",
                        "description": "VIN used to access DMV records without permissible purpose",
                    },
                    {
                        "statute": "FCRA",
                        "section": "1681b(a)",
                        "description": "C.L.U.E. VIN-based report access without documented permissible purpose",
                    },
                ],
            }
        )
    return vin_links


def compute_risk_score(
    events: List[Dict],
    clusters: List[Dict],
    correlations: List[Dict],
    vin_links: List[Dict],
) -> Dict[str, Any]:
    """
    Compute an overall surveillance risk score (0–100) and breakdown.
    """
    score = 0
    factors = []

    # Base: number of surveillance events
    score += min(len(events) * 5, 25)
    factors.append(f"+{min(len(events)*5, 25)} pts — {len(events)} total surveillance events")

    # Same-day clusters
    same_day = sum(1 for c in clusters if c.get("same_day"))
    if same_day:
        pts = min(same_day * 15, 30)
        score += pts
        factors.append(f"+{pts} pts — {same_day} same-day multi-entity cluster(s)")

    # Cross-entity correlations
    if correlations:
        pts = min(len(correlations) * 10, 20)
        score += pts
        factors.append(f"+{pts} pts — {len(correlations)} cross-entity date correlation(s)")

    # VIN tracking
    if vin_links:
        pts = min(len(vin_links) * 10, 15)
        score += pts
        factors.append(f"+{pts} pts — {len(vin_links)} VIN tracking event(s)")

    score = min(score, 100)
    level = "LOW" if score < 30 else "MEDIUM" if score < 60 else "HIGH" if score < 85 else "CRITICAL"

    return {
        "score": score,
        "level": level,
        "factors": factors,
        "interpretation": (
            f"Score {score}/100 ({level}): "
            + (
                "Strong indicators of coordinated surveillance, data-sharing, and VIN-level tracking across multiple entities. "
                "Immediate FCRA §1681b(a) challenge letters and CFPB complaint recommended."
                if level in ("HIGH", "CRITICAL")
                else "Moderate surveillance activity detected. Monitor and document."
                if level == "MEDIUM"
                else "Low-level surveillance activity. Continue monitoring."
            )
        ),
    }


def write_surveillance_overlays(events: List[Dict]) -> None:
    """Update/create overlay YAML files for each surveillance event with legal claim annotations."""
    OVERLAYS_DIR.mkdir(exist_ok=True)
    for evt in events:
        ident = evt["identifier"]
        safe_name = re.sub(r"[^\w\-_]", "_", ident.lower())
        overlay_path = OVERLAYS_DIR / f"{safe_name}_surveillance_overlay.yml"

        claims_yaml = "\n".join(
            f"  - statute: {c['statute']}\n    section: \"{c['section']}\"\n    description: \"{c['description']}\""
            for c in evt.get("legal_claims", [])
        )

        content = f"""# Surveillance Event Overlay — {ident}
identifier: {ident}
surveillance_type: {evt.get('surveillance_type', 'UNKNOWN')}
event_date: {evt.get('event_date', 'unknown')}
source: {evt.get('source', 'unknown')}
defendant_id: {evt.get('defendant_id', 'unknown')}
vin_involved: {evt.get('vin', 'null')}
overlay_hash: {hashlib.sha256(ident.encode()).hexdigest()[:16]}
generated_at: {_now_utc()}

legal_claims:
{claims_yaml}

risk_indicators:
  - type: unauthorized_access
    basis: "No documented permissible purpose or existing account relationship found"
  - type: coordinated_inquiry
    basis: "Same-date or same-window inquiry pattern with other entities detected"

remedy_actions:
  - Send FCRA §604 dispute letter demanding permissible purpose documentation
  - File CFPB complaint citing unauthorized consumer report access
  - Preserve all related disclosures as evidence for litigation
"""
        with open(overlay_path, "w") as f:
            f.write(content)


def run_analysis(verbose: bool = False) -> Dict[str, Any]:
    """Run the full surveillance pattern analysis pipeline."""
    print("🔍 Starting Surveillance Pattern Analysis...")

    all_identifiers = _load_identifiers()

    # Step 1: Load surveillance events
    events = load_surveillance_events(all_identifiers)
    if verbose:
        print(f"  Found {len(events)} SURVEILLANCE-* identifiers")

    # Step 2: Detect temporal clusters
    clusters = detect_temporal_clusters(events)
    if verbose:
        print(f"  Detected {len(clusters)} temporal cluster(s)")

    # Step 3: Cross-entity correlations
    correlations = detect_cross_entity_correlations(events)
    if verbose:
        print(f"  Found {len(correlations)} cross-entity date correlation(s)")

    # Step 4: VIN tracking
    vin_links = detect_vin_tracking(events, all_identifiers)
    if verbose:
        print(f"  Found {len(vin_links)} VIN tracking link(s)")

    # Step 5: Risk score
    risk = compute_risk_score(events, clusters, correlations, vin_links)
    if verbose:
        print(f"  Risk score: {risk['score']}/100 ({risk['level']})")

    # Step 6: Write surveillance overlays
    write_surveillance_overlays(events)
    if verbose:
        print(f"  Written {len(events)} surveillance overlay file(s)")

    # Build full analysis report
    analysis = {
        "generated_at": _now_utc(),
        "total_surveillance_events": len(events),
        "risk_assessment": risk,
        "surveillance_timeline": sorted(events, key=lambda e: e["event_date"]),
        "temporal_clusters": clusters,
        "cross_entity_correlations": correlations,
        "vin_tracking_links": vin_links,
        "recommended_actions": [
            {
                "priority": 1,
                "action": "FCRA §1681b(a) dispute letters",
                "targets": list({e.get("source", "") for e in events}),
                "description": "Demand written documentation of permissible purpose for each surveillance event",
            },
            {
                "priority": 2,
                "action": "CFPB complaint filing",
                "targets": list({e.get("source", "") for e in events}),
                "description": "File Consumer Financial Protection Bureau complaints for unauthorized consumer report access",
            },
            {
                "priority": 3,
                "action": "DPPA demand letters",
                "targets": [e.get("source", "") for e in events if e.get("vin")],
                "description": "Driver's Privacy Protection Act demand for VIN-related surveillance events",
            },
            {
                "priority": 4,
                "action": "Insurance regulatory complaint",
                "targets": [e.get("source", "") for e in events if "Insurance" in e.get("source", "")],
                "description": "File complaint with state insurance commissioner for unauthorized C.L.U.E. access",
            },
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ANALYSIS_FILE, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n✅ Surveillance analysis complete.")
    print(f"   Risk: {risk['score']}/100 — {risk['level']}")
    print(f"   Clusters detected: {len(clusters)}")
    print(f"   Cross-entity correlations: {len(correlations)}")
    print(f"   VIN tracking links: {len(vin_links)}")
    print(f"   Output: {ANALYSIS_FILE}")

    return analysis


def main():
    parser = argparse.ArgumentParser(
        description="Trust Identifier Trace — Surveillance Pattern Analyzer",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    run_analysis(verbose=args.verbose)


if __name__ == "__main__":
    main()
