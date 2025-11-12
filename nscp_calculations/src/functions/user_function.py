import mysql.connector
from src.functions.db_connection import get_db_connection
from src.functions.hash_password import hash_password

# ---- User Functions ----
def register_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                       (username, hash_password(password)))
        conn.commit()
        return True
    except mysql.connector.IntegrityError:
        return False
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",
                   (username, hash_password(password)))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user is not None