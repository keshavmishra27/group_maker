from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from backend.app.routers import members, groups
from fastapi.middleware.cors import CORSMiddleware # <--- IMPORT THIS

app = FastAPI()

# --- ADD THIS SECTION ---
origins = [
    "http://127.0.0.1:5500",    # VS Code Live Server default
    "http://localhost:5500",
    "http://localhost:3000",    # React default (if applicable)
    "*"                         # OR use "*" to allow ALL (easiest for development)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],        # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],        # Allows all headers
)
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
