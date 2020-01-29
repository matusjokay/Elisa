\set ON_ERROR_STOP 1
-- Don't let any more connections to be established at the DB
UPDATE pg_database SET datallowconn = 'false' WHERE datname = 'elisa';
-- Terminate the connection process
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'elisa';
-- Recreate DB
DROP DATABASE IF EXISTS elisa;
CREATE DATABASE elisa WITH OWNER elisa;