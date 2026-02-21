from fastapi import FastAPI
from backend.app.routers import members, assessment
from fastapi.middleware.cors import CORSMiddleware 

from backend.app.database import engine
from backend.app import models

# Auto-create any new tables (e.g. assessment_sessions) on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
app.include_router(assessment.router)

