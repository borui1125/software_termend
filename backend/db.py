import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="software_termend",
    user="postgres",
    password="66276005"
)

cursor = conn.cursor()
