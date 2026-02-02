from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.routers import members, groups

app = FastAPI()

app.include_router(members.router)
app.include_router(groups.router)

# Absolute path resolution (VERY IMPORTANT)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

print("Frontend dir:", FRONTEND_DIR)  # debug once

# Mount frontend
app.mount("/ui", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

print(FRONTEND_DIR.exists())
print(list(FRONTEND_DIR.iterdir()))
