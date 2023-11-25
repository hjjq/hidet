import os
import argparse
import numpy as np
import torch
import torchvision
import hidet
from transformers import AutoTokenizer, AutoModelForMaskedLM, logging
os.environ["TOKENIZERS_PARALLELISM"] = "false"
logging.set_verbosity_error()

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

def bench_hf_transformers(model_name, seqlen, dtype):
    setup_hidet_flags(dtype)
    dtype = getattr(torch, dtype)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForMaskedLM.from_pretrained(model_name,
            max_position_embeddings=8192, ignore_mismatched_sizes=True)
    model = model.eval().to(dtype).cuda()
    inputs = tokenizer("Dummy sentence", padding='max_length', max_length=seqlen,
                       return_tensors='pt')
    inputs = {'input_ids': inputs['input_ids']}
    torch_inputs = tuple(i.clone().cuda() for i in inputs.values())
    with torch.no_grad(), torch.autocast("cuda"):
        model = torch.compile(model, backend='hidet')
        latency = bench_torch_model(model, torch_inputs)
        del model
    return latency

parser = argparse.ArgumentParser(prog='Benchmark Transformers')
parser.add_argument(
    'model',
    type=str,
    help='Specify model'
)
parser.add_argument(
    '--params',
    type=str,
    default='seqlen=1024',
    help='Specify Input Parameters. E.g., seqlen=1024'
)
parser.add_argument(
    '--dtype',
    type=str,
    default='float16',
    help='Specify precision. E.g., float32'
)
args = parser.parse_args()

model, dtype = args.model, args.dtype
seqlen = int(args.params.split('=')[1])
latency = bench_hf_transformers(model, seqlen, dtype)
print(latency)