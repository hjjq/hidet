import os
import json
# fh = open('run_configs.json')
# run_configs = json.load(fh)
# fh.close()
# print(run_configs)

sha = os.environ.get('COMMIT_SHA')
commit_time = os.environ.get('COMMIT_TIME')
commit_author = os.environ.get('COMMIT_AUTHOR')
repo_name = os.environ.get('REPO_NAME')
hw_configs = os.environ.get('HW_CONFIGS')
print(sha)
print(commit_time)
print(commit_author)
print(repo_name)
print(hw_configs)

hw_configs = json.loads(hw_configs)
for hw_config in  hw_configs:
    artifact_path = f'./run_configs_{hw_config}/run_configs.json'
    fh = open(artifact_path)
    run_configs = json.load(fh)
    fh.close()
    print(run_configs)