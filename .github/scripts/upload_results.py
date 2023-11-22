import os
import json
# fh = open('run_configs.json')
# run_configs = json.load(fh)
# fh.close()
# print(run_configs)

sha = os.environ.get('COMMIT_SHA')
commit_time = os.environ.get('COMMIT_TIME')
repo_name = os.environ.get('REPO_NAME')
print(sha)
print(commit_time)
print(repo_name)