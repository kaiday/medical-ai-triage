-- Apply this file in the Supabase SQL editor for feature/backend-queue-api.
-- It is idempotent and includes the baseline tables plus queue RPC function.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS staff (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT UNIQUE NOT NULL,
  role       TEXT DEFAULT 'nurse' CHECK (role IN ('nurse','charge_nurse','admin')),
  created_at TIMESTAMPTZ DEFAULT now()
);

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

CREATE TABLE IF NOT EXISTS classification_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id   UUID REFERENCES patients(id) ON DELETE CASCADE,
  input_hash   TEXT,
  model        TEXT,
  raw_response JSONB,
  latency_ms   INT,
  created_at   TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION get_active_queue()
RETURNS SETOF patients
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
  SELECT *
  FROM patients
  WHERE status != 'seen'
  ORDER BY
    CASE final_level
      WHEN 'CRITICAL' THEN 4
      WHEN 'HIGH' THEN 3
      WHEN 'MEDIUM' THEN 2
      WHEN 'LOW' THEN 1
      WHEN 'UNCLASSIFIED' THEN 0
      ELSE 0
    END DESC,
    submitted_at ASC;
$$;
