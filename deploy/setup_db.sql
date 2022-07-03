CREATE USER user_db WITH PASSWORD '123456789';
ALTER USER user_db CREATEDB;
ALTER USER user_db SET client_encoding TO 'utf8';
ALTER USER user_db SET default_transaction_isolation TO 'read committed';
ALTER USER user_db SET timezone TO 'UTC';
CREATE DATABASE hasker OWNER :user;
