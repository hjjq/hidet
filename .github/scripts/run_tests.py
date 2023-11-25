import os
import json
import subprocess
import mysql.connector
import numpy as np

# fh = open('run_configs.json')
# run_configs = json.load(fh)
# fh.close()
# print(run_configs)
# hw_config = os.environ.get('HW_CONFIG')
# print('hw:', hw_config)
# for run_config in run_configs:
#     # Append hardware_config column
#     run_config['hardware_config'] = hw_config
#     # Extract configurations
#     run_type = run_config['type']
#     run_id = run_config['id']
#     run_name = run_config['name']
#     run_param_id = run_config['param_id']
#     run_param_name = run_config['param_name']
#     run_config['latency'] = np.random.random() * 10
# with open('run_configs.json', 'w') as fh:
#     json.dump(run_configs, fh)

def run_command(cmd):
    print("Running command: " + " ".join(cmd))
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    outputs = []
    for line in popen.stdout:
        print(line, end='')
        outputs.append(line)
    popen.stdout.close()
    ret = popen.wait()
    if ret:
        raise RuntimeError(f'Command {cmd} failed with return code {ret}.')
    return outputs

def get_bench_cmd(run_type, run_id, run_name, run_param_id, run_param_name, dtype):
    # Get the name of the benchmark script from DB
    conn = mysql.connector.connect(
        host=os.environ.get('CI_DB_HOSTNAME'),
        user=os.environ.get('CI_DB_USERNAME'),
        password=os.environ.get('CI_DB_PASSWORD'),
        port=os.environ.get('CI_DB_PORT'),
        database='hidet_ci'
    )
    cursor = conn.cursor()
    query = f'SELECT runfile FROM {run_type} WHERE id = {run_id}'
    cursor.execute(query)
    runfile = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    cmd = ['python', runfile, run_name, '--params', run_param_name, '--dtype', dtype]
    return cmd

run_type, run_id, run_name, run_param_id, run_param_name = 'model', 1, 'bert-base-uncased', 1, 'seqlen=256'
dtype = 'float16'
cmd = get_bench_cmd(run_type, run_id, run_name, run_param_id, run_param_name, dtype)
outputs = run_command(cmd)
latency = float(outputs[-1].split('\n')[0]) # Get last line
print(f'Latency = {latency}')
