"""
solara_app/pages/calling.py
----------------------------
Calling Agent page — start AI phone calls and view call reports.
"""

import solara
import requests
import os

API = os.getenv("API_URL", "http://localhost:8000")

# ── Reactive state ─────────────────────────────────────────────────────────
phone_input    = solara.reactive("")
prompt_input   = solara.reactive("")
duration_input = solara.reactive(300)
status_msg     = solara.reactive("")
loading_call   = solara.reactive(False)

reports        = solara.reactive([])
loading_reports= solara.reactive(False)
selected_report= solara.reactive(None)
report_content = solara.reactive("")


def start_call():
    if not phone_input.value.strip():
        status_msg.set("⚠️ Please enter a phone number.")
        return
    loading_call.set(True)
    status_msg.set("")
    try:
        body = {
            "phone_number": phone_input.value.strip(),
            "max_duration_seconds": int(duration_input.value),
        }
        if prompt_input.value.strip():
            body["system_prompt"] = prompt_input.value.strip()
        r = requests.post(f"{API}/call/start", json=body, timeout=15)
        data = r.json()
        if r.status_code == 200 and data.get("success"):
            status_msg.set(
                f"✅ Call started! ID: {data['call_id']} — "
                "Answer your phone. Report will appear below once the call ends."
            )
            phone_input.set("")
        else:
            detail = data.get("detail", r.text)
            status_msg.set(f"❌ {detail}")
    except Exception as e:
        status_msg.set(f"❌ {e}")
    finally:
        loading_call.set(False)


def fetch_reports():
    loading_reports.set(True)
    report_content.set("")
    selected_report.set(None)
    try:
        r = requests.get(f"{API}/call/reports", timeout=5)
        reports.set(r.json())
    except Exception as e:
        status_msg.set(f"❌ {e}")
    finally:
        loading_reports.set(False)


def open_report(filename: str):
    selected_report.set(filename)
    try:
        r = requests.get(f"{API}/call/reports/{filename}", timeout=5)
        report_content.set(r.text)
    except Exception as e:
        report_content.set(f"Error loading report: {e}")


def delete_report(filename: str):
    try:
        requests.delete(f"{API}/call/reports/{filename}", timeout=5)
        if selected_report.value == filename:
            selected_report.set(None)
            report_content.set("")
        fetch_reports()
    except Exception as e:
        status_msg.set(f"❌ {e}")


@solara.component
def ReportRow(rep: dict):
    name     = rep["filename"]
    created  = rep.get("created_at", "")[:19].replace("T", " ")
    size_kb  = round(rep.get("size_bytes", 0) / 1024, 1)
    is_open  = selected_report.value == name

    with solara.Card(
        style=(
            "margin-bottom:6px; cursor:pointer;"
            + ("border:2px solid #6366f1;" if is_open else "")
        )
    ):
        with solara.Row(justify="space-between"):
            with solara.Column():
                solara.Text(name, style="font-weight:600; font-size:13px;")
                solara.Text(
                    f"{created}  •  {size_kb} KB",
                    style="color:#888; font-size:12px;",
                )
            with solara.Row():
                solara.Button("📄 View", on_click=lambda: open_report(name), small=True, outlined=True)
                solara.Button("🗑️", on_click=lambda: delete_report(name), small=True, color="error")


@solara.component
def Page():
    solara.Title("AI Calling Agent")

    solara.use_effect(fetch_reports, [])

    with solara.Column(style="max-width:900px; margin:0 auto; padding:24px;"):
        solara.Markdown("# 📞 AI Calling Agent")
        solara.Markdown(
            "Start an outbound AI phone call. The agent will "
            "talk for up to the configured duration, then auto-save a summary + transcript."
        )

        # ── Start Call Form ────────────────────────────────────────────
        with solara.Card("📲 Start a Call"):
            solara.InputText(
                "📱 Phone Number (E.164 format, e.g. +919876543210)",
                value=phone_input,
            )
            solara.InputText(
                "🧠 Custom Prompt (optional — leave blank for default friendly agent)",
                value=prompt_input,
            )
            solara.SliderInt(
                "⏱️ Max Duration (seconds)",
                value=duration_input,
                min=30,
                max=600,
                step=30,
            )
            solara.Text(
                f"Call will last up to {duration_input.value // 60}m {duration_input.value % 60}s",
                style="color:#888; font-size:13px;",
            )
            solara.Button(
                "📞 Call Now",
                color="primary",
                on_click=start_call,
                disabled=loading_call.value,
            )

        if status_msg.value:
            solara.Text(status_msg.value, style="margin-top:8px;")

        # ── Reports section ────────────────────────────────────────────
        with solara.Row(justify="space-between", style="margin-top:24px;"):
            solara.Markdown(f"### 📋 Call Reports ({len(reports.value)})")
            solara.Button(
                "🔄 Refresh",
                on_click=fetch_reports,
                outlined=True,
                small=True,
                disabled=loading_reports.value,
            )

        if loading_reports.value:
            solara.Text("Loading reports…")
        elif not reports.value:
            solara.Text(
                "No reports yet. Make a call and reports will appear here automatically.",
                style="color:#888;",
            )
        else:
            for rep in reports.value:
                ReportRow(rep)

        # ── Report Viewer ─────────────────────────────────────────────
        if selected_report.value and report_content.value:
            solara.Markdown(f"### 📄 {selected_report.value}")
            with solara.Card(style="background:#1e1e2e; padding:16px; border-radius:8px;"):
                solara.Preformatted(
                    report_content.value,
                    style="color:#cdd6f4; font-size:12px; white-space:pre-wrap; font-family:monospace;",
                )
