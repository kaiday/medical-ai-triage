import argparse
import json
import os
import sys
import urllib.error
import urllib.request


CONFIG_MISSING = 2
API_UNAVAILABLE = 3
BEHAVIOR_FAILURE = 4


def _as_bool(value: str | None, *, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _looks_placeholder(value: str | None) -> bool:
    if not value:
        return True
    lowered = value.strip().lower()
    return lowered in {"dummy", "change-me"} or "your-project" in lowered or "example." in lowered


def _fail(message: str, code: int) -> None:
    print(f"SMOKE_FAIL[{code}]: {message}", file=sys.stderr)
    raise SystemExit(code)


def _get_json(base_url: str, path: str) -> object:
    url = f"{base_url.rstrip('/')}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read().decode("utf-8")
            return json.loads(body) if body else None
    except urllib.error.HTTPError as exc:
        _fail(f"API returned HTTP {exc.code} for {path}", BEHAVIOR_FAILURE)
    except (urllib.error.URLError, TimeoutError) as exc:
        _fail(f"API unavailable at {url}: {exc}", API_UNAVAILABLE)
    except json.JSONDecodeError as exc:
        _fail(f"API returned invalid JSON for {path}: {exc}", BEHAVIOR_FAILURE)


def _validate_supabase_env() -> None:
    missing = [
        name
        for name in ("SUPABASE_URL", "SUPABASE_SERVICE_KEY")
        if _looks_placeholder(os.getenv(name))
    ]
    if missing:
        _fail(f"Missing real Supabase env values: {', '.join(missing)}", CONFIG_MISSING)


def main() -> None:
    parser = argparse.ArgumentParser(description="Smoke test the Dockerized backend API.")
    parser.add_argument("--base-url", default=os.getenv("SMOKE_BASE_URL", "http://localhost:8000"))
    parser.add_argument(
        "--require-supabase",
        action=argparse.BooleanOptionalAction,
        default=_as_bool(os.getenv("SMOKE_REQUIRE_SUPABASE"), default=True),
    )
    parser.add_argument(
        "--check-queue",
        action=argparse.BooleanOptionalAction,
        default=_as_bool(os.getenv("SMOKE_CHECK_QUEUE"), default=False),
    )
    args = parser.parse_args()

    if args.require_supabase:
        _validate_supabase_env()

    health = _get_json(args.base_url, "/health")
    if not isinstance(health, dict) or health.get("status") != "ok":
        _fail(f"Unexpected /health payload: {health!r}", BEHAVIOR_FAILURE)
    if args.require_supabase and health.get("supabase_configured") is not True:
        _fail("/health reports Supabase is not configured", CONFIG_MISSING)

    if args.check_queue:
        queue = _get_json(args.base_url, "/queue")
        if not isinstance(queue, list):
            _fail(f"Expected /queue to return a list, got: {queue!r}", BEHAVIOR_FAILURE)

    print("SMOKE_OK: backend Docker smoke test passed")


if __name__ == "__main__":
    main()
