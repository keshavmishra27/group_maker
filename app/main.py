from fastapi import FastAPI
from .database import engine, Base
from .routers import members, groups

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Tech Society Group Generator")

app.include_router(members.router)
app.include_router(groups.router)

@app.get("/")
def root():
    return {"status": "API running"}
