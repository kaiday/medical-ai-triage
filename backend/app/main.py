from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import triage, queue
from app.core.config import settings

app = FastAPI(title="Medical AI Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router)
app.include_router(queue.router)
