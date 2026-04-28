CREATE TABLE staff (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT UNIQUE NOT NULL,
  role       TEXT DEFAULT 'nurse' CHECK (role IN ('nurse','charge_nurse','admin')),
  created_at TIMESTAMPTZ DEFAULT now()
);
