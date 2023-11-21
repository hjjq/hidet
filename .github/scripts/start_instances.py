import os
import time
import subprocess
import mysql.connector

def run_command(cmd):
    print("Running command: " + " ".join(cmd))
    output = subprocess.run(cmd, capture_output=True, text=True)
    print(output.stdout)
    print(output.stderr)
    return output

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

instances = []
# Fetch list of (cloud_provider_id, instance_id) tuples from DB
for hw_config_id in hw_config_ids:
    query = (
        'SELECT cloud_provider_id, instance_id FROM cloud_instance '
        f'WHERE hardware_config_id = {hw_config_id} LIMIT 1'
    )
    cursor.execute(query)
    rows = cursor.fetchall()
    if len(rows) == 0:
        raise ValueError(f'Instance with hardware config id {hw_config_id} does not exist.')
    instances.append(rows[0])

# Close DB connection
cursor.close()
conn.close()

# # Launch all instances
# for instance in instances:
#     cloud_provider_id, instance_id = instance
#     if cloud_provider_id == 1: # AWS
#         cmd = ['aws', 'ec2', 'start-instances', '--instance-ids', instance_id]
#     else:
#         raise ValueError(f'Unknown cloud provider id: {cloud_provider_id}')
#     output = run_command(cmd)
#     if output.returncode != 0:
#         raise RuntimeError(f'Failed to start instance {instance_id} on cloud provider {cloud_provider_id}.')

# # Wait until all instances are running
# for instance in instances:
#     cloud_provider_id, instance_id = instance
#     started = False
#     while not started:
#         time.sleep(5)
#         if cloud_provider_id == 1: # AWS
#             cmd = ['aws', 'ec2', 'describe-instance-status', '--instance-ids', instance_id]
#             output = run_command(cmd)
#             if output.returncode != 0:
#                 raise RuntimeError(f'Failed to check status for {instance_id} on cloud provider {cloud_provider_id}.')
#             if output.stdout.count('ok') >= 2:
#                 started = True
#         else:
#             raise ValueError(f'Unknown cloud provider id: {cloud_provider_id}')

# Set output for github action
# e.g., "1,aws-instance0;1,aws-instance1;2,gcp-instance0" representing two AWS instances and one GCP instance
instances_str = ''
for instance in instances:
    cloud_provider_id, instance_id = instance
    instances_str += cloud_provider_id + ',' + instance_id + ';'
cmd = ['echo', f'"started_instances={instances_str}"', '>>', '"$GITHUB_OUTPUT"']
run_command(cmd)
