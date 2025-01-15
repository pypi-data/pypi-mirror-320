CREATE OR REPLACE FUNCTION get_coarse(cuc_time text) RETURNS bigint
AS $$ select (SPLIT_PART(cuc_time, ':', 1))::bigint
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_fine(cuc_time text) RETURNS int
AS $$ select (SPLIT_PART(cuc_time, ':', 2))::int
$$ LANGUAGE SQL;

ALTER TABLE IF EXISTS pipeline.tm_log
    RENAME TO tm_log_old;

CREATE TABLE pipeline.tm_log (
    id              bigserial not null,
    sha             text not null,
    length          int,
    category        varchar(512),
    apid            int,
    sync_flag       boolean,
    srdb_id         varchar(16),
    palisade_id     varchar(256),
    "binary"        text,
    data            jsonb,
    sequence_cnt    bigint,
    cuc_coarse_time bigint not null,
    cuc_fine_time   int,
    obt_time        timestamp,
    utc_time        timestamp,
    utc_time_is_predictive boolean,
    insert_time     timestamp not null,
    PRIMARY KEY (id, cuc_coarse_time),
    UNIQUE (sha, cuc_coarse_time)
) PARTITION BY RANGE (cuc_coarse_time);

CREATE TABLE pipeline.tm_log_2020 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (631152000) TO (662774400);
CREATE TABLE pipeline.tm_log_2021 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (662774400) TO (694310400);
CREATE TABLE pipeline.tm_log_2022 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (694310400) TO (725846400);
CREATE TABLE pipeline.tm_log_2023 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (725846400) TO (757382400);
CREATE TABLE pipeline.tm_log_2024 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (757382400) TO (789004800);
CREATE TABLE pipeline.tm_log_2025 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (789004800) TO (820540800);
CREATE TABLE pipeline.tm_log_2026 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (820540800) TO (852076800);
CREATE TABLE pipeline.tm_log_2027 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (852076800) TO (883612800);
CREATE TABLE pipeline.tm_log_2028 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (883612800) TO (915235200);
CREATE TABLE pipeline.tm_log_2029 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (915235200) TO (946771200);
CREATE TABLE pipeline.tm_log_2030 PARTITION OF pipeline.tm_log
    FOR VALUES FROM (946771200) TO (978307200);

INSERT INTO pipeline.tm_log(id, sha, length, category, apid, sync_flag,
                            srdb_id, palisade_id, "binary", data,
                            sequence_cnt, cuc_coarse_time, cuc_fine_time,
                            obt_time, utc_time, utc_time_is_predictive,
                            insert_time)
SELECT id, sha, length, category, apid, sync_flag,
                            srdb_id, palisade_id, "binary", data,
                            sequence_cnt, get_coarse(cuc_time), get_fine(cuc_time),
                            obt_time, utc_time, utc_time_is_predictive,
                            insert_time
        FROM pipeline.tm_log_old;
DROP TABLE pipeline.tm_log_old;
