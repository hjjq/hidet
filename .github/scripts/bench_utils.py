import os
import mysql.connector
import hidet
import torch

def get_db_conn():
    conn = mysql.connector.connect(
        host=os.environ.get('CI_DB_HOSTNAME'),
        user=os.environ.get('CI_DB_USERNAME'),
        password=os.environ.get('CI_DB_PASSWORD'),
        port=os.environ.get('CI_DB_PORT'),
        database='hidet_ci'
    )
    return conn

def setup_hidet_flags(dtype):
    use_fp16 = dtype == 'float16'
    hidet.torch.dynamo_config.search_space(0)
    hidet.torch.dynamo_config.use_fp16(use_fp16)
    hidet.torch.dynamo_config.use_fp16_reduction(use_fp16)
    hidet.torch.dynamo_config.use_attention(True)
    hidet.torch.dynamo_config.use_tensor_core(True)
    hidet.torch.dynamo_config.use_cuda_graph(True)
    hidet.option.cache_dir(hidet.option.get_cache_dir() + '/regression')

def bench_torch_model(model, torch_inputs, bench_iters=100, warmup_iters=10):
    for _ in range(warmup_iters):
        torch_out = model(*torch_inputs)
    torch.cuda.empty_cache()

    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    torch.cuda.synchronize()
    start.record()
    for _ in range(bench_iters):
        torch_out = model(*torch_inputs)
    end.record()
    end.synchronize()
    torch.cuda.empty_cache()

    latency = start.elapsed_time(end) / bench_iters
    return latency

def enable_compile_server(enable=True):
    hidet.option.compile_server.addr(os.environ.get('CI_CS_HOSTNAME'))
    hidet.option.compile_server.port(int(os.environ.get('CI_CS_PORT')))
    hidet.option.compile_server.username(os.environ.get('CI_CS_USERNAME'))
    hidet.option.compile_server.password(os.environ.get('CI_CS_PASSWORD'))
    hidet.option.compile_server.repo(os.environ.get('REPO_NAME'), os.environ.get('REPO_BRANCH'))
    hidet.option.compile_server.enable(flag=enable)