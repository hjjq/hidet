import os
import time
import subprocess



started_instances = os.environ.get('STARTED_INSTANCES')
instances = started_instances.split(';')

# Stop all instances
for instance in instances:
    cloud_provider_id, instance_id = instance.split(',')
    cloud_provider_id = int(cloud_provider_id)
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
