-- Optional smoke-test seed data for feature/backend-queue-api.
-- Apply after supabase/apply_backend_queue_api.sql.

INSERT INTO staff (id, email, role)
VALUES
  ('00000000-0000-0000-0000-000000000001', 'nurse@test.com', 'nurse'),
  ('00000000-0000-0000-0000-000000000002', 'charge@test.com', 'charge_nurse')
ON CONFLICT (id) DO UPDATE
SET email = EXCLUDED.email,
    role = EXCLUDED.role;

INSERT INTO patients (
  id,
  patient_ref,
  age,
  chief_complaint,
  pain_scale,
  duration,
  conditions,
  ai_level,
  ai_confidence,
  ai_reasoning,
  ai_actions,
  ai_source,
  final_level,
  status
)
VALUES
  (
    '10000000-0000-0000-0000-000000000001',
    'Patient #CRITICAL',
    67,
    'Crushing chest pain radiating to left arm',
    9,
    'Just started',
    ARRAY['Heart condition'],
    'CRITICAL',
    96,
    'High-risk chest pain symptoms require immediate review.',
    ARRAY['Bring to resus immediately', 'Prepare ECG station'],
    'openai',
    'CRITICAL',
    'waiting'
  ),
  (
    '10000000-0000-0000-0000-000000000002',
    'Patient #HIGH',
    31,
    'Suspected broken arm after fall',
    8,
    'A few hours',
    ARRAY[]::TEXT[],
    'HIGH',
    80,
    'Severe pain and possible fracture require urgent review.',
    ARRAY['Assess within 15 minutes', 'Prepare examination room'],
    'rule-based',
    'HIGH',
    'waiting'
  ),
  (
    '10000000-0000-0000-0000-000000000003',
    'Patient #MEDIUM',
    45,
    'Vomiting and dizziness',
    5,
    'A few days',
    ARRAY[]::TEXT[],
    'MEDIUM',
    60,
    'Moderate symptoms require queue monitoring.',
    ARRAY['Monitor symptoms', 'Check vital signs'],
    'rule-based',
    'MEDIUM',
    'waiting'
  ),
  (
    '10000000-0000-0000-0000-000000000004',
    'Patient #LOW',
    24,
    'Mild cold and runny nose',
    2,
    'A few days',
    ARRAY[]::TEXT[],
    'LOW',
    55,
    'Mild non-urgent symptoms.',
    ARRAY['Add to standard queue', 'Advise patient to report worsening symptoms'],
    'rule-based',
    'LOW',
    'waiting'
  ),
  (
    '10000000-0000-0000-0000-000000000005',
    'Patient #UNCLASSIFIED',
    50,
    'Unclear symptoms',
    4,
    'A few hours',
    ARRAY[]::TEXT[],
    'UNCLASSIFIED',
    0,
    'Manual nurse review required.',
    ARRAY['Review manually', 'Check vital signs'],
    'unclassified',
    'UNCLASSIFIED',
    'waiting'
  )
ON CONFLICT (id) DO UPDATE
SET patient_ref = EXCLUDED.patient_ref,
    age = EXCLUDED.age,
    chief_complaint = EXCLUDED.chief_complaint,
    pain_scale = EXCLUDED.pain_scale,
    duration = EXCLUDED.duration,
    conditions = EXCLUDED.conditions,
    ai_level = EXCLUDED.ai_level,
    ai_confidence = EXCLUDED.ai_confidence,
    ai_reasoning = EXCLUDED.ai_reasoning,
    ai_actions = EXCLUDED.ai_actions,
    ai_source = EXCLUDED.ai_source,
    final_level = EXCLUDED.final_level,
    status = EXCLUDED.status,
    confirmed_by = NULL,
    confirmed_at = NULL,
    seen_at = NULL;
