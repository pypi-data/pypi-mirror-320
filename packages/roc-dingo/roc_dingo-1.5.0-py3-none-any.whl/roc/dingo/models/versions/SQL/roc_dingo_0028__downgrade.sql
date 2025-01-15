
CREATE OR REPLACE FUNCTION to_old_status(status jsonb) RETURNS sbm_status_type
AS $$ select (status->0->>'status')::sbm_status_type
$$ LANGUAGE SQL;

ALTER TABLE pipeline.sbm_log ADD COLUMN status_tmp sbm_status_type;
UPDATE pipeline.sbm_log set status_tmp= to_old_status(status);
ALTER TABLE pipeline.sbm_log DROP COLUMN status;
ALTER TABLE pipeline.sbm_log RENAME COLUMN status_tmp TO status;
