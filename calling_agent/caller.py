"""
caller.py
---------
Initiates an outbound AI phone call via the Vapi.ai REST API.

Usage:
    python caller.py

The AI agent will:
  • Call the CUSTOMER_PHONE_NUMBER defined in .env
  • Introduce itself and have a natural conversation
  • Automatically hang up after 5 minutes (300 seconds)
  • Send a full call report (transcript + summary) to your WEBHOOK_URL
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

# ── Load environment variables ─────────────────────────────────────────────
load_dotenv()

VAPI_API_KEY          = os.getenv("VAPI_API_KEY", "").strip()
VAPI_PHONE_NUMBER_ID  = os.getenv("VAPI_PHONE_NUMBER_ID", "").strip()
CUSTOMER_PHONE_NUMBER = os.getenv("CUSTOMER_PHONE_NUMBER", "").strip()
WEBHOOK_URL           = os.getenv("WEBHOOK_URL", "").strip()
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "").strip()

VAPI_BASE_URL = "https://api.vapi.ai"

# ── Validation ─────────────────────────────────────────────────────────────
def _validate_config() -> None:
    missing = []
    for name, val in [
        ("VAPI_API_KEY",          VAPI_API_KEY),
        ("VAPI_PHONE_NUMBER_ID",  VAPI_PHONE_NUMBER_ID),
        ("CUSTOMER_PHONE_NUMBER", CUSTOMER_PHONE_NUMBER),
        ("WEBHOOK_URL",           WEBHOOK_URL),
    ]:
        if not val or val.startswith("your_"):
            missing.append(name)

    if missing:
        print("❌  Missing or placeholder values in .env:")
        for m in missing:
            print(f"    • {m}")
        print("\n👉  Copy .env.example → .env and fill in all values.")
        sys.exit(1)


# ── Assistant configuration ────────────────────────────────────────────────
def _build_assistant() -> dict:
    """
    Defines the AI agent's personality, voice, and behaviour.
    Adjust the systemPrompt to change what the agent talks about.
    """
    assistant = {
        "name": "Calling Agent",
        "firstMessage": (
            "Hello! I'm your AI assistant calling for a quick catch-up. "
            "I'm here to chat for a few minutes — how are you doing today?"
        ),
        "model": {
            "provider": "openai",
            "model": "gpt-4o-mini",    # cost-effective; change to gpt-4o for best quality
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, professional AI calling agent. "
                        "Your job is to have a warm, helpful conversation with the user. "
                        "Ask open-ended questions to understand how they are doing, "
                        "what topics they want to discuss, or if there's anything you can help with. "
                        "Keep responses concise and natural — this is a phone call, not an essay. "
                        "After about 4.5 minutes, politely wrap up the conversation and say goodbye. "
                        "End the call gracefully."
                    ),
                }
            ],
            # Inject user's OpenAI key if provided (avoids extra Vapi LLM costs)
            **({"credentialId": None} if not OPENAI_API_KEY else {}),
        },
        "voice": {
            "provider": "playht",
            "voiceId": "jennifer",      # natural-sounding female voice
        },
        "transcriber": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "en",
        },
        # Cap the call at exactly 5 minutes
        "maxDurationSeconds": 300,
        # Generate a summary automatically when the call ends
        "analysisPlan": {
            "summaryPrompt": (
                "Summarize this phone call in 3–5 sentences. "
                "Highlight the main topics discussed, any decisions made, "
                "and the overall sentiment of the conversation."
            ),
        },
        # Send the end-of-call report to the webhook server
        "serverUrl": WEBHOOK_URL,
    }

    # Use the caller's own OpenAI key if provided
    if OPENAI_API_KEY:
        assistant["model"]["openAIKey"] = OPENAI_API_KEY

    return assistant


# ── Start the call ─────────────────────────────────────────────────────────
def start_call() -> dict:
    """POST /call/phone to Vapi and return the response JSON."""
    url     = f"{VAPI_BASE_URL}/call/phone"
    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type":  "application/json",
    }
    body = {
        "phoneNumberId": VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": CUSTOMER_PHONE_NUMBER,
        },
        "assistant": _build_assistant(),
    }

    print(f"📞  Initiating call to {CUSTOMER_PHONE_NUMBER} …")
    response = requests.post(url, headers=headers, json=body, timeout=30)

    if response.status_code not in (200, 201):
        print(f"❌  Vapi API error {response.status_code}:")
        print(response.text)
        sys.exit(1)

    return response.json()


# ── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _validate_config()

    result = start_call()
    call_id = result.get("id", "unknown")

    print(f"✅  Call started successfully!")
    print(f"    Call ID  : {call_id}")
    print(f"    Status   : {result.get('status', 'N/A')}")
    print(f"    To       : {CUSTOMER_PHONE_NUMBER}")
    print(f"    Max dur. : 5 minutes (300 s)")
    print()
    print("📡  Waiting for call to end …")
    print(f"    The call report will be sent to: {WEBHOOK_URL}")
    print(f"    Make sure webhook_server.py is running in another terminal!")
    print()
    print("    (You can also check call status in the Vapi dashboard)")
