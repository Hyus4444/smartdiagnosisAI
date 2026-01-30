import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    user="admin",
    password="Admin12345678"
    ,
    dbname="smartdiagnosis_db"
)

print("OK")
conn.close()

