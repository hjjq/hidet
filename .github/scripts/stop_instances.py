import os
import time
import subprocess



started_instances = os.environ.get('STARTED_INSTANCES')
print(started_instances)

# # Launch all instances
# for instance in instances:
#     cloud_provider_id, instance_id = instance
#     if cloud_provider_id == 1: # AWS
#         cmd = ['aws', 'ec2', 'start-instances', '--instance-ids', instance_id]
#     else:
#         raise ValueError(f'Unknown cloud provider id: {cloud_provider_id}')
#     print("Running command: " + " ".join(cmd))
#     output = subprocess.run(cmd, capture_output=True, text=True)
#     print(output.stdout)
#     print(output.stderr)
#     if output.returncode != 0:
#         raise RuntimeError(f'Failed to start instance {instance_id} on cloud provider {cloud_provider_id}.')

# # Wait until all instances are running
# for instance in instances:
#     cloud_provider_id, instance_id = instance
#     started = False
#     while not started:
#         time.sleep(5)
#         if cloud_provider_id == 1: # AWS
#             cmd = ['aws', 'ec2', 'describe-instance-status', '--instance-ids', instance_id]
#             print("Running command: " + " ".join(cmd))
#             output = subprocess.run(cmd, capture_output=True, text=True)
#             print(output.stdout)
#             print(output.stderr)
#             if output.returncode != 0:
#                 raise RuntimeError(f'Failed to check status for {instance_id} on cloud provider {cloud_provider_id}.')
#             if output.stdout.count('ok') >= 2:
#                 started = True
#         else:
#             raise ValueError(f'Unknown cloud provider id: {cloud_provider_id}')
    
