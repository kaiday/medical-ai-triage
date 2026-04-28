import httpx
from app.core.config import settings

_HEADERS = {
    "apikey": settings.SUPABASE_SERVICE_KEY or "",
    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY or ''}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


def _url(path: str) -> str:
    return f"{settings.SUPABASE_URL}/rest/v1/{path}"


def is_configured() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


async def insert(table: str, data: dict) -> dict | None:
    if not is_configured():
        return None
    async with httpx.AsyncClient() as client:
        r = await client.post(_url(table), headers=_HEADERS, json=data)
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) else result


async def select(table: str, filters: dict | None = None, order: str | None = None) -> list:
    if not is_configured():
        return []
    params: dict = {}
    if filters:
        params.update(filters)
    if order:
        params["order"] = order
    async with httpx.AsyncClient() as client:
        r = await client.get(_url(table), headers=_HEADERS, params=params)
        r.raise_for_status()
        return r.json()


async def update(table: str, match: dict, data: dict) -> dict | None:
    if not is_configured():
        return None
    params = {k: f"eq.{v}" for k, v in match.items()}
    async with httpx.AsyncClient() as client:
        r = await client.patch(_url(table), headers=_HEADERS, params=params, json=data)
        r.raise_for_status()
        result = r.json()
        return result[0] if isinstance(result, list) and result else None


async def delete(table: str, match: dict) -> None:
    if not is_configured():
        return
    params = {k: f"eq.{v}" for k, v in match.items()}
    async with httpx.AsyncClient() as client:
        r = await client.delete(_url(table), headers=_HEADERS, params=params)
        r.raise_for_status()
