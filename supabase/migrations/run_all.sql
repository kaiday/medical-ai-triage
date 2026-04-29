-- Run this entire file in the Supabase SQL Editor
-- Dashboard → SQL Editor → New query → paste → Run
-- Order: staff → patients → classification_log → RLS → indexes

-- ============================================================
-- 1. STAFF TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS staff (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT UNIQUE NOT NULL,
  role       TEXT DEFAULT 'nurse' CHECK (role IN ('nurse','charge_nurse','admin')),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- 2. PATIENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS patients (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_ref     TEXT NOT NULL,
  age             INT CHECK (age BETWEEN 0 AND 120),
  chief_complaint TEXT NOT NULL,
  pain_scale      INT CHECK (pain_scale BETWEEN 1 AND 10),
  duration        TEXT,
  conditions      TEXT[],
  submitted_at    TIMESTAMPTZ DEFAULT now(),
  ai_level        TEXT CHECK (ai_level IN ('CRITICAL','HIGH','MEDIUM','LOW','UNCLASSIFIED')),
  ai_confidence   INT CHECK (ai_confidence BETWEEN 0 AND 100),
  ai_reasoning    TEXT,
  ai_actions      TEXT[],
  ai_source       TEXT CHECK (ai_source IN ('openai','rule-based','unclassified')),
  final_level     TEXT CHECK (final_level IN ('CRITICAL','HIGH','MEDIUM','LOW','UNCLASSIFIED')),
  confirmed_by    UUID REFERENCES staff(id),
  confirmed_at    TIMESTAMPTZ,
  seen_at         TIMESTAMPTZ,
  status          TEXT DEFAULT 'waiting' CHECK (status IN ('waiting','confirmed','seen'))
);

-- ============================================================
-- 3. CLASSIFICATION AUDIT LOG
-- ============================================================
CREATE TABLE IF NOT EXISTS classification_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id   UUID REFERENCES patients(id) ON DELETE CASCADE,
  input_hash   TEXT,
  model        TEXT,
  raw_response JSONB,
  latency_ms   INT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

-- ============================================================
-- 4. INDEXES (queue sort performance)
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_patients_status     ON patients(status);
CREATE INDEX IF NOT EXISTS idx_patients_final_level ON patients(final_level);
CREATE INDEX IF NOT EXISTS idx_patients_submitted   ON patients(submitted_at);

-- ============================================================
-- 5. ROW LEVEL SECURITY
-- ============================================================
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE staff    ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_log ENABLE ROW LEVEL SECURITY;

-- Anon (patients): INSERT only
CREATE POLICY "anon_insert_patients" ON patients
  FOR INSERT TO anon WITH CHECK (true);

-- Authenticated (nurses): SELECT + UPDATE
CREATE POLICY "auth_select_patients" ON patients
  FOR SELECT TO authenticated USING (true);

CREATE POLICY "auth_update_patients" ON patients
  FOR UPDATE TO authenticated USING (true);

-- charge_nurse + admin only: DELETE
CREATE POLICY "charge_delete_patients" ON patients
  FOR DELETE TO authenticated
  USING (auth.jwt() ->> 'role' IN ('charge_nurse', 'admin'));

-- Staff: authenticated read-only (nurses see their own record)
CREATE POLICY "auth_select_staff" ON staff
  FOR SELECT TO authenticated USING (true);

-- Audit log: service role only
CREATE POLICY "service_insert_log" ON classification_log
  FOR INSERT TO service_role WITH CHECK (true);

CREATE POLICY "auth_select_log" ON classification_log
  FOR SELECT TO authenticated USING (true);

-- ============================================================
-- 6. GET_ACTIVE_QUEUE RPC FUNCTION
-- ============================================================
-- Called by GET /queue via POST /rest/v1/rpc/get_active_queue
-- Returns all non-seen patients sorted by urgency rank then submission time.
-- SECURITY DEFINER so the sort runs as the function owner, not the caller.
CREATE OR REPLACE FUNCTION get_active_queue()
RETURNS SETOF patients
LANGUAGE sql STABLE SECURITY DEFINER
AS $$
  SELECT *
  FROM patients
  WHERE status != 'seen'
  ORDER BY
    CASE final_level
      WHEN 'CRITICAL'     THEN 0
      WHEN 'HIGH'         THEN 1
      WHEN 'MEDIUM'       THEN 2
      WHEN 'LOW'          THEN 3
      WHEN 'UNCLASSIFIED' THEN 4
      ELSE 5
    END ASC,
    submitted_at ASC;
$$;

-- Allow nurses (authenticated) and the anon role to call this function
GRANT EXECUTE ON FUNCTION get_active_queue() TO authenticated;
GRANT EXECUTE ON FUNCTION get_active_queue() TO anon;

-- ============================================================
-- 7. TEST ACCOUNTS (insert into staff after auth users exist)
-- ============================================================
-- Run after creating users in Authentication → Users:
-- INSERT INTO staff (id, email, role) VALUES
--   ('<auth-user-uuid>', 'nurse@test.com', 'nurse'),
--   ('<auth-user-uuid>', 'charge@test.com', 'charge_nurse');
