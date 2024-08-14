# syntax=docker/dockerfile:1.4
FROM postgres

WORKDIR /db
COPY init.sql /docker-entrypoint-initdb.d/
COPY reset-db.sql /home

# sa nu se ceara parola la executia scriptului reset-db
ENV PGPASSWORD dev
