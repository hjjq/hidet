import os
import json
import mysql.connector

# Get environment variables
commit_sha = os.environ.get('COMMIT_SHA')
commit_time = os.environ.get('COMMIT_TIME')
commit_author = os.environ.get('COMMIT_AUTHOR')
repo_name = os.environ.get('REPO_NAME')
hw_configs = os.environ.get('HW_CONFIGS')
commit_url = f'https://github.com/{repo_name}/commit/{commit_sha}'

# Insert commit into DB
conn = mysql.connector.connect(
    host=os.environ.get('CI_DB_HOSTNAME'),
    user=os.environ.get('CI_DB_USERNAME'),
    password=os.environ.get('CI_DB_PASSWORD'),
    port=os.environ.get('CI_DB_PORT'),
    database='hidet_ci'
)
cursor = conn.cursor()

query = (
    'INSERT INTO commit (hash, url, author, time, status) VALUES (%s, %s, %s, %s, %s)'
)
val = (commit_sha[:7], commit_url, commit_author, commit_time, 'pass')
cursor.execute(query, val)
conn.commit()

query = ('SELECT LAST_INSERT_ID()')
cursor.execute(query)
commit_id = cursor.fetchall()[0][0]

# Create a mapping of HW config name to HW config ID
query = (
    'SELECT id, name FROM hardware_config'
)
cursor.execute(query)
hw_config_table = cursor.fetchall()
hw_config_map = {}
for hw_config in hw_config_table:
    hw_config_map[hw_config[1]] = int(hw_config[0])

# Insert results into table
hw_configs = json.loads(hw_configs)
for hw_config in  hw_configs:
    artifact_path = f'./run_configs_{hw_config}/run_configs.json'
    fh = open(artifact_path)
    run_configs = json.load(fh)
    fh.close()
    for run_config in run_configs:
        run_type = run_config['type']
        run_id = run_config['id']
        run_param_id = run_config['param_id']
        run_hw_config = run_config['hardware_config'] # Should be same as `hw_config`
        run_latency = run_config['latency']
        run_hw_config_id = hw_config_map[run_hw_config]
        query = (
            f'INSERT INTO {run_type}_result (commit_id, {run_type}_id, input_parameter_id, hardware_config_id, '
            f'dtype_id, latency) VALUES (%s, %s, %s, %s, %s, %s)'
        )
        val = (commit_id, run_id, run_param_id, run_hw_config_id, 1, run_latency)
        cursor.execute(query, val)
        val = (commit_id, run_id, run_param_id, run_hw_config_id, 2, run_latency * 2)
        cursor.execute(query, val)
        conn.commit()