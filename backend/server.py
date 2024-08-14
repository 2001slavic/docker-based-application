from flask import Flask
from flask import Response
from flask import request
import psycopg2
import psycopg2.errorcodes
import json

server = Flask(__name__)

# Parametri de conectare la baza de date
dbParams = {
  'dbname': 'db',
  'user': 'dev',
  'password': 'dev',
  'host': 'db',
  'port': 5432
}

# conectare la baza de date

conn = psycopg2.connect(**dbParams)
cur = conn.cursor()

# Transforma raspunsul pentru tari de la db in lista de dictionare pentru json.dumps()
def countriesListToDict(list):
    res = []
    for e in list:
        res.append({
            "id"   : e[0],
            "nume" : e[1],
            "lat"  : e[2],
            "lon"  : e[3]
        })
    return res

# Transforma raspunsul pentru orase de la db in lista de dictionare pentru json.dumps()
def citiesListToDict(list):
    res = []
    for e in list:
        res.append({
            "id"     : e[0],
            "idTara" : e[1],
            "nume"   : e[2],
            "lat"    : e[3],
            "lon"    : e[4]
        })
    return res

# Transforma raspunsul pentru temperaturi de la db in lista de dictionare pentru json.dumps()
def temperaturesListToDict(list):
    res = []
    for e in list:
        res.append({
            "id": e[0],
            "valoare": e[1],
            "timestamp": e[2].strftime("%Y-%m-%d")
        })
    return res


@server.route('/api/countries', methods=['POST'])
def postCountry():
    content = request.get_json()

    try:
        cur.execute(f"""
            INSERT INTO "Tari" (nume_tara, latitudine, longitudine)
            VALUES ('{content["nume"]}', '{content["lat"]}', '{content["lon"]}');
            """)
    except psycopg2.IntegrityError:
        conn.rollback()
        return Response(status=409)
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)

    conn.commit()

    # primeste ultimul id asignat pentru raspuns
    cur.execute("""SELECT last_value FROM "Tari_id_seq";""")

    id = cur.fetchone()[0]

    return Response(json.dumps({"id" : id}), status=201)

@server.route('/api/countries', methods=['GET'])
def getCountry():
    cur.execute("""SELECT * FROM "Tari";""")

    res = cur.fetchall()

    return Response(json.dumps(countriesListToDict(res)), status=200)

@server.route('/api/countries/<int:country_id>', methods=['PUT'])
def putCountry(country_id):
    # verificare daca id-ul exista in baza de date

    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Tari" WHERE id = '{country_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    content = request.get_json()

    try:
        _ = content["id"] # verifica daca id-ul este prezent in body
        cur.execute(f"""
            UPDATE "Tari" SET nume_tara = '{content["nume"]}', latitudine = '{content["lat"]}', longitudine = '{content["lon"]}'
            WHERE id = '{country_id}';
            """)
    except psycopg2.IntegrityError:
        conn.rollback()
        return Response(status=409)
    # daca nu s-a putut extrage un camp necesar, sau are date invalide
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)
    conn.commit()
    return Response(status=200)

@server.route('/api/countries/<int:country_id>', methods=['DELETE'])
def deleteCountry(country_id):
    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Tari" WHERE id = '{country_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    cur.execute(f"""DELETE FROM "Tari" WHERE id = '{country_id}';""")
    conn.commit()
    return Response(status=200)

@server.route('/api/cities', methods=['POST'])
def postCity():
    content = request.get_json()

    try:
        cur.execute(f"""
                INSERT INTO "Orase" (id_tara, nume_oras, latitudine, longitudine)
                VALUES ('{content["idTara"]}', '{content["nume"]}', '{content["lat"]}', '{content["lon"]}');
                """)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            return Response(status=409)
        elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
            return Response(status=404)
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)

    conn.commit()

    cur.execute("""SELECT last_value FROM "Orase_id_seq";""")

    id = cur.fetchone()[0]

    return Response(json.dumps({"id": id}), status=201)

@server.route('/api/cities', methods=['GET'])
def getCities():
    cur.execute("""SELECT * FROM "Orase";""")

    res = cur.fetchall()

    return Response(json.dumps(citiesListToDict(res)), status=200)

@server.route('/api/cities/country/<int:country_id>', methods=['GET'])
def getCitiesByCountry(country_id):
    cur.execute(f"""SELECT * FROM "Orase" WHERE id_tara = '{country_id}';""")

    res = cur.fetchall()

    return Response(json.dumps(citiesListToDict(res)), status=200)

@server.route('/api/cities/<int:city_id>', methods=['PUT'])
def putCity(city_id):
    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Orase" WHERE id = '{city_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    content = request.get_json()

    try:
        # id-ul din body este verificat pentru integritate, dar ignorat dupa, prioritar fiind id-ul dat in URL
        _ = content["id"] 
        cur.execute(f"""
                UPDATE "Orase" SET id_tara = '{content["idTara"]}', nume_oras = '{content["nume"]}', latitudine = '{content["lat"]}', longitudine = '{content["lon"]}'
                WHERE id = '{city_id}';
                """)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            return Response(status=409)
        elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
            return Response(status=404)
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)
    conn.commit()
    return Response(status=200)

@server.route('/api/cities/<int:city_id>', methods=['DELETE'])
def deleteCity(city_id):
    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Orase" WHERE id = '{city_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    cur.execute(f"""DELETE FROM "Orase" WHERE id = '{city_id}';""")
    conn.commit()
    return Response(status=200)

@server.route('/api/temperatures', methods=['POST'])
def postTemperature():
    content = request.get_json()

    try:
        cur.execute(f"""
                    INSERT INTO "Temperaturi" (valoare, timestamp, id_oras)
                    VALUES ('{content["valoare"]}', NOW(), '{content["idOras"]}');
                    """)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            return Response(status=409)
        elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
            return Response(status=404)
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)

    conn.commit()

    cur.execute("""SELECT last_value FROM "Temperaturi_id_seq";""")

    id = cur.fetchone()

    return Response(json.dumps({"id": id[0]}), status=201)

@server.route('/api/temperatures', methods=['GET'])
def getTemperatures():
    query = """SELECT t.id,
                      t.valoare,
                      t.timestamp,
                      t.id_oras
                 FROM "Temperaturi" t,
                      "Orase" o
                 WHERE t.id_oras = o.id"""

    # adauga conditia de respectare a latitudinii in query, daca e disponibila

    lat = request.args.get('lat', None, float)
    if lat is not None:
        query += f" AND o.latitudine = '{lat}'"

    # adauga conditia de respectare a longitudinii in query, daca e disponibila

    lon = request.args.get('lon', None, float)
    if lon is not None:
        query += f" AND o.longitudine = '{lon}'"

    # adauga conditia de respectare a timestamp-ului from in query, daca e disponibil

    fromTimestamp = request.args.get('from', None, str)
    if fromTimestamp is not None:
        query += f" AND t.timestamp >= '{fromTimestamp} 00:00:00'"

     # adauga conditia de respectare a timestamp-ului until in query, daca e disponibil

    untilTimestamp = request.args.get('until', None, str)
    if untilTimestamp is not None:
        query += f" AND t.timestamp <= '{untilTimestamp} 00:00:00'"

    try:
        cur.execute(query)
    except:
        conn.rollback()
        return Response(status=400)

    res = cur.fetchall()

    return Response(json.dumps(temperaturesListToDict(res)), status=200)

@server.route('/api/temperatures/cities/<int:city_id>', methods=['GET'])
def getTemperaturesByCity(city_id):
    query = f'SELECT * FROM "Temperaturi" WHERE id_oras = {city_id}'

    fromTimestamp = request.args.get('from', None, str)
    if fromTimestamp is not None:
        query += f" AND timestamp >= '{fromTimestamp} 00:00:00'"

    untilTimestamp = request.args.get('until', None, str)
    if untilTimestamp is not None:
        query += f" AND timestamp <= '{untilTimestamp} 00:00:00'"

    try:
        cur.execute(query)
    except:
        conn.rollback()
        return Response(status=400)

    res = cur.fetchall()

    return Response(json.dumps(temperaturesListToDict(res)), status=200)

@server.route('/api/temperatures/countries/<int:country_id>', methods=['GET'])
def getTemperaturesByCountry(country_id):
    query = f"""SELECT t.id,
                      t.valoare,
                      t.timestamp,
                      t.id_oras
                 FROM "Temperaturi" t,
                      "Orase" o
                 WHERE t.id_oras = o.id AND
                       o.id_tara = '{country_id}'"""

    fromTimestamp = request.args.get('from', None, str)
    if fromTimestamp is not None:
        query += f" AND timestamp >= '{fromTimestamp} 00:00:00'"

    untilTimestamp = request.args.get('until', None, str)
    if untilTimestamp is not None:
        query += f" AND timestamp <= '{untilTimestamp} 00:00:00'"

    try:
        cur.execute(query)
    except:
        conn.rollback()
        return Response(status=400)

    res = cur.fetchall()

    return Response(json.dumps(temperaturesListToDict(res)), status=200)

@server.route('/api/temperatures/<int:temperature_id>', methods=['PUT'])
def putTemperature(temperature_id):
    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Temperaturi" WHERE id = '{temperature_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    content = request.get_json()

    try:
        _ = content["id"]
        cur.execute(f"""
                UPDATE "Temperaturi" SET valoare = '{content["valoare"]}', id_oras = '{content["idOras"]}'
                WHERE id = '{temperature_id}';
                """)
    except psycopg2.IntegrityError as e:
        conn.rollback()
        if e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
            return Response(status=409)
        elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
            return Response(status=404)
    except (KeyError, psycopg2.DataError):
        conn.rollback()
        return Response(status=400)
    conn.commit()
    return Response(status=200)

@server.route('/api/temperatures/<int:temperature_id>', methods=['DELETE'])
def deleteTemperature(temperature_id):
    cur.execute(f"""SELECT EXISTS(SELECT 1 FROM "Temperaturi" WHERE id = '{temperature_id}');""")
    id_exists = cur.fetchone()[0]

    if id_exists == 0:
        return Response(status=404)

    cur.execute(f"""DELETE FROM "Temperaturi" WHERE id = '{temperature_id}';""")
    conn.commit()
    return Response(status=200)
