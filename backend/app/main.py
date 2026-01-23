from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import members, groups

app = FastAPI()

app.include_router(members.router)
app.include_router(groups.router)


app.mount("/ui", StaticFiles(directory="frontend", html=True), name="frontend")
