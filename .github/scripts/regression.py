import os
import mysql.connector


# e.g., '1,2,3'
hw_config_ids = os.environ.get('HW_CONFIG')
hw_config_ids = hw_config_ids.split(',')

conn = mysql.connector.connect(
    host=os.environ.get('CI_DB_HOSTNAME'),
    user=os.environ.get('CI_DB_USERNAME'),
    password=os.environ.get('CI_DB_PASSWORD'),
    port=os.environ.get('CI_DB_PORT'),
    database='hidet_ci'
)
cursor = conn.cursor()

for hw_config_id in hw_config_ids:
    query = (
        'SELECT cloud_provider_id, instance_id FROM cloud_instance '
        f'WHERE hardware_config_id = {hw_config_id} LIMIT 1'
    )
    cursor.execute(query)
    if cursor.rowcount == 0:
        raise ValueError(f'Instance with hardware config id {hw_config_id} does not exist.')
    for row in cursor:
        print(row)

cursor.close()
conn.close()