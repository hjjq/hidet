import torch
import hidet

a = hidet.randn([1, 3, 224, 224], dtype='float16', device='cuda')
b = hidet.randn([1, 1, 224, 224], dtype='float16', device='cuda')
c = a + b
print(c)