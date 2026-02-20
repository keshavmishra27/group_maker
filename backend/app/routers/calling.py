"""
routers/calling.py
------------------
AI Calling Agent — integrated as a FastAPI router.

Endpoints (all visible in /docs):
  POST  /call/start           → initiates an outbound AI phone call
  POST  /call/webhook         → Vapi sends the end-of-call report here
  GET   /call/reports         → list all saved call reports
  GET   /call/reports/{name}  → read a specific call report
  DELETE /call/reports/{name} → delete a specific report

Setup (add to your .env):
  VAPI_API_KEY=...
  VAPI_PHONE_NUMBER_ID=...
  WEBHOOK_URL=https://<ngrok>.ngrok-free.app/call/webhook
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Optional

import requests
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

load_dotenv()

log = logging.getLogger(__name__)

router = APIRouter(prefix="/call", tags=["Calling Agent"])

# ── Config from .env ───────────────────────────────────────────────────────
VAPI_API_KEY         = os.getenv("VAPI_API_KEY", "")
VAPI_PHONE_NUMBER_ID = os.getenv("VAPI_PHONE_NUMBER_ID", "")
WEBHOOK_URL          = os.getenv("WEBHOOK_URL", "")
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY", "")
VAPI_BASE_URL        = "https://api.vapi.ai"

# Reports saved next to this file, inside backend/app/routers/call_reports/
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "call_reports")


# ── Pydantic schemas ───────────────────────────────────────────────────────

class StartCallRequest(BaseModel):
    phone_number: str = Field(
        ...,
        example="+919876543210",
        description="Phone number to call in E.164 format (e.g. +919876543210)",
    )
    agent_name: Optional[str] = Field(
        "AI Assistant",
        description="Display name of the AI agent",
    )
    system_prompt: Optional[str] = Field(
        None,
        description=(
            "Custom system prompt for the AI agent. "
            "Leave blank to use the default friendly-conversation prompt."
        ),
    )
    first_message: Optional[str] = Field(
        None,
        description="Opening line the agent speaks when the user picks up.",
    )
    max_duration_seconds: int = Field(
        300,
        ge=30,
        le=600,
        description="Max call duration in seconds (30–600). Default is 300 (5 min).",
    )


class StartCallResponse(BaseModel):
    success: bool
    call_id: str
    status: str
    to: str
    max_duration_seconds: int
    message: str


class CallReportMeta(BaseModel):
    filename: str
    created_at: str
    size_bytes: int


# ── Helpers ────────────────────────────────────────────────────────────────

def _ensure_reports_dir() -> None:
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _check_vapi_config() -> None:
    missing = [
        name for name, val in [
            ("VAPI_API_KEY",         VAPI_API_KEY),
            ("VAPI_PHONE_NUMBER_ID", VAPI_PHONE_NUMBER_ID),
            ("WEBHOOK_URL",          WEBHOOK_URL),
        ] if not val or val.startswith("your_")
    ]
    if missing:
        raise HTTPException(
            status_code=503,
            detail=(
                f"Vapi.ai not configured. Missing env vars: {', '.join(missing)}. "
                "Add them to your .env file."
            ),
        )


def _build_assistant(req: StartCallRequest) -> dict:
    default_prompt = (
        "You are a friendly, professional AI calling agent. "
        "Have a warm, helpful conversation with the user. "
        "Ask open-ended questions, listen carefully, and keep responses concise "
        "— this is a phone call, not an essay. "
        "After about 4.5 minutes, politely wrap up and say goodbye."
    )
    default_first_message = (
        f"Hello! This is {req.agent_name} calling. "
        "I'm here for a quick chat — how are you doing today?"
    )

    assistant: dict = {
        "name": req.agent_name,
        "firstMessage": req.first_message or default_first_message,
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": req.system_prompt or default_prompt,
                }
            ],
        },
        "voice": {
            "provider": "playht",
            "voiceId": "jennifer",
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en",
        },
        "maxDurationSeconds": req.max_duration_seconds,
        "analysisPlan": {
            "summaryPrompt": (
                "Summarize this phone call in 3–5 sentences. "
                "Highlight the main topics discussed, any decisions made, "
                "and the overall sentiment of the conversation."
            ),
        },
        "serverUrl": WEBHOOK_URL,
    }

    if OPENAI_API_KEY:
        assistant["model"]["openAIKey"] = OPENAI_API_KEY

    return assistant


def _save_report(payload: dict) -> str:
    """Format and save the end-of-call-report to disk. Returns the file path."""
    _ensure_reports_dir()

    msg            = payload.get("message", payload)
    call_id        = msg.get("call", {}).get("id", "unknown")
    started_at     = msg.get("startedAt",       "N/A")
    ended_at       = msg.get("endedAt",         "N/A")
    ended_reason   = msg.get("endedReason",     "N/A")
    duration_sec   = msg.get("durationSeconds", None)
    cost           = msg.get("cost",            None)
    summary        = msg.get("summary",         "No summary provided.")
    transcript     = msg.get("transcript",      "No transcript available.")

    if duration_sec is not None:
        mins, secs = divmod(int(duration_sec), 60)
        duration_str = f"{mins}m {secs}s"
    else:
        duration_str = "N/A"

    cost_str  = f"${cost:.4f}" if cost is not None else "N/A"
    now_label = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    report_text = "\n".join([
        "=" * 60,
        "        AI CALLING AGENT — CALL REPORT",
        "=" * 60,
        f"  Generated   : {now_label}",
        f"  Call ID     : {call_id}",
        f"  Started At  : {started_at}",
        f"  Ended At    : {ended_at}",
        f"  Duration    : {duration_str}",
        f"  End Reason  : {ended_reason}",
        f"  Cost        : {cost_str}",
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
    ])

    timestamp        = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_filename  = f"call_report_{timestamp}.txt"
    raw_filename     = f"call_raw_{timestamp}.json"

    with open(os.path.join(REPORTS_DIR, report_filename), "w", encoding="utf-8") as f:
        f.write(report_text)

    with open(os.path.join(REPORTS_DIR, raw_filename), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return os.path.join(REPORTS_DIR, report_filename)


# ── Routes ─────────────────────────────────────────────────────────────────

@router.post(
    "/start",
    response_model=StartCallResponse,
    summary="Start an outbound AI phone call",
    description=(
        "Initiates a Vapi.ai outbound call to the specified phone number. "
        "The AI agent will talk for up to `max_duration_seconds` (default 5 min). "
        "When the call ends, Vapi automatically sends the transcript + summary "
        "to `POST /call/webhook`, which saves a report file."
    ),
)
def start_call(req: StartCallRequest):
    _check_vapi_config()

    body = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {"number": req.phone_number},
        "assistant": _build_assistant(req),
    }
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{VAPI_BASE_URL}/call/phone",
            headers=headers,
            json=body,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Vapi.ai unreachable: {exc}")

    if resp.status_code not in (200, 201):
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"Vapi.ai error: {resp.text}",
        )

    data = resp.json()
    return StartCallResponse(
        success=True,
        call_id=data.get("id", "unknown"),
        status=data.get("status", "queued"),
        to=req.phone_number,
        max_duration_seconds=req.max_duration_seconds,
        message=(
            f"Call initiated! The AI agent will call {req.phone_number} shortly. "
            f"The call report will appear under GET /call/reports once the call ends."
        ),
    )


@router.post(
    "/webhook",
    summary="Vapi.ai webhook — receives end-of-call reports",
    description=(
        "**Do not call this manually.** "
        "Vapi.ai automatically POSTs call events here. "
        "When a call ends, the `end-of-call-report` event triggers saving "
        "a `.txt` report + raw `.json` to `backend/app/routers/call_reports/`."
    ),
    include_in_schema=True,
)
async def vapi_webhook(request: Request):
    try:
        payload = await request.json()
    except Exception:
        return Response(status_code=400)

    msg_type = (
        payload.get("message", {}).get("type")
        or payload.get("type")
        or "unknown"
    )

    log.info("Vapi webhook received: type=%s", msg_type)

    if msg_type == "end-of-call-report":
        try:
            path = _save_report(payload)
            log.info("Call report saved → %s", path)
        except Exception as exc:
            log.error("Failed to save report: %s", exc)

    # Always return 200 so Vapi doesn't retry
    return Response(status_code=200)


@router.get(
    "/reports",
    response_model=List[CallReportMeta],
    summary="List all saved call reports",
)
def list_reports():
    _ensure_reports_dir()
    files = sorted(
        [f for f in os.listdir(REPORTS_DIR) if f.endswith(".txt")],
        reverse=True,
    )
    result = []
    for filename in files:
        full_path = os.path.join(REPORTS_DIR, filename)
        stat = os.stat(full_path)
        result.append(CallReportMeta(
            filename=filename,
            created_at=datetime.fromtimestamp(
                stat.st_ctime, tz=timezone.utc
            ).isoformat(),
            size_bytes=stat.st_size,
        ))
    return result


@router.get(
    "/reports/{filename}",
    summary="Read a specific call report",
    response_class=Response,
)
def get_report(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    _ensure_reports_dir()
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Report '{filename}' not found.")
    with open(path, encoding="utf-8") as f:
        content = f.read()
    return Response(content=content, media_type="text/plain")


@router.delete(
    "/reports/{filename}",
    summary="Delete a specific call report",
)
def delete_report(filename: str):
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    _ensure_reports_dir()
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail=f"Report '{filename}' not found.")
    os.remove(path)
    # Also delete the matching raw JSON if it exists
    raw_name = filename.replace("call_report_", "call_raw_").replace(".txt", ".json")
    raw_path = os.path.join(REPORTS_DIR, raw_name)
    if os.path.isfile(raw_path):
        os.remove(raw_path)
    return {"message": f"Report '{filename}' deleted."}
