import os
import json
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

def get_bench_cmd(run_type, run_id, run_name, run_param_id, run_param_name):
    cmd = ['python']
    if run_name in ['bert-base-uncased', 'other models that share same interface']:
        pass
    elif run_name in ['another group of models/operators']:
        pass

    return cmd

run_type, run_id, run_name, run_param_id, run_param_name = 'model', 1, 'bert-base-uncased', 1, 'seqlen=256'

cmd = get_bench_cmd(run_type, run_id, run_name, run_param_id, run_param_name)
