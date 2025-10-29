#!/bin/bash
# Setup the Database Container
docker-compose up -d --force-recreate --build 
sleep 10
docker exec -it clinical-database python3 db-import.py 
