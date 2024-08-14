#!/bin/bash

# Script pentru a curati baza de date

echo "Container tema2-api is stopping..."
docker stop tema2-api
docker exec -it tema2-db psql -U dev -d db -a -f /home/reset-db.sql
docker start tema2-api
