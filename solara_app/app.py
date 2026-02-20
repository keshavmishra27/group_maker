"""
solara_app/app.py
-----------------
Main entry point for the Solara frontend.

Run with:
    solara run solara_app/app.py

Then open http://localhost:8765
"""

import sys, os

# Solara runs this file via exec(), so the project root may not be on sys.path.
# This line ensures `from solara_app.pages import ...` always resolves correctly.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import solara
import solara.lab
from solara_app.pages import members, calling


# ── App-wide layout with sidebar navigation ────────────────────────────────
@solara.component
def Layout(children=[]):
    with solara.AppLayout(title="Group Maker", children=children):
        pass


# ── Route definitions ──────────────────────────────────────────────────────
routes = [
    solara.Route(
        path="/",
        component=members.Page,
        label="👥 Members",
    ),
    solara.Route(
        path="calling",
        component=calling.Page,
        label="📞 Calling Agent",
    ),
]
