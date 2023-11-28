import hidet
import torch

def setup_hidet_flags(dtype):
    use_fp16 = dtype == 'float16'
    hidet.torch.dynamo_config.search_space(2)
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
