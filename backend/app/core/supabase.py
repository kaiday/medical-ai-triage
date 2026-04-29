from functools import lru_cache
from typing import Any, Dict, Optional

from app.core.config import settings


class SupabaseConfigurationError(RuntimeError):
    """Raised when Supabase service credentials are missing."""


class SupabaseRestClient:
    def __init__(self, url: str, service_key: str, timeout: float = 10.0) -> None:
        self.url = url.rstrip("/")
        self.service_key = service_key
        self.timeout = timeout

    @property
    def rest_url(self) -> str:
        return f"{self.url}/rest/v1"

    def _headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        headers = {
            "apikey": self.service_key,
            "Authorization": f"Bearer {self.service_key}",
            "Content-Type": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        import httpx

        endpoint = path if path.startswith("/") else f"/{path}"
        async with httpx.AsyncClient(base_url=self.rest_url, timeout=self.timeout) as client:
            response = await client.request(
                method,
                endpoint,
                params=params,
                json=json,
                headers=self._headers(headers),
            )
        response.raise_for_status()
        return response.json() if response.content else None


@lru_cache(maxsize=1)
def get_supabase_client() -> SupabaseRestClient:
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
        raise SupabaseConfigurationError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured to use Supabase."
        )
    return SupabaseRestClient(
        url=settings.SUPABASE_URL,
        service_key=settings.SUPABASE_SERVICE_KEY,
    )


def is_configured() -> bool:
    return bool(settings.SUPABASE_URL and settings.SUPABASE_SERVICE_KEY)


async def insert(table: str, data: dict) -> dict | None:
    if not is_configured():
        return None
    result = await get_supabase_client().request(
        "POST",
        table,
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return result[0] if isinstance(result, list) and result else result


async def select(
    table: str,
    filters: Optional[Dict[str, Any]] = None,
    order: Optional[str] = None,
) -> list:
    if not is_configured():
        return []
    params: Dict[str, Any] = {}
    if filters:
        params.update(filters)
    if order:
        params["order"] = order
    result = await get_supabase_client().request("GET", table, params=params)
    return result or []


async def update(table: str, match: dict, data: dict) -> dict | None:
    if not is_configured():
        return None
    params = {key: f"eq.{value}" for key, value in match.items()}
    result = await get_supabase_client().request(
        "PATCH",
        table,
        params=params,
        json=data,
        headers={"Prefer": "return=representation"},
    )
    return result[0] if isinstance(result, list) and result else None


async def delete(table: str, match: dict) -> None:
    if not is_configured():
        return
    params = {key: f"eq.{value}" for key, value in match.items()}
    await get_supabase_client().request("DELETE", table, params=params)
