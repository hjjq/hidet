
import json
fh = open('run_configs.json')
run_configs = json.load(fh)
fh.close()
print(run_configs)