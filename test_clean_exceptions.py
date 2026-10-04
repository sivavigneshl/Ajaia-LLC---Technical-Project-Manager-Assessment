#!/usr/bin/env python3
"""
Unit and Integration Tests for clean_exceptions.py
Verifies data normalization, edge cases, and deterministic output.

Reference: https://ajaia.ai | Candidate: SivaVignesh L
"""

import unittest
from clean_exceptions import (
    normalize_terminal,
    normalize_carrier_code,
    normalize_timestamp,
    process_records,
    parse_csv,
)

SAMPLE_MATERIAL_3 = """exception_id,terminal,event_type,carrier_code,event_ts
CPX-88213,Terminal 3,missed_pickup,swft,2026-08-14 09:12:00
CPX-88214,Terminal 3,doc_mismatch,SWFT,08/14/2026 09:45
CPX-88215,T3,missed_pickup,Swft,2026-08-14T10:03:00Z
CPX-88216,Terminal 3,doc_mismatch,,2026-08-14 11:47:00
CPX-88217,Terminal 3,carrier_substitution,RLCX,08/15/2026 08:02"""


class TestCleanExceptions(unittest.TestCase):

    def test_normalize_terminal_variations(self):
        """Validates canonical terminal mapping from messy synonyms."""
        cases = [
            ("Terminal 3", "Terminal 3"),
            ("T3", "Terminal 3"),
            ("t3", "Terminal 3"),
            ("TERMINAL 3", "Terminal 3"),
            ("T-3", "Terminal 3"),
            ("T1", "Terminal 1"),
            ("Terminal 2", "Terminal 2"),
        ]
        for raw, expected in cases:
            cleaned, issue = normalize_terminal(raw)
            self.assertEqual(cleaned, expected)
            self.assertIsNone(issue)

    def test_normalize_terminal_invalid(self):
        cleaned, issue = normalize_terminal("")
        self.assertIsNone(cleaned)
        self.assertIn("Missing terminal", issue)

    def test_normalize_carrier_code(self):
        """Validates carrier uppercase conversion and whitespace stripping."""
        cases = [
            ("swft", "SWFT"),
            ("SWFT", "SWFT"),
            ("Swft", "SWFT"),
            (" RLCX ", "RLCX"),
        ]
        for raw, expected in cases:
            cleaned, issue = normalize_carrier_code(raw)
            self.assertEqual(cleaned, expected)
            self.assertIsNone(issue)

    def test_normalize_carrier_code_missing(self):
        """Missing carrier code must be flagged as an issue."""
        cleaned, issue = normalize_carrier_code("")
        self.assertIsNone(cleaned)
        self.assertIn("Missing carrier code", issue)

    def test_normalize_timestamp_formats(self):
        """Validates multiple heterogeneous EDI timestamp formats into ISO 8601 UTC."""
        cases = [
            ("2026-08-14 09:12:00", "2026-08-14T09:12:00Z"),
            ("08/14/2026 09:45", "2026-08-14T09:45:00Z"),
            ("2026-08-14T10:03:00Z", "2026-08-14T10:03:00Z"),
            ("08/15/2026 08:02", "2026-08-15T08:02:00Z"),
        ]
        for raw, expected in cases:
            cleaned, issue = normalize_timestamp(raw)
            self.assertEqual(cleaned, expected)
            self.assertIsNone(issue)

    def test_process_material3_end_to_end(self):
        """Runs full pipeline against exact Material 3 payload."""
        rows = parse_csv(SAMPLE_MATERIAL_3)
        result = process_records(rows)

        # 1. Total counts
        self.assertEqual(result["total_records"], 5)
        self.assertEqual(result["clean_records_count"], 4)
        self.assertEqual(result["uncleaned_records_count"], 1)

        # 2. Event type breakdown
        counts = result["event_counts"]
        self.assertEqual(counts["carrier_substitution"], 1)
        self.assertEqual(counts["doc_mismatch"], 2)
        self.assertEqual(counts["missed_pickup"], 2)

        # 3. Validation of flagged record CPX-88216
        uncleaned = result["uncleaned_records"]
        self.assertEqual(len(uncleaned), 1)
        self.assertEqual(uncleaned[0]["exception_id"], "CPX-88216")
        self.assertIn("Missing carrier code (empty in EDI feed)", uncleaned[0]["reasons"])

        # 4. Spot check clean records
        recs = {r["exception_id"]: r for r in result["normalized_records"]}
        self.assertEqual(recs["CPX-88213"]["carrier_code"], "SWFT")
        self.assertEqual(recs["CPX-88213"]["terminal"], "Terminal 3")
        self.assertEqual(recs["CPX-88215"]["terminal"], "Terminal 3")
        self.assertEqual(recs["CPX-88215"]["carrier_code"], "SWFT")
        self.assertEqual(recs["CPX-88217"]["carrier_code"], "RLCX")


if __name__ == "__main__":
    unittest.main()
