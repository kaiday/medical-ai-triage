// Supabase client — used for Realtime subscriptions on the nurse dashboard
// Auth: anon key for patient intake, JWT for nurse routes
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY,
);
