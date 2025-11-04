#!/bin/bash
# Build and recreate the docker containers
docker-compose up -d --force-recreate --build 

# Uncomment if the containers are built and configured and 
# the environment is to be persisted
# docker-compose up -d

# Wait for PostgreSQL to be ready
until docker exec clinical-database pg_isready -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done
docker exec -it clinical-database python3 db-import.py 
