"""
Run after executing supabase/migrations/run_all.sql in the Supabase SQL Editor.
Usage: python verify_supabase.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.core.supabase import select, insert, delete, is_configured

async def main():
    if not is_configured():
        print("SKIP: SUPABASE_URL or SUPABASE_SERVICE_KEY not set in .env")
        return

    print("Verifying Supabase connection and schema...\n")
    errors = []

    for table in ["staff", "patients", "classification_log"]:
        try:
            rows = await select(table)
            print(f"  {table}: OK ({len(rows)} rows)")
        except Exception as e:
            print(f"  {table}: FAIL — {e}")
            errors.append(table)

    # Insert + delete a test patient row
    try:
        test_row = {
            "patient_ref": "Test #0",
            "chief_complaint": "connectivity test",
            "pain_scale": 1,
            "ai_level": "LOW",
            "ai_confidence": 0,
            "ai_reasoning": "test",
            "ai_actions": ["test"],
            "ai_source": "unclassified",
            "final_level": "LOW",
            "status": "seen",
        }
        inserted = await insert("patients", test_row)
        patient_id = inserted["id"]
        await delete("patients", {"id": patient_id})
        print(f"  insert+delete round-trip: OK")
    except Exception as e:
        print(f"  insert+delete round-trip: FAIL — {e}")
        errors.append("insert-delete")

    print()
    if errors:
        print(f"Failed: {errors}")
        print("Run supabase/migrations/run_all.sql in the Supabase SQL Editor first.")
    else:
        print("All checks passed — Supabase is ready.")

asyncio.run(main())
