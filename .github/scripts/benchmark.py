import os
import torch
import hidet
import json
import mysql.connector
import numpy as np

a = hidet.randn([1, 3, 224, 224], dtype='float16', device='cuda')
b = hidet.randn([1, 1, 224, 224], dtype='float16', device='cuda')
c = a + b
print(c)

fh = open('run_configs.json')
run_configs = json.load(fh)
fh.close()
print(run_configs)
hw_config = os.environ.get('HW_CONFIG')
print('hw:', hw_config)
for run_config in run_configs:
    run_config['hardware_config'] = hw_config
    run_config['latency'] = np.random.randn()
with open('run_configs.json', 'w') as fh:
    json.dump(run_configs, fh)