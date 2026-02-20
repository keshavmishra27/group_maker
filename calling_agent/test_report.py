"""
test_report.py
--------------
Unit tests for report.py — verifies that save_report() correctly
creates a formatted .txt file and raw JSON file from a mock payload.

Usage:
    pip install pytest
    pytest test_report.py -v
"""

import os
import json
import glob
import shutil
import pytest

from report import save_report, REPORTS_DIR


# ── Fixtures ───────────────────────────────────────────────────────────────

MOCK_PAYLOAD = {
    "message": {
        "type": "end-of-call-report",
        "call": {
            "id": "test-call-123",
            "startedAt": "2026-02-20T10:00:00Z",
            "endedAt": "2026-02-20T10:05:00Z",
        },
        "startedAt": "2026-02-20T10:00:00Z",
        "endedAt":   "2026-02-20T10:05:00Z",
        "durationSeconds": 300,
        "endedReason": "assistant-ended-call",
        "cost": 0.85,
        "summary": (
            "The AI agent greeted the user and had a pleasant 5-minute conversation. "
            "Topics included the user's day and general well-being. "
            "The call ended amicably with the agent wrapping up politely."
        ),
        "transcript": (
            "Agent: Hello! I'm your AI assistant calling for a quick catch-up. "
            "How are you doing today?\n"
            "User: I'm doing great, thanks for calling!\n"
            "Agent: That's wonderful to hear! Is there anything you'd like to chat about?\n"
            "User: Not really, just enjoying the day.\n"
            "Agent: That sounds lovely. Well, I won't keep you too long — "
            "it was great talking with you! Have a wonderful day!\n"
            "User: You too, bye!\n"
            "Agent: Goodbye!"
        ),
    }
}


@pytest.fixture(autouse=True)
def clean_reports_dir():
    """Remove any test report files after each test."""
    yield
    # Cleanup: remove all call_report_* and call_raw_* files created by tests
    for pattern in ["call_report_*.txt", "call_raw_*.json"]:
        for f in glob.glob(os.path.join(REPORTS_DIR, pattern)):
            try:
                os.remove(f)
            except OSError:
                pass


# ── Tests ──────────────────────────────────────────────────────────────────

def test_save_report_creates_txt_file():
    """save_report() should create a .txt report file."""
    filepath = save_report(MOCK_PAYLOAD)
    assert os.path.isfile(filepath), f"Expected file at {filepath}"
    assert filepath.endswith(".txt")


def test_save_report_creates_raw_json():
    """save_report() should also create a raw JSON file alongside the report."""
    save_report(MOCK_PAYLOAD)
    json_files = glob.glob(os.path.join(REPORTS_DIR, "call_raw_*.json"))
    assert len(json_files) >= 1, "Expected at least one call_raw_*.json file"


def test_report_contains_summary():
    """The report file must contain the AI-generated summary."""
    filepath = save_report(MOCK_PAYLOAD)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    assert "The AI agent greeted" in content, "Summary not found in report"


def test_report_contains_transcript():
    """The report file must contain the full call transcript."""
    filepath = save_report(MOCK_PAYLOAD)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    assert "Hello! I'm your AI assistant" in content, "Transcript not found in report"


def test_report_contains_metadata():
    """The report file must contain call ID, duration, and end reason."""
    filepath = save_report(MOCK_PAYLOAD)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    assert "test-call-123"          in content, "Call ID not in report"
    assert "5m 0s"                  in content, "Duration not in report"
    assert "assistant-ended-call"   in content, "End reason not in report"


def test_report_contains_cost():
    """The report file must show the call cost."""
    filepath = save_report(MOCK_PAYLOAD)
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    assert "$0.8500" in content, "Cost not in report"


def test_raw_json_is_valid():
    """The raw JSON file must be parseable and match the original payload."""
    save_report(MOCK_PAYLOAD)
    json_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "call_raw_*.json")))
    with open(json_files[-1], encoding="utf-8") as f:
        data = json.load(f)
    assert data["message"]["call"]["id"] == "test-call-123"


def test_reports_dir_created_automatically():
    """save_report() must create the reports/ directory if it doesn't exist."""
    # Temporarily rename dir if it exists
    backup = REPORTS_DIR + "_backup"
    if os.path.isdir(REPORTS_DIR):
        shutil.move(REPORTS_DIR, backup)
    try:
        save_report(MOCK_PAYLOAD)
        assert os.path.isdir(REPORTS_DIR), "reports/ dir was not created"
    finally:
        if os.path.isdir(backup):
            shutil.rmtree(REPORTS_DIR, ignore_errors=True)
            shutil.move(backup, REPORTS_DIR)
