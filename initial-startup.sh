#!/bin/bash
# Setup the Database Container
docker-compose up -d --force-recreate --build 
# Wait for PostgreSQL to be ready
until docker exec clinical-database pg_isready -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done
docker exec -it clinical-database python3 db-import.py 
