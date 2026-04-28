# Queue management service
# Handles Supabase Postgres reads/writes for the patient queue
# Urgency sort order: CRITICAL(4) > HIGH(3) > MEDIUM(2) > LOW(1) > UNCLASSIFIED(0)
# Within same urgency tier: sort by submitted_at ASC (earliest first)
