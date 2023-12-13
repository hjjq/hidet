import sys
import os
import argparse
import numpy as np
import torch
import hidet
from bench_utils import enable_compile_server, setup_hidet_flags, bench_torch_model

def bench_matmul_f16(params: str, *args, **kwargs) -> float:
    return 0

def bench_batch_matmul(params: str, *args, **kwargs) -> float:
    return 0

def bench_conv2d(params: str, *args, **kwargs) -> float:
    return 0

def bench_conv2d_gemm_f16(params: str, *args, **kwargs) -> float:
    return 0

def bench_attn(params: str, *args, **kwargs) -> float:
    return 0

def bench_attn_mask_add(params: str, *args, **kwargs) -> float:
    return 0

def bench_reduce(params: str, *args, **kwargs) -> float:
    return 0

bench_func_map = {
    'matmul_f16': bench_matmul_f16,
    'batch_matmul': bench_batch_matmul,
    'conv2d': bench_conv2d,
    'conv2d_gemm_f16': bench_conv2d_gemm_f16,
    'attn': bench_attn,
    'attn_mask_add': bench_attn_mask_add,
    'reduce': bench_reduce,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='Benchmark Operators')
    parser.add_argument(
        'operator',
        type=str,
        help='Specify operator. E.g., matmul_f16'
    )
    parser.add_argument(
        '--params',
        type=str,
        help='Specify Input Parameters. Different operators have different formats.'
    )
    parser.add_argument(
        '--dtype',
        type=str,
        default='float16',
        help='Specify precision. E.g., float32'
    )
    args = parser.parse_args()

    operator, dtype = args.operator, args.dtype
    params = args.params
    if operator in bench_func_map:
        bench_func = bench_func_map[operator]
    else:
        raise ValueError(f'Benchmark function for operator {operator} not implemented')

    setup_hidet_flags(dtype)
    enable_compile_server(True)
    latency = bench_func(params, dtype)
    print(latency)