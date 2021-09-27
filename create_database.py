import sqlite3 as sq

with sq.connect('client_orders.db') as con:
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    text TEXT
    )
    ''')




con.close()

