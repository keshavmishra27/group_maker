"""
report.py
---------
Formats and saves the post-call report to a .txt file on disk.
Called automatically by webhook_server.py when Vapi sends end-of-call-report.
"""

import os
import json
from datetime import datetime, timezone


REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def save_report(payload: dict) -> str:
    """
    Parse the Vapi end-of-call-report webhook payload and
    write a formatted .txt report file.

    Returns the absolute path of the saved report file.
    """
    _ensure_reports_dir()

    msg = payload.get("message", payload)  # some payloads wrap in 'message'

    # ── Core metadata ──────────────────────────────────────────────────
    call_id        = msg.get("call", {}).get("id", "unknown")
    started_at     = msg.get("startedAt", msg.get("call", {}).get("startedAt", "N/A"))
    ended_at       = msg.get("endedAt",   msg.get("call", {}).get("endedAt",   "N/A"))
    ended_reason   = msg.get("endedReason", "N/A")
    duration_sec   = msg.get("durationSeconds", None)
    cost           = msg.get("cost", None)

    # ── Summary & transcript ───────────────────────────────────────────
    summary        = msg.get("summary", "No summary provided.")
    transcript     = msg.get("transcript", "No transcript available.")

    # ── Duration formatting ────────────────────────────────────────────
    if duration_sec is not None:
        minutes, seconds = divmod(int(duration_sec), 60)
        duration_str = f"{minutes}m {seconds}s"
    else:
        duration_str = "N/A"

    # ── Cost formatting ────────────────────────────────────────────────
    cost_str = f"${cost:.4f}" if cost is not None else "N/A"

    # ── Build report content ───────────────────────────────────────────
    now_label = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        "=" * 60,
        "           AI CALLING AGENT — CALL REPORT",
        "=" * 60,
        f"  Generated     : {now_label}",
        f"  Call ID       : {call_id}",
        f"  Started At    : {started_at}",
        f"  Ended At      : {ended_at}",
        f"  Duration      : {duration_str}",
        f"  End Reason    : {ended_reason}",
        f"  Cost          : {cost_str}",
        "",
        "─" * 60,
        "  SUMMARY",
        "─" * 60,
        "",
        summary,
        "",
        "─" * 60,
        "  FULL TRANSCRIPT",
        "─" * 60,
        "",
        transcript,
        "",
        "=" * 60,
        "  END OF REPORT",
        "=" * 60,
    ]

    report_text = "\n".join(lines)

    # ── Build filename & save ──────────────────────────────────────────
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename  = f"call_report_{timestamp}.txt"
    filepath  = os.path.join(REPORTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_text)

    # Also save the raw JSON payload alongside for debugging
    raw_filename = f"call_raw_{timestamp}.json"
    raw_filepath = os.path.join(REPORTS_DIR, raw_filename)
    with open(raw_filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return filepath
