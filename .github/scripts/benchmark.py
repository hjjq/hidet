import torch
import hidet
import json
import mysql.connector

a = hidet.randn([1, 3, 224, 224], dtype='float16', device='cuda')
b = hidet.randn([1, 1, 224, 224], dtype='float16', device='cuda')
c = a + b
print(c)

fh = open('run_configs.json')
run_configs = json.load(fh)
fh.close()
print(run_configs)