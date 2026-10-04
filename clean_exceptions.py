#!/usr/bin/env python3
"""
Corrigan Peak Logistics - Dispatch Exception Triage (DET)
Data Normalization and Exception Ingestion Utility

Authored for Ajaia Technical Project Manager Assessment
Author: SivaVignesh L (sivavignesh.it@gmail.com)
Project: Dispatch Exception Triage (DET) for Corrigan Peak Logistics
Reference: https://ajaia.ai
"""

import csv
import io
import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Canonical Terminal Mappings
TERMINAL_SYNONYMS = {
    "T1": "Terminal 1",
    "TERMINAL 1": "Terminal 1",
    "TERMINAL1": "Terminal 1",
    "T2": "Terminal 2",
    "TERMINAL 2": "Terminal 2",
    "TERMINAL2": "Terminal 2",
    "T3": "Terminal 3",
    "TERMINAL 3": "Terminal 3",
    "TERMINAL3": "Terminal 3",
}

# Timestamp parsing formats supported across FreightWorks EDI exports
TIMESTAMP_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
]


def normalize_terminal(raw_terminal: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Normalizes messy terminal representations to canonical format (e.g. 'Terminal 3')."""
    if not raw_terminal or not raw_terminal.strip():
        return None, "Missing terminal identifier"
    
    cleaned = raw_terminal.strip()
    lookup = re.sub(r"\s+", " ", cleaned.upper())
    
    if lookup in TERMINAL_SYNONYMS:
        return TERMINAL_SYNONYMS[lookup], None
    
    # Heuristic for formats like 'T-3' or 'Term 3'
    m = re.match(r"^(?:T|TERM|TERMINAL)\s*[-_]?\s*(\d+)$", lookup)
    if m:
        return f"Terminal {m.group(1)}", None
        
    return cleaned, "Non-standard terminal identifier format"


def normalize_carrier_code(raw_carrier: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Normalizes carrier code (SCAC) to uppercase 2-4 letter alphanumeric code."""
    if not raw_carrier or not raw_carrier.strip():
        return None, "Missing carrier code (empty in EDI feed)"
    
    cleaned = raw_carrier.strip().upper()
    if not re.match(r"^[A-Z0-9]{2,5}$", cleaned):
        return cleaned, f"Invalid carrier code format: '{cleaned}'"
        
    return cleaned, None


def normalize_timestamp(raw_ts: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Parses heterogeneous timestamp formats and outputs standardized ISO 8601 UTC string."""
    if not raw_ts or not raw_ts.strip():
        return None, "Missing timestamp"
        
    cleaned = raw_ts.strip()
    
    for fmt in TIMESTAMP_FORMATS:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ"), None
        except ValueError:
            continue
            
    return None, f"Unrecognized timestamp format: '{cleaned}'"


def process_records(raw_rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Ingests raw exception records, normalizes fields, generates event counts,
    and isolates records with validation issues.
    """
    normalized_records = []
    uncleaned_records = []
    event_counts = {}

    for row in raw_rows:
        rec_id = row.get("exception_id", "").strip()
        event_type = row.get("event_type", "").strip()
        
        # Track event counts
        if event_type:
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        else:
            event_counts["unknown_event"] = event_counts.get("unknown_event", 0) + 1

        norm_term, term_issue = normalize_terminal(row.get("terminal"))
        norm_carrier, carrier_issue = normalize_carrier_code(row.get("carrier_code"))
        norm_ts, ts_issue = normalize_timestamp(row.get("event_ts"))

        record_issues = []
        if term_issue:
            record_issues.append(term_issue)
        if carrier_issue:
            record_issues.append(carrier_issue)
        if ts_issue:
            record_issues.append(ts_issue)

        is_confident = (
            norm_term is not None and
            norm_carrier is not None and
            norm_ts is not None and
            len(record_issues) == 0
        )

        cleaned_entry = {
            "exception_id": rec_id,
            "terminal": norm_term if norm_term else row.get("terminal", ""),
            "event_type": event_type,
            "carrier_code": norm_carrier if norm_carrier else "",
            "event_ts": norm_ts if norm_ts else row.get("event_ts", ""),
            "is_clean": is_confident,
            "issues": record_issues
        }

        normalized_records.append(cleaned_entry)

        if not is_confident:
            uncleaned_records.append({
                "exception_id": rec_id,
                "event_type": event_type,
                "raw_values": {
                    "terminal": row.get("terminal"),
                    "carrier_code": row.get("carrier_code"),
                    "event_ts": row.get("event_ts")
                },
                "reasons": record_issues
            })

    return {
        "total_records": len(raw_rows),
        "clean_records_count": len(raw_rows) - len(uncleaned_records),
        "uncleaned_records_count": len(uncleaned_records),
        "event_counts": event_counts,
        "normalized_records": normalized_records,
        "uncleaned_records": uncleaned_records
    }


def parse_csv(csv_content: str) -> List[Dict[str, str]]:
    """Helper to parse CSV string into list of dicts."""
    reader = csv.DictReader(io.StringIO(csv_content.strip()))
    return [row for row in reader]


def export_cleaned_csv(normalized_records: List[Dict[str, Any]], filepath: str) -> None:
    """Exports cleaned records to standard CSV file."""
    fieldnames = ["exception_id", "terminal", "event_type", "carrier_code", "event_ts", "is_clean"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in normalized_records:
            writer.writerow({
                "exception_id": r["exception_id"],
                "terminal": r["terminal"],
                "event_type": r["event_type"],
                "carrier_code": r["carrier_code"],
                "event_ts": r["event_ts"],
                "is_clean": r["is_clean"],
            })


def export_audit_json(result: Dict[str, Any], filepath: str) -> None:
    """Exports structured audit metrics and records to JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)


def main():
    input_file = "material3_input.csv"
    output_csv = "normalized_exceptions.csv"
    output_json = "audit_summary.json"

    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'", file=sys.stderr)
        sys.exit(1)

    raw_rows = parse_csv(content)
    result = process_records(raw_rows)

    # Save output artifacts
    export_cleaned_csv(result["normalized_records"], output_csv)
    export_audit_json(result, output_json)

    print("=" * 80)
    print("CORRIGAN PEAK LOGISTICS - DISPATCH EXCEPTION TRIAGE (DET)")
    print("MATERIAL 3: DATA NORMALIZATION AND EXCEPTION AUDIT REPORT")
    print(f"Reference: https://ajaia.ai | Candidate: SivaVignesh L")
    print("=" * 80)
    print()
    
    print("--- 1. SUMMARY COUNT OF EXCEPTIONS BY EVENT TYPE ---")
    for event, count in sorted(result["event_counts"].items()):
        print(f"  - {event:<25}: {count} record(s)")
    print(f"  Total Ingested Exceptions  : {result['total_records']}")
    print(f"  Clean / Validated Records  : {result['clean_records_count']}")
    print(f"  Flagged / Uncleaned Records: {result['uncleaned_records_count']}")
    print()

    print("--- 2. NORMALIZED RECORDS DATASET ---")
    header = f"{'ID':<11} | {'Terminal':<12} | {'Event Type':<22} | {'Carrier':<8} | {'Standardized Timestamp (UTC)':<24} | {'Clean?'}"
    print(header)
    print("-" * len(header))
    for r in result["normalized_records"]:
        clean_status = "PASS" if r["is_clean"] else "FLAGGED"
        print(f"{r['exception_id']:<11} | {r['terminal']:<12} | {r['event_type']:<22} | {r['carrier_code']:<8} | {r['event_ts']:<24} | {clean_status}")
    print()

    print("--- 3. UNCONFIDENT / UNCLEANED RECORDS AUDIT NOTES ---")
    if result["uncleaned_records"]:
        for item in result["uncleaned_records"]:
            print(f"  [FLAGGED] Record ID: {item['exception_id']} (Event: {item['event_type']})")
            print(f"    Raw Values     : {item['raw_values']}")
            for reason in item["reasons"]:
                print(f"    Failure Reason : {reason}")
            print(f"    Impact & Action: Cannot confidently route or score urgency. In FreightWorks EDI,")
            print(f"                     carrier_code is a mandatory foreign key to the carrier dispatch table.")
            print(f"                     Action required: Fallback lookup on FreightWorks master shipment payload.")
    else:
        print("  All records were cleaned with 100% confidence.")
    print()
    print("--- 4. ARTIFACTS EXPORTED ---")
    print(f"  [+] Clean CSV Export : {output_csv}")
    print(f"  [+] Audit JSON Export: {output_json}")
    print("=" * 80)


if __name__ == "__main__":
    main()
