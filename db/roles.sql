-- #############################################################################################
-- ###################### MUST BE EXECUTED BY SUPER USER #######################################
-- #############################################################################################

-- Admin with full control
DROP ROLE IF EXISTS app_admin;
CREATE ROLE app_admin WITH LOGIN PASSWORD 'admin_secure_pass' CREATEDB CREATEROLE;

-- Guest with read only
DROP ROLE IF EXISTS app_guest;
CREATE ROLE app_guest WITH LOGIN PASSWORD 'guest_pass';

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

-- #############################################################################################
-- #############################################################################################
-- #############################################################################################