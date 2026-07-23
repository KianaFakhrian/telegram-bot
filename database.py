import sqlite3


DB_NAME = "messages.db"


def get_connection():
    return sqlite3.connect(DB_NAME)



def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        chat_id INTEGER,

        content_hash TEXT UNIQUE,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()



def is_duplicate(content_hash):

    conn = get_connection()
    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT id 
        FROM messages
        WHERE content_hash = ?
        """,
        (content_hash,)
    )


    result = cursor.fetchone()


    conn.close()


    return result is not None




def save_message_hash(chat_id, content_hash):

    conn = get_connection()
    cursor = conn.cursor()


    try:

        cursor.execute(
            """
            INSERT INTO messages
            (
            chat_id,
            content_hash
            )
            VALUES (?,?)
            """,

            (
                chat_id,
                content_hash
            )

        )


        conn.commit()


    except sqlite3.IntegrityError:

        # اگر قبلا وجود داشته باشد
        pass


    finally:

        conn.close()