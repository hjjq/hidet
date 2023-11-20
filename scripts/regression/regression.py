import os


import mysql.connector

conn = mysql.connector.connect(
    host=os.environ.get('CI_DB_HOSTNAME'),
    user=os.environ.get('CI_DB_USERNAME'),
    password=os.environ.get('CI_DB_PASSWORD'),
    port=os.environ.get('CI_DB_PORT'),
    database='hidet_ci'
)

cursor = conn.cursor()
query = "SELECT * FROM hardware_config"
cursor.execute(query)

for row in cursor:
    print(row)

cursor.close()
conn.close()