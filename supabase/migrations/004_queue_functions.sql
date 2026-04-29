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
