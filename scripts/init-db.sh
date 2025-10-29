#!/bin/bash

echo "DEBUG: POSTGRES_DB = $POSTGRES_DB"
echo "DEBUG: POSTGRES_USER = $POSTGRES_USER"
echo "DEBUG: POSTGRES_PASSWORD = $POSTGRES_PASSWORD"
echo "DEBUG: CLINOPS_DB = $CLINOPS_DB"
echo "DEBUG: CLINOPS_USER = $CLINOPS_USER"
echo "DEBUG: CLINOPS_PASSWORD = $CLINOPS_PASSWORD"
 
psql -v ON_ERROR_STOP=1 \
    -v clinops_user="$CLINOPS_USER" \
    -v clinops_db="$CLINOPS_DB" \
    -v clinops_password="$CLINOPS_PASSWORD" \
    --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER :"clinops_user";
    GRANT ALL PRIVILEGES ON DATABASE :"clinops_db" TO :"clinops_user";
    ALTER DATABASE :"clinops_db" OWNER TO :"clinops_user";
    ALTER USER :"clinops_user" WITH PASSWORD :'clinops_password';
EOSQL
 
