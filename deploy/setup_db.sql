CREATE USER :user_db WITH PASSWORD '123456789';
ALTER USER :user CREATEDB;
ALTER USER :user SET client_encoding TO 'utf8';
ALTER USER :user SET default_transaction_isolation TO 'read committed';
ALTER USER :user SET timezone TO 'UTC';
CREATE DATABASE hasker OWNER :user;
