DROP TABLE IF EXISTS "Temperaturi";

DROP TABLE IF EXISTS "Orase";

DROP TABLE IF EXISTS "Tari";


CREATE TABLE "Tari" (
    id serial PRIMARY KEY,
    nume_tara VARCHAR(50) NOT NULL,
    latitudine double precision NOT NULL,
    longitudine double precision NOT NULL,
    UNIQUE (nume_tara));

CREATE TABLE "Orase" (
    id serial PRIMARY KEY,
    id_tara INT NOT NULL,
    nume_oras VARCHAR(50) NOT NULL,
    latitudine double precision NOT NULL,
    longitudine double precision NOT NULL,
    UNIQUE (id_tara, nume_oras),
    FOREIGN KEY (id_tara)
        REFERENCES "Tari" (id) ON DELETE CASCADE);

CREATE TABLE "Temperaturi" (
    id serial PRIMARY KEY,
    valoare double precision NOT NULL,
    timestamp timestamp NOT NULL,
    id_oras INT NOT NULL,
    UNIQUE (id_oras, timestamp),
    FOREIGN KEY (id_oras)
        REFERENCES "Orase" (id) ON DELETE CASCADE);
