<<<<<<< HEAD
import os
import psycopg2


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "software_termend"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "資料庫密碼"), 
    )
=======
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="software_termend",
    user="postgres",
    password="66276005"
)

cursor = conn.cursor()
>>>>>>> 2cf90c0b7b25864b6cecedc957116561f940a1dc
