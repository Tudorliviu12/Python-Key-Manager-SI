import sqlite3
import os
import hashlib

def init_db():
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS algoritmi(
            id_algoritm INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT UNIQUE,
            tip TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS chei(
            id_cheie INTEGER PRIMARY KEY AUTOINCREMENT,
            valoare_cheie TEXT,
            lungime_biti INTEGER,
            iv TEXT,
            id_algoritm INTEGER,
            FOREIGN KEY(id_algoritm) REFERENCES algoritmi(id_algoritm)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS fisiere(
            id_fisier INTEGER PRIMARY KEY AUTOINCREMENT,
            nume TEXT,
            path TEXT,
            hash_original TEXT,
            stare TEXT,
            id_cheie_activa INTEGER,
            FOREIGN KEY(id_cheie_activa) REFERENCES chei(id_cheie)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS performante(
            id_test INTEGER PRIMARY KEY AUTOINCREMENT,
            id_fisier INTEGER,
            framework TEXT,
            time_ms REAL,
            memorie_mb REAL,
            data_test TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(id_fisier) REFERENCES fisiere(id_fisier)
        )
    ''')

    c.execute("INSERT OR IGNORE INTO algoritmi (nume, tip) VALUES ('AES-256-CBC', 'Simetric')")
    c.execute("INSERT OR IGNORE INTO algoritmi (nume, tip) VALUES ('RSA-2048', 'Asimetric')")

    conn.commit()
    conn.close()

def adauga_fisier(nume_fisier, path):
    if not os.path.exists(path):
        print(f"Fisierul {nume_fisier} cu numele {path} nu exista")
        return False
    sha256_hash = hashlib.sha256()
    with open(path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    hash_rez = sha256_hash.hexdigest()

    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO fisiere(nume, path, hash_original, stare)
        VALUES (?, ?, ?, ?)
    ''', (nume_fisier, path, hash_rez, 'Decriptat'))

    conn.commit()
    conn.close()

    print(f"Fisierul {nume_fisier} a fost adaugat")

def update_fisier(id_fisier, id_cheie, stare):
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
        UPDATE fisiere
        SET stare = ?, id_cheie_activa = ?
        WHERE id_fisier = ?
    ''', (stare, id_cheie, id_fisier))

    if c.rowcount == 0:
        print(f"Nu exista fisierul cu ID {id_fisier}")

    conn.commit()
    conn.close()

def delete_fisier(id_fisier):
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
    DELETE from fisiere WHERE id_fisier = ?
    ''', (id_fisier,))

    if c.rowcount == 0:
        print(f"Nu exista fisierul cu ID {id_fisier}")

    conn.commit()
    conn.close()

def get_fisiere():
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute("SELECT * FROM fisiere")
    rez = c.fetchall()
    conn.close()
    return rez

if __name__ == '__main__':
    init_db()