"""
Integration smoke test — Phase 6 (T-12 through T-16).

Pre-conditions:
  1. Backend running:  uvicorn app.main:app --reload
  2. .env has valid SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET
  3. T-08–T-11 complete (Realtime on, test users + staff rows exist)

Usage:
  python smoke_test.py [--base-url http://localhost:8000]

Exit code 0 = all checks passed.
Exit code 1 = one or more checks failed.
"""

import argparse
import asyncio
import json
import sys
import time

import httpx

BASE_URL = "http://localhost:8000"

INTAKE_PAYLOAD = {
    "chief_complaint": "smoke test — severe chest pain and shortness of breath",
    "pain_scale": 9,
    "age": 55,
    "duration": "30 minutes",
    "conditions": ["hypertension", "diabetes"],
}

OK = "\033[92m OK\033[0m"
FAIL = "\033[91m FAIL\033[0m"


def _result(label: str, passed: bool, detail: str = "") -> bool:
    status = OK if passed else FAIL
    suffix = f" — {detail}" if detail else ""
    print(f"  {label}:{status}{suffix}")
    return passed


# ---------------------------------------------------------------------------
# T-13: POST /triage → patient classified + returned
# ---------------------------------------------------------------------------

async def check_triage(client: httpx.AsyncClient) -> str | None:
    """Returns patient id if triage succeeded, None on failure."""
    print("\nT-13  POST /triage")
    try:
        t0 = time.perf_counter()
        resp = await client.post("/triage", json=INTAKE_PAYLOAD)
        ms = int((time.perf_counter() - t0) * 1000)

        passed = _result("status 200", resp.status_code == 200, f"got {resp.status_code}")
        if not passed:
            print(f"        body: {resp.text[:300]}")
            return None

        body = resp.json()
        _result("has id", "id" in body)
        _result("has urgency", "triage" in body and "urgency" in body["triage"])
        _result(f"latency {ms}ms < 10000ms", ms < 10000)

        urgency = body.get("triage", {}).get("urgency", "?")
        source = body.get("triage", {}).get("source", "?")
        print(f"        urgency={urgency}  source={source}  id={body.get('id','')[:8]}...")
        return body.get("id")

    except Exception as exc:
        _result("POST /triage", False, str(exc))
        return None


# ---------------------------------------------------------------------------
# T-14: GET /queue → patient appears, sorted correctly
# ---------------------------------------------------------------------------

async def check_queue(client: httpx.AsyncClient, expected_id: str | None) -> bool:
    print("\nT-14  GET /queue")
    try:
        resp = await client.get("/queue")
        passed = _result("status 200", resp.status_code == 200, f"got {resp.status_code}")
        if not passed:
            print(f"        body: {resp.text[:300]}")
            return False

        body = resp.json()
        patients = body if isinstance(body, list) else body.get("patients", [])
        all_ok = True
        all_ok &= _result("returns list", isinstance(patients, list))
        all_ok &= _result("non-empty", len(patients) > 0, f"{len(patients)} patients")

        if expected_id:
            ids = [p.get("id") for p in patients]
            in_queue = expected_id in ids
            all_ok &= _result("smoke patient in queue", in_queue)
            if not in_queue:
                print(f"        expected id: {expected_id}")
                print(f"        returned ids: {ids[:10]}")

        # Verify sort order: no CRITICAL after HIGH, no HIGH after MEDIUM, etc.
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNCLASSIFIED": 4}
        levels = [
            order.get(p.get("final_level") or p.get("finalLevel", "UNCLASSIFIED"), 5)
            for p in patients
        ]
        sorted_ok = levels == sorted(levels)
        all_ok &= _result("queue sorted by urgency", sorted_ok)

        return all_ok

    except Exception as exc:
        _result("GET /queue", False, str(exc))
        return False


# ---------------------------------------------------------------------------
# T-15: verify_supabase.py connectivity (run inline)
# ---------------------------------------------------------------------------

async def check_supabase_connectivity() -> bool:
    print("\nT-15  Supabase connectivity (via verify_supabase logic)")
    try:
        import os, sys
        sys.path.insert(0, ".")
        from app.core.supabase import select, is_configured

        if not is_configured():
            _result("configured", False, "SUPABASE_URL or SUPABASE_SERVICE_KEY missing")
            return False

        _result("configured", True)
        all_ok = True
        for table in ["staff", "patients", "classification_log"]:
            try:
                rows = await select(table)
                _result(f"{table} readable", True, f"{len(rows)} rows")
            except Exception as exc:
                _result(f"{table} readable", False, str(exc))
                all_ok = False
        return all_ok

    except Exception as exc:
        _result("connectivity", False, str(exc))
        return False


# ---------------------------------------------------------------------------
# T-16: GET /queue with nurse JWT (AUTH_ENABLED=true)
# ---------------------------------------------------------------------------

async def check_auth_queue(client: httpx.AsyncClient) -> bool:
    print("\nT-16  GET /queue with nurse JWT")
    try:
        import os
        from app.core.config import settings

        if not settings.AUTH_ENABLED:
            print("       AUTH_ENABLED=false — skipping (set to true to test)")
            return True

        if not settings.SUPABASE_JWT_SECRET:
            _result("jwt secret set", False, "SUPABASE_JWT_SECRET missing in .env")
            return False

        # Generate a minimal nurse JWT signed with the project secret
        import base64, hmac, hashlib, json as _json

        def _b64(data: bytes) -> str:
            return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

        header = _b64(_json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
        payload_data = {
            "sub": "00000000-0000-0000-0000-000000000001",
            "email": "nurse@test.com",
            "app_metadata": {"role": "nurse"},
            "role": "authenticated",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
        }
        payload_b64 = _b64(_json.dumps(payload_data).encode())
        signing_input = f"{header}.{payload_b64}".encode()
        sig = hmac.new(
            settings.SUPABASE_JWT_SECRET.encode(),
            signing_input,
            hashlib.sha256,
        ).digest()
        token = f"{header}.{payload_b64}.{_b64(sig)}"

        resp = await client.get(
            "/queue",
            headers={"Authorization": f"Bearer {token}"},
        )
        passed = _result("GET /queue with nurse JWT → 200", resp.status_code == 200,
                         f"got {resp.status_code}")
        return passed

    except Exception as exc:
        _result("auth queue", False, str(exc))
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main(base_url: str) -> int:
    print(f"Smoke test against {base_url}")
    print("=" * 50)

    failures = 0

    async with httpx.AsyncClient(base_url=base_url, timeout=15.0, follow_redirects=True) as client:
        # Health check first
        print("\nHealth check")
        try:
            resp = await client.get("/health")
            if not _result("GET /health", resp.status_code == 200, f"got {resp.status_code}"):
                failures += 1
        except Exception as exc:
            _result("GET /health", False, str(exc))
            print("\nBackend not reachable. Start it with:")
            print("  uvicorn app.main:app --reload")
            return 1

        patient_id = await check_triage(client)
        if patient_id is None:
            failures += 1

        # Brief pause for Supabase Realtime / write propagation
        await asyncio.sleep(1)

        if not await check_queue(client, patient_id):
            failures += 1

    if not await check_supabase_connectivity():
        failures += 1

    # T-16 needs a fresh client (may have different auth settings)
    async with httpx.AsyncClient(base_url=base_url, timeout=15.0, follow_redirects=True) as client:
        if not await check_auth_queue(client):
            failures += 1

    print("\n" + "=" * 50)
    if failures:
        print(f"\033[91m{failures} check(s) FAILED\033[0m")
        return 1
    else:
        print("\033[92mAll checks passed.\033[0m")
        return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    args = parser.parse_args()

    sys.exit(asyncio.run(main(args.base_url)))
