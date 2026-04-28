CREATE TABLE classification_log (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id   UUID REFERENCES patients(id) ON DELETE CASCADE,
  input_hash   TEXT,
  model        TEXT,
  raw_response JSONB,
  latency_ms   INT,
  created_at   TIMESTAMPTZ DEFAULT now()
);
