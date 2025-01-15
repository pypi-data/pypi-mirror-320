
CREATE OR REPLACE FUNCTION to_not_null(input_time TIMESTAMP)
RETURNS TIMESTAMP AS $$
  SELECT COALESCE(input_time, '9999-01-01 00:00:00');
$$ LANGUAGE SQL;

ALTER TABLE pipeline.file_log ADD COLUMN start_time_tmp TIMESTAMP;
UPDATE pipeline.file_log set start_time_tmp = to_not_null(start_time);
ALTER TABLE pipeline.file_log DROP COLUMN start_time;
ALTER TABLE pipeline.file_log RENAME COLUMN start_time_tmp TO start_time;

ALTER TABLE pipeline.file_log ADD COLUMN end_time_tmp TIMESTAMP;
UPDATE pipeline.file_log set end_time_tmp = to_not_null(end_time);
ALTER TABLE pipeline.file_log DROP COLUMN end_time;
ALTER TABLE pipeline.file_log RENAME COLUMN end_time_tmp TO end_time;
