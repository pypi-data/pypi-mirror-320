
CREATE OR REPLACE FUNCTION to_new_status(status sbm_status_type) RETURNS jsonb
AS $$ select (jsonb_build_array(json_build_object(
    'status', status::sbm_status_type,
    'date', '2000-01-01 00:00:00'::TIMESTAMP)))::jsonb
$$ LANGUAGE SQL;

ALTER TABLE pipeline.sbm_log ADD COLUMN status_tmp jsonb;
UPDATE pipeline.sbm_log set status_tmp= to_new_status(status);
ALTER TABLE pipeline.sbm_log DROP COLUMN status;
ALTER TABLE pipeline.sbm_log RENAME COLUMN status_tmp TO status;
