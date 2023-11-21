import os
import time
import subprocess

instances = os.environ.get('STARTED_INSTANCES').replace(' ', '')
instances = [s for s in instances.split(';') if s]
# Stop all instances
for instance in instances:
    ids = [s for s in instance.split(',') if s]
    cloud_provider_id = int(ids[0])
    instance_id = ids[1]
    if cloud_provider_id == 1: # AWS
        cmd = ['aws', 'ec2', 'stop-instances', '--instance-ids', instance_id]
    else:
        raise ValueError(f'Unknown cloud provider id: {cloud_provider_id}')
    print("Running command: " + " ".join(cmd))
    output = subprocess.run(cmd, capture_output=True, text=True)
    print(output.stdout)
    print(output.stderr)
    if output.returncode != 0:
        raise RuntimeError(f'Failed to stop instance {instance_id} on cloud provider {cloud_provider_id}.')
