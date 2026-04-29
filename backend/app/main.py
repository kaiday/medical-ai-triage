from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import triage, queue
from app.core.config import settings
from app.core.supabase import is_configured

app = FastAPI(title="Medical AI Triage API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(triage.router)
app.include_router(queue.router)


@app.get("/health", tags=["health"])
async def health():
    return {
        "status": "ok",
        "supabase_configured": is_configured(),
        "auth_enabled": settings.AUTH_ENABLED,
    }
