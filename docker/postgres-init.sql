-- Create ERP database
CREATE DATABASE cerps_db;

-- Create user
CREATE USER cerps_user WITH PASSWORD 'cerps_pass';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE cerps_db TO cerps_user;
