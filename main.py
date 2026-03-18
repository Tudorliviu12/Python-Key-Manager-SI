from database import init_db
import sqlite3
from models import Algoritm

def test():
    init_db()
    conn = sqlite3.connect('local.db')
    c = conn.cursor()
    c.execute("SELECT * FROM algoritmi")
    rows = c.fetchall()
    alg = [Algoritm(r[0], r[1], r[2]) for r in rows]

    for i in alg:
        print(f"{i.id} - {i.nume} - {i.tip}")


if __name__ == '__main__':
    test()