#!/bin/sh
# Setup the Database Container
docker-compose up -d --force-recreate --build 
# Wait for the database to become ready
until docker exec clinical-database pg_isready -U postgres; do
  echo "Waiting for database to be ready..."
  sleep 2
done
docker exec -it clinical-database python3 db-import.py 
