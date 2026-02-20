"""
webhook_server.py
-----------------
FastAPI server that receives the Vapi end-of-call-report webhook.

When a call ends, Vapi.ai sends a POST request to WEBHOOK_URL/webhook with
a JSON payload containing the call summary, full transcript, and metadata.
This server processes that payload and saves a human-readable report.

Usage:
    python webhook_server.py           # runs on http://0.0.0.0:8000
    uvicorn webhook_server:app --reload  # alternative (auto-reload on save)

Then expose it with ngrok:
    ngrok http 8000
"""

import logging
import os
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

from report import save_report

# ── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

load_dotenv()

# ── App ────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Calling Agent — Webhook Server",
    description=(
        "Receives Vapi.ai call lifecycle events and saves "
        "end-of-call reports (summary + transcript) to disk."
    ),
    version="1.0.0",
)


@app.get("/", tags=["Health"])
async def health_check():
    """Simple health check — visit http://localhost:8000 to confirm server is up."""
    return {
        "status": "running",
        "time": datetime.now(timezone.utc).isoformat(),
        "message": "AI Calling Agent webhook server is live ✅",
    }


@app.post("/webhook", tags=["Vapi Webhook"])
async def vapi_webhook(request: Request):
    """
    Primary webhook endpoint.
    Vapi sends all call events here (call-started, transcript, end-of-call-report, etc.)
    We only act on 'end-of-call-report'.
    """
    try:
        payload = await request.json()
    except Exception as exc:
        log.error("Failed to parse webhook payload: %s", exc)
        return Response(status_code=400)

    # Determine event type — Vapi wraps it in message.type
    msg_type = (
        payload.get("message", {}).get("type")
        or payload.get("type")
        or "unknown"
    )

    log.info("📨  Received Vapi event: type=%s", msg_type)

    if msg_type == "end-of-call-report":
        _handle_end_of_call_report(payload)
    elif msg_type == "call-started":
        call_id = (
            payload.get("message", {}).get("call", {}).get("id")
            or payload.get("call", {}).get("id", "unknown")
        )
        log.info("📞  Call started  call_id=%s", call_id)
    elif msg_type == "transcript":
        # Real-time transcript snippets — log but don't save individually
        role = payload.get("message", {}).get("role", "?")
        text = payload.get("message", {}).get("transcript", "")
        log.info("💬  [%s]: %s", role.upper(), text[:120])
    else:
        log.info("ℹ️   Unhandled event type: %s — ignoring", msg_type)

    # Vapi expects a 200 OK; anything else triggers retries
    return Response(status_code=200)


def _handle_end_of_call_report(payload: dict) -> None:
    """Process end-of-call-report and save the report file."""
    msg = payload.get("message", payload)

    call_id      = msg.get("call", {}).get("id", "unknown")
    duration_sec = msg.get("durationSeconds", None)
    ended_reason = msg.get("endedReason", "N/A")
    summary      = msg.get("summary", "")

    log.info("─" * 50)
    log.info("📋  END-OF-CALL REPORT RECEIVED")
    log.info("    Call ID   : %s", call_id)
    log.info("    Duration  : %s s", duration_sec)
    log.info("    Reason    : %s", ended_reason)

    if summary:
        log.info("    Summary   : %s …", summary[:200])

    try:
        report_path = save_report(payload)
        log.info("✅  Report saved → %s", report_path)
    except Exception as exc:
        log.error("❌  Failed to save report: %s", exc)

    log.info("─" * 50)


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    log.info("🚀  Starting webhook server on http://0.0.0.0:%d", port)
    log.info("    Webhook endpoint: POST http://0.0.0.0:%d/webhook", port)
    log.info("    Health check   : GET  http://0.0.0.0:%d/", port)
    log.info("    Reports saved to: ./reports/")
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=port, reload=False)
