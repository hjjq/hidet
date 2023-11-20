import os
import mysql.connector


# e.g., '1,2,3'
hw_config_ids = os.environ.get('HW_CONFIG')

conn = mysql.connector.connect(
    host=os.environ.get('CI_DB_HOSTNAME'),
    user=os.environ.get('CI_DB_USERNAME'),
    password=os.environ.get('CI_DB_PASSWORD'),
    port=os.environ.get('CI_DB_PORT'),
    database='hidet_ci'
)

cursor = conn.cursor()
query = f"SELECT cloud_provider_id, instance_id FROM cloud_instance WHERE hardware_config_id IN ({hw_config_ids})"
cursor.execute(query)

for row in cursor:
    print(row)

cursor.close()
conn.close()