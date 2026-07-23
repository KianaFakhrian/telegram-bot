import sqlite3

DB_NAME = "messages.db"

import os

print("Database location:", os.path.abspath(DB_NAME))

def connect():
    return sqlite3.connect(DB_NAME)


def create_table():

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL,
        user TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()



def exists(hash_value):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM messages WHERE hash=?",
        (hash_value,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None



def save(hash_value, user):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO messages(hash,user)
        VALUES(?,?)
        """,
        (hash_value, user)
    )

    conn.commit()
    conn.close()