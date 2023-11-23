import argparse
import numpy as np

parser = argparse.ArgumentParser(prog='Benchmark Transformers')
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

print(np.random.random() * 10)