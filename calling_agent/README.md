# 📞 AI Calling Agent

An AI-powered outbound phone call agent that:
- **Calls any phone number** and holds a natural 5-minute conversation
- **Auto-generates a call report** (AI summary + full transcript) saved to disk the moment the call ends

Built with **[Vapi.ai](https://vapi.ai)** (voice AI + telephony) and **FastAPI** (webhook receiver).

---

## 📁 Project Structure

```
calling_agent/
├── caller.py          ← Run this to start a call
├── webhook_server.py  ← Run this to receive call reports
├── report.py          ← Formats & saves the call report
├── test_report.py     ← Unit tests
├── requirements.txt
├── .env.example       ← Copy to .env and fill in your keys
└── reports/           ← Auto-created; call reports saved here
    ├── call_report_<timestamp>.txt
    └── call_raw_<timestamp>.json
```

---

## ⚙️ One-Time Setup

### Step 1 — Sign up for Vapi.ai (free)
1. Go to [https://dashboard.vapi.ai](https://dashboard.vapi.ai) and create an account  
2. You'll get **$10 in free credits** (~6–15 test calls automatically)

### Step 2 — Get your API key
1. In the Vapi dashboard → **Account → API Keys**
2. Copy your **Private API Key**

### Step 3 — Get a phone number
1. In the Vapi dashboard → **Phone Numbers → Buy Number** (or get a free test number)
2. Copy the **Phone Number ID** (it's a UUID, not the actual number)

### Step 4 — Install ngrok (for local webhook)
Download from [https://ngrok.com/download](https://ngrok.com/download) and install.  
ngrok creates a public HTTPS URL that tunnels to your local machine so Vapi can send you the call report.

### Step 5 — Install Python dependencies

```powershell
cd calling_agent
pip install -r requirements.txt
```

### Step 6 — Configure `.env`

```powershell
copy .env.example .env
```

Open `.env` in any text editor and fill in:

```env
VAPI_API_KEY=sk-...              # Your Vapi private key
VAPI_PHONE_NUMBER_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CUSTOMER_PHONE_NUMBER=+919876543210   # Number to call (E.164 format)
WEBHOOK_URL=https://abc123.ngrok-free.app/webhook  # Fill after Step 1 below
OPENAI_API_KEY=                  # Optional — leave blank to use Vapi's default
```

---

## 🚀 Making a Call (3 terminals)

### Terminal 1 — Start the webhook server
```powershell
cd calling_agent
python webhook_server.py
```
You should see:
```
🚀  Starting webhook server on http://0.0.0.0:8000
    Webhook endpoint: POST http://0.0.0.0:8000/webhook
```

### Terminal 2 — Start ngrok
```powershell
ngrok http 8000
```
Copy the **Forwarding** URL (looks like `https://abc123.ngrok-free.app`).

Now update your `.env`:
```env
WEBHOOK_URL=https://abc123.ngrok-free.app/webhook
```

### Terminal 3 — Start the call
```powershell
cd calling_agent
python caller.py
```

**Your phone will ring in seconds!** Answer it — the AI agent will greet you and have a conversation for up to 5 minutes.

---

## 📋 Reading Your Call Report

When the call ends, check **Terminal 1** (webhook server) for a line like:
```
✅  Report saved → C:\...\calling_agent\reports\call_report_20260220_150000.txt
```

Open that file to see:
```
============================================================
           AI CALLING AGENT — CALL REPORT
============================================================
  Generated     : 2026-02-20 15:00:00 UTC
  Call ID       : abc-123
  Duration      : 4m 52s
  End Reason    : assistant-ended-call
  Cost          : $0.8500

──────────────────────────────────────────────────────────
  SUMMARY
──────────────────────────────────────────────────────────

The AI agent greeted the user and discussed their day...

──────────────────────────────────────────────────────────
  FULL TRANSCRIPT
──────────────────────────────────────────────────────────

Agent: Hello! I'm your AI assistant...
User: Hi there!
...
```

---

## 🧪 Running Tests

```powershell
cd calling_agent
pip install pytest
pytest test_report.py -v
```

---

## 🛠️ Customizing the AI Agent

Open `caller.py` and edit the `_build_assistant()` function:

| Field | What it does |
|---|---|
| `firstMessage` | The agent's opening line when the user answers |
| `model.messages[0].content` (system prompt) | Agent personality & instructions |
| `voice.voiceId` | Change voice (see [Vapi voice library](https://docs.vapi.ai/customization/voices)) |
| `model.model` | Change LLM: `gpt-4o-mini`, `gpt-4o`, `claude-3-5-sonnet`, etc. |
| `maxDurationSeconds` | Call length limit (default: `300` = 5 min) |
| `analysisPlan.summaryPrompt` | How the AI summarizes the call |

---

## 💰 Cost Estimate

| Component | Cost per minute |
|---|---|
| Vapi orchestration | $0.05 |
| Deepgram STT | ~$0.01 |
| GPT-4o-mini | ~$0.02 |
| PlayHT voice | ~$0.05 |
| Twilio telephony | ~$0.01 |
| **Total (5 min call)** | **~$0.70** |

Your **$10 free credits** will cover around **~14 test calls**.

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| `Missing or placeholder values in .env` | Make sure you filled in ALL 4 values in `.env` |
| Phone doesn't ring | Check `VAPI_PHONE_NUMBER_ID` is the UUID, not the actual phone number |
| No report received | Make sure ngrok is running AND `WEBHOOK_URL` in `.env` matches the ngrok URL **with `/webhook`** at the end |
| `402 Payment Required` from Vapi | Add a payment method at dashboard.vapi.ai → Billing |
| Report shows `No summary provided` | This can happen if the call was very short (<10s). Try a longer call |
