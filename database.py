import sqlite3
import os
import hashlib
import secrets
import subprocess

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

def get_detalii_cheie(id_cheie):
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''SELECT valoare_cheie, iv FROM chei WHERE id_cheie = ?''', (id_cheie,))
    rez = c.fetchone()
    conn.close()
    return rez

def get_toate_cheile():
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
        SELECT c.id_cheie, a.nume
        FROM chei c
        JOIN algoritmi a ON c.id_algoritm = a.id_algoritm
    ''')
    rez = [f"{rand[0]} ({rand[1]})" for rand in c.fetchall()]
    conn.close()
    return rez

def generare_cheie(id_algoritm):
    if id_algoritm == 1:
        val_cheie = secrets.token_hex(32)
        iv = secrets.token_hex(16)
        lungime_biti = 256
    else:
        subprocess.run([r"C:\Program Files\Git\usr\bin\openssl.exe", "genrsa", "-out", "private.pem", "2048"], check=True)
        subprocess.run([r"C:\Program Files\Git\usr\bin\openssl.exe", "rsa", "-in", "private.pem", "-pubout", "-out", "public.pem"], check=True)
        val_cheie = "private.pem"
        iv = "public.pem"
        lungime_biti = 2048
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''
    INSERT INTO chei(valoare_cheie, lungime_biti, iv, id_algoritm)
    VALUES (?, ?, ?, ?)
    ''', (val_cheie, lungime_biti, iv, id_algoritm))

    id_cheie_noua = c.lastrowid
    conn.commit()
    conn.close()
    return id_cheie_noua, val_cheie, iv

def get_all_chei_debug():
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM chei''')
    rez = c.fetchall()
    conn.close()
    return rez

if __name__ == '__main__':
    init_db()