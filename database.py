import sqlite3

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
            id_chei INTEGER PRIMARY KEY AUTOINCREMENT,
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

if __name__ == '__main__':
    init_db()