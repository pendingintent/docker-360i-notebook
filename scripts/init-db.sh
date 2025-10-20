#!/bin/bash
 
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER clinops;
    GRANT ALL PRIVILEGES ON DATABASE clinops TO clinops;
    ALTER DATABASE clinops OWNER TO clinops;
    ALTER USER clinops WITH PASSWORD 'changeme';
EOSQL
 
