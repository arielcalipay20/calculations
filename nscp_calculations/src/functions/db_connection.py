import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# ---- Database Connection ----
def get_db_connection():
    conn = mysql.connector.connect(
        host=os.getenv("HOST"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        database=os.getenv("DATABASE")
    )
    return conn