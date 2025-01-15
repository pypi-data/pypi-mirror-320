CREATE OR REPLACE FUNCTION merge_coarse_fine(coarse bigint, fine int) RETURNS varchar(1024)
AS $$ select (CONCAT(coarse::varchar(1024), ':', fine::varchar(1024)))::varchar(1024)
$$ LANGUAGE SQL;

CREATE TABLE pipeline.tm_log_new (
    id              bigserial PRIMARY KEY,
    length          int,
    category        varchar(512),
    apid            int,
    sync_flag       boolean,
    srdb_id         varchar(16),
    palisade_id     varchar(256),
    "binary"        text,
    data            jsonb,
    sha             text,
    sequence_cnt    bigint,
    cuc_time        varchar(1024),
    obt_time        timestamp,
    utc_time        timestamp,
    utc_time_is_predictive boolean,
    insert_time     timestamp not null,
    UNIQUE(sha)
);

INSERT INTO pipeline.tm_log_new(id, length, category, apid, sync_flag,
                            srdb_id, palisade_id, "binary", data, sha,
                            sequence_cnt, cuc_time,
                            obt_time, utc_time, utc_time_is_predictive,
                            insert_time)
SELECT id, length, category, apid, sync_flag,
                            srdb_id, palisade_id, "binary", data, sha,
                            sequence_cnt,
                            merge_coarse_fine(cuc_coarse_time, cuc_fine_time),
                            obt_time, utc_time, utc_time_is_predictive,
                            insert_time
        FROM pipeline.tm_log;

DROP TABLE IF EXISTS pipeline.tm_log_2020;
DROP TABLE IF EXISTS pipeline.tm_log_2021;
DROP TABLE IF EXISTS pipeline.tm_log_2022;
DROP TABLE IF EXISTS pipeline.tm_log_2023;
DROP TABLE IF EXISTS pipeline.tm_log_2024;
DROP TABLE IF EXISTS pipeline.tm_log_2025;
DROP TABLE IF EXISTS pipeline.tm_log_2026;
DROP TABLE IF EXISTS pipeline.tm_log_2027;
DROP TABLE IF EXISTS pipeline.tm_log_2028;
DROP TABLE IF EXISTS pipeline.tm_log_2029;
DROP TABLE IF EXISTS pipeline.tm_log_2030;
DROP TABLE IF EXISTS pipeline.tm_log;
ALTER TABLE IF EXISTS pipeline.tm_log_new
    RENAME TO tm_log;

