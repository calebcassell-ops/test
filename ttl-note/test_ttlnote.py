#!/usr/bin/env python3
"""Tests for ttl-note."""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

# Add parent to path so we can import the module
sys.path.insert(0, os.path.dirname(__file__))
import ttlnote


class TestSemverParsing(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(ttlnote.parse_semver("1.2.3"), (1, 2, 3))

    def test_with_v_prefix(self):
        self.assertEqual(ttlnote.parse_semver("v2.0.0"), (2, 0, 0))

    def test_partial(self):
        self.assertEqual(ttlnote.parse_semver("3.1"), (3, 1, 0))

    def test_invalid(self):
        self.assertIsNone(ttlnote.parse_semver("not-a-version"))


class TestDateCondition(unittest.TestCase):
    def test_expired_date(self):
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        expired, reason = ttlnote.evaluate_condition({"type": "date", "value": yesterday})
        self.assertTrue(expired)
        self.assertIn("expired", reason)

    def test_future_date(self):
        future = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
        expired, reason = ttlnote.evaluate_condition({"type": "date", "value": future})
        self.assertFalse(expired)
        self.assertIn("remaining", reason)

    def test_bad_date(self):
        expired, reason = ttlnote.evaluate_condition({"type": "date", "value": "not-a-date"})
        self.assertFalse(expired)
        self.assertIn("unparseable", reason)


class TestSemverCondition(unittest.TestCase):
    @patch("ttlnote.detect_project_version", return_value="2.1.0")
    def test_gte_triggered(self, _mock):
        expired, reason = ttlnote.evaluate_condition({"type": "semver", "value": ">=2.0.0"})
        self.assertTrue(expired)

    @patch("ttlnote.detect_project_version", return_value="1.9.0")
    def test_gte_not_triggered(self, _mock):
        expired, reason = ttlnote.evaluate_condition({"type": "semver", "value": ">=2.0.0"})
        self.assertFalse(expired)

    @patch("ttlnote.detect_project_version", return_value=None)
    def test_no_version_detected(self, _mock):
        expired, reason = ttlnote.evaluate_condition({"type": "semver", "value": ">=2.0.0"})
        self.assertFalse(expired)
        self.assertIn("not detected", reason)


class TestDependencyCondition(unittest.TestCase):
    @patch("ttlnote.detect_dependency_version", return_value="19.0.1")
    def test_dep_triggered(self, _mock):
        expired, reason = ttlnote.evaluate_condition(
            {"type": "dependency", "value": "react@>=19.0.0"}
        )
        self.assertTrue(expired)

    @patch("ttlnote.detect_dependency_version", return_value="18.2.0")
    def test_dep_not_triggered(self, _mock):
        expired, reason = ttlnote.evaluate_condition(
            {"type": "dependency", "value": "react@>=19.0.0"}
        )
        self.assertFalse(expired)

    @patch("ttlnote.detect_dependency_version", return_value=None)
    def test_dep_removed(self, _mock):
        expired, reason = ttlnote.evaluate_condition(
            {"type": "dependency", "value": "old-pkg@removed"}
        )
        self.assertTrue(expired)

    @patch("ttlnote.detect_dependency_version", return_value="1.0.0")
    def test_dep_not_removed(self, _mock):
        expired, reason = ttlnote.evaluate_condition(
            {"type": "dependency", "value": "old-pkg@removed"}
        )
        self.assertFalse(expired)


class TestStorageRoundTrip(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()  # so find_root can locate it
            note = ttlnote.make_note("app.py", 42, "fix this hack", "date", "2025-12-31", "debt")
            ttlnote.save_notes([note], root)
            loaded = ttlnote.load_notes(root)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["message"], "fix this hack")
            self.assertEqual(loaded[0]["tag"], "debt")
            self.assertEqual(loaded[0]["line"], 42)


class TestScanPattern(unittest.TestCase):
    def test_scan_finds_inline_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            ttlnote.save_notes([], root)

            src = root / "example.py"
            src.write_text(
                "x = 1\n"
                "# ttl-note(date=2024-01-01): Remove this workaround [#hack]\n"
                "y = hack()\n"
            )

            with patch("ttlnote.find_root", return_value=root):
                import argparse
                args = argparse.Namespace(path=str(root))
                ttlnote.cmd_scan(args)

                notes = ttlnote.load_notes(root)
                self.assertEqual(len(notes), 1)
                self.assertEqual(notes[0]["condition"]["type"], "date")
                self.assertEqual(notes[0]["condition"]["value"], "2024-01-01")
                self.assertEqual(notes[0]["tag"], "hack")
                self.assertEqual(notes[0]["line"], 2)

    def test_scan_js_comments(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            ttlnote.save_notes([], root)

            src = root / "index.js"
            src.write_text(
                "const x = 1;\n"
                "// ttl-note(semver=>=2.0.0): Remove legacy API shim\n"
            )

            with patch("ttlnote.find_root", return_value=root):
                import argparse
                args = argparse.Namespace(path=str(root))
                ttlnote.cmd_scan(args)

                notes = ttlnote.load_notes(root)
                self.assertEqual(len(notes), 1)
                self.assertEqual(notes[0]["condition"]["type"], "semver")
                self.assertIn("legacy API", notes[0]["message"])


class TestCheckExitCode(unittest.TestCase):
    def test_returns_1_on_expired(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
            note = ttlnote.make_note("f.py", 1, "old note", "date", yesterday)
            ttlnote.save_notes([note], root)

            with patch("ttlnote.find_root", return_value=root):
                import argparse
                args = argparse.Namespace(quiet=True)
                result = ttlnote.cmd_check(args)
                self.assertEqual(result, 1)

    def test_returns_0_when_clear(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".git").mkdir()
            future = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
            note = ttlnote.make_note("f.py", 1, "future note", "date", future)
            ttlnote.save_notes([note], root)

            with patch("ttlnote.find_root", return_value=root):
                import argparse
                args = argparse.Namespace(quiet=True)
                result = ttlnote.cmd_check(args)
                self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
